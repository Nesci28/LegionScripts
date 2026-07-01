try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass

# API is injected by TazUO at runtime; the import above is IDE-only.
import datetime
import importlib
import json
import math
import os
import re
import time
import traceback

from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump

importlib.reload(Gump)
from Gump import Gump


class RailCreator:
    WIDTH = 900
    HEIGHT = 650

    ROUTES_DIR = LegionPath.createPath("Data/Rails")
    ROUTE_FILE_VERSION = 1
    POINT_LIST_SIZE = 9
    ROUTE_LIST_SIZE = 7
    MAX_VISUAL_POINTS = 110
    VISUAL_REFRESH_POINTS = 10
    VISUAL_REFRESH_SECONDS = 1.0
    PATHFIND_TIMEOUT_SECONDS = 10.0

    def __init__(self):
        self._running = True
        self.gump = None
        self.routeNameInput = None
        self.statLabels = {}
        self.pointLabels = []
        self._needsRedraw = False
        self._captureNameOnRedraw = True
        self._redrawing = False
        self._statusText = "Ready."
        self._statusHue = None

        self.routes = []
        self.routeName = self._default_route_name()
        self.routePath = None
        self.points = []
        self.createdAt = None
        self.dirty = False

        self.recording = False
        self.lastRecordedPoint = None
        self._lastVisualPointCount = 0
        self._lastVisualRefreshAt = 0

        self.playing = False
        self.playbackIndex = 0
        self.playbackTarget = None
        self.playbackDeadline = 0

    # ------------------------------
    # Script lifecycle
    # ------------------------------
    def main(self):
        try:
            self._ensure_routes_dir()
            self._load_route_index()
            self._show_gump()
        except Exception as e:
            API.SysMsg("RailCreator e: {}".format(e), 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def run(self):
        while self._isRunning():
            if not self.tick():
                return
            self._process_recording()
            self._process_playback()
            API.Pause(0.05)

    def tick(self):
        if not self._running:
            return False

        if self.gump:
            self.gump.tick()
            if not self.gump:
                return False
            self.gump.tickSubGumps()
            try:
                if self.gump.gump.IsDisposed and not self._redrawing:
                    self._onClose()
                    return False
            except Exception:
                pass

        if self._needsRedraw and self._running:
            self._redraw_gump()

        return self._running

    def _isRunning(self):
        return self._running

    def _onClose(self):
        if not self._running:
            return

        self._running = False
        self.recording = False
        self._stop_playback(cancelPath=True, status=False)

        if self.gump:
            try:
                for subGump in self.gump.subGumps:
                    subGump.destroy()
                self.gump.destroy()
            except Exception:
                pass
            self.gump = None

        API.Stop()

    # ------------------------------
    # Recording and playback
    # ------------------------------
    def _start_recording(self):
        self._capture_route_name()
        if self.playing:
            self._stop_playback(cancelPath=True, status=False)

        current = self._current_point()
        if not self.points:
            self._append_point(current)
        self.lastRecordedPoint = self._point_key(self.points[-1])
        self.recording = True
        self._set_status("Recording every X/Y/Z change.")
        self._request_redraw()

    def _stop_recording(self):
        self.recording = False
        self.lastRecordedPoint = None
        self._set_status("Recording stopped. {} points captured.".format(len(self.points)))
        self._request_redraw()

    def _process_recording(self):
        if not self.recording or self.playing:
            return

        current = self._current_point()
        key = self._point_key(current)
        if key == self.lastRecordedPoint:
            return

        self._append_point(current)
        self.lastRecordedPoint = key
        self._set_status("Recording... {} points captured.".format(len(self.points)))
        self._update_dynamic_labels()

        now = time.time()
        if (
            len(self.points) - self._lastVisualPointCount >= self.VISUAL_REFRESH_POINTS
            or now - self._lastVisualRefreshAt >= self.VISUAL_REFRESH_SECONDS
        ):
            self._request_redraw()

    def _start_playback(self):
        self._capture_route_name()
        if not self.points:
            self._set_status("No points to play.", 33)
            return

        if self.recording:
            self.recording = False

        self.playing = True
        self.playbackIndex = 0
        self.playbackTarget = None
        self.playbackDeadline = 0
        self._set_status("Playback started.")
        self._request_redraw()

    def _process_playback(self):
        if not self.playing:
            return

        if self.playbackIndex >= len(self.points):
            self._stop_playback(cancelPath=False, status=False)
            self._set_status("Playback complete. {} points visited.".format(len(self.points)))
            self._request_redraw()
            return

        point = self.points[self.playbackIndex]

        if self._at_point(point):
            self.playbackIndex += 1
            self.playbackTarget = None
            self._set_status("Playback {}/{}.".format(self.playbackIndex, len(self.points)))
            self._update_dynamic_labels()
            if self.playbackIndex % self.VISUAL_REFRESH_POINTS == 0:
                self._request_redraw()
            return

        if self.playbackTarget is None:
            self.playbackTarget = point
            self.playbackDeadline = time.time() + self.PATHFIND_TIMEOUT_SECONDS
            try:
                result = API.Pathfind(
                    int(point["x"]),
                    int(point["y"]),
                    int(point["z"]),
                    0,
                    False,
                    int(self.PATHFIND_TIMEOUT_SECONDS),
                )
                if result is False:
                    self._fail_playback(point, "Pathfind failed to start")
            except Exception as e:
                self._fail_playback(point, "Pathfind error: {}".format(e))
            return

        if time.time() > self.playbackDeadline:
            self._fail_playback(point, "Pathfind timed out")

    def _fail_playback(self, point, reason):
        index = self.playbackIndex + 1
        self._stop_playback(cancelPath=True, status=False)
        self._set_status(
            "{} at point {} ({}, {}, {}).".format(
                reason,
                index,
                point["x"],
                point["y"],
                point["z"],
            ),
            33,
        )
        self._request_redraw()

    def _stop_playback(self, cancelPath=True, status=True):
        wasPlaying = self.playing
        self.playing = False
        self.playbackTarget = None
        self.playbackDeadline = 0

        if cancelPath:
            try:
                API.CancelPathfinding()
            except Exception:
                pass

        if status and wasPlaying:
            self._set_status("Playback stopped.")
            self._request_redraw()

    # ------------------------------
    # Route data
    # ------------------------------
    def _append_point(self, point):
        if self.points and self._point_key(self.points[-1]) == self._point_key(point):
            return

        self.points.append(point)
        self.dirty = True
        self._lastVisualRefreshAt = 0
        if not self.createdAt:
            self.createdAt = self._now_iso()

    def _clear_points(self):
        self.points = []
        self.dirty = True
        self.lastRecordedPoint = None
        self.playbackIndex = 0
        self.playbackTarget = None
        self._set_status("Route cleared.")
        self._request_redraw()

    def _new_route(self):
        self.recording = False
        self._stop_playback(cancelPath=True, status=False)
        self.routeName = self._default_route_name()
        self.routePath = None
        self.points = []
        self.createdAt = None
        self.dirty = False
        self.lastRecordedPoint = None
        self.playbackIndex = 0
        self._set_status("New route ready.")
        self._request_redraw(captureName=False)

    def _save_route(self):
        self._capture_route_name()
        self._ensure_routes_dir()

        if not self.routeName:
            self.routeName = self._default_route_name()

        path = self._route_path_for_name(self.routeName)
        now = self._now_iso()
        data = {
            "version": self.ROUTE_FILE_VERSION,
            "name": self.routeName,
            "createdAt": self.createdAt or now,
            "updatedAt": now,
            "points": self.points,
        }

        with open(path, "w") as routeFile:
            json.dump(data, routeFile, indent=2, sort_keys=True)

        self.routePath = path
        self.createdAt = data["createdAt"]
        self.dirty = False
        self._load_route_index()
        self._set_status("Saved {} points to {}.".format(len(self.points), os.path.basename(path)))
        self._request_redraw()

    def _delete_route(self):
        self._capture_route_name()
        path = self.routePath
        if not path:
            path = self._route_path_for_name(self.routeName)

        if path and os.path.exists(path):
            os.remove(path)
            self._set_status("Deleted {}.".format(os.path.basename(path)))
        else:
            self._set_status("No saved route file to delete.", 33)

        self.routePath = None
        self.dirty = True
        self._load_route_index()
        self._request_redraw()

    def _load_route(self, path):
        self.recording = False
        self._stop_playback(cancelPath=True, status=False)

        data = self._read_route_file(path)
        self.routeName = data["name"]
        self.routePath = path
        self.points = data["points"]
        self.createdAt = data.get("createdAt")
        self.dirty = False
        self.lastRecordedPoint = self._point_key(self.points[-1]) if self.points else None
        self.playbackIndex = 0
        self.playbackTarget = None
        self._set_status("Loaded {} points from {}.".format(len(self.points), os.path.basename(path)))
        self._request_redraw(captureName=False)

    def _read_route_file(self, path):
        with open(path, "r") as routeFile:
            data = json.load(routeFile)

        if not isinstance(data, dict):
            raise Exception("Route file is not a JSON object.")

        name = str(data.get("name") or os.path.splitext(os.path.basename(path))[0]).strip()
        rawPoints = data.get("points", [])
        if not isinstance(rawPoints, list):
            raise Exception("Route points must be a list.")

        points = []
        for rawPoint in rawPoints:
            if not isinstance(rawPoint, dict):
                continue
            points.append(
                {
                    "x": int(rawPoint.get("x")),
                    "y": int(rawPoint.get("y")),
                    "z": int(rawPoint.get("z")),
                }
            )

        return {
            "name": name or self._default_route_name(),
            "createdAt": data.get("createdAt"),
            "updatedAt": data.get("updatedAt"),
            "points": points,
        }

    def _load_route_index(self):
        self._ensure_routes_dir()
        routes = []
        for fileName in os.listdir(self.ROUTES_DIR):
            if not fileName.lower().endswith(".json"):
                continue
            path = os.path.join(self.ROUTES_DIR, fileName)
            try:
                data = self._read_route_file(path)
                routes.append(
                    {
                        "name": data["name"],
                        "path": path,
                        "count": len(data["points"]),
                        "updatedAt": data.get("updatedAt") or "",
                    }
                )
            except Exception:
                pass

        routes.sort(key=lambda route: (route["name"].lower(), route["path"].lower()))
        self.routes = routes

    # ------------------------------
    # Gump
    # ------------------------------
    def _show_gump(self):
        g = Gump(self.WIDTH, self.HEIGHT, self._onClose)
        self.gump = g
        self.statLabels = {}
        self.pointLabels = []

        g.addTitle("RAIL CREATOR", 8)

        routesPanel = g.addPanel(14, 48, 280, 420, "Rails")
        mapPanel = g.addPanel(302, 48, 584, 420, "Route Visualizer")
        pointsPanel = g.addPanel(14, 476, 872, 130, "Recorded Points")

        self._draw_routes_panel(routesPanel)
        self._draw_visualizer(mapPanel)
        self._draw_points_panel(pointsPanel)

        g.create()
        self._lastVisualPointCount = len(self.points)
        self._lastVisualRefreshAt = time.time()
        self._set_status(self._statusText, self._statusHue)
        self._update_dynamic_labels()

    def _draw_routes_panel(self, panel):
        x = panel["x"]
        y = panel["y"]
        width = panel["width"]

        self.gump.addLabel("Name", x + 4, y + 3, Gump.hues["muted"])
        self.routeNameInput = self._add_textbox(self.routeName, x + 48, y, width - 54, 24)

        buttonY = y + 34
        self._button("New", x + 4, buttonY, 58, self._new_route)
        self._button("Save", x + 68, buttonY, 58, self._save_route)
        self._button("Delete", x + 132, buttonY, 68, self._delete_route)
        self._button("Clear", x + 206, buttonY, 58, self._clear_points)

        buttonY += 34
        recordLabel = "Stop Rec" if self.recording else "Record"
        recordAction = self._stop_recording if self.recording else self._start_recording
        playLabel = "Stop Play" if self.playing else "Play"
        playAction = self._stop_playback if self.playing else self._start_playback
        self._button(recordLabel, x + 4, buttonY, 88, recordAction)
        self._button(playLabel, x + 98, buttonY, 88, playAction)
        self._button("Reload", x + 192, buttonY, 72, self._reload_routes)

        statsY = buttonY + 36
        self.statLabels["points"] = self.gump.addLabel("", x + 4, statsY, Gump.hues["text"])
        self.statLabels["state"] = self.gump.addLabel("", x + 4, statsY + 18, Gump.hues["text"])
        self.statLabels["position"] = self.gump.addLabel("", x + 4, statsY + 36, Gump.hues["muted"])
        self.statLabels["file"] = self.gump.addLabel("", x + 4, statsY + 54, Gump.hues["muted"])

        self.gump.addDivider(x + 4, statsY + 79, width - 8, 0.6)
        self.gump.addLabel("Saved Rails", x + 4, statsY + 86, Gump.hues["text"])

        listY = statsY + 108
        visibleRoutes = self.routes[: self.ROUTE_LIST_SIZE]
        if not visibleRoutes:
            self.gump.addLabel("No saved rails yet.", x + 4, listY + 4, Gump.hues["muted"])
            return

        for index, route in enumerate(visibleRoutes):
            rowY = listY + index * 28
            selected = bool(self.routePath and os.path.abspath(route["path"]) == os.path.abspath(self.routePath))
            self.gump.addFlatRow(x + 2, rowY - 2, width - 4, 26, selected)
            self._button("Load", x + 6, rowY, 48, lambda path=route["path"]: self._load_route(path), height=21)
            label = "{} ({})".format(route["name"], route["count"])
            self.gump.addLabel(self._truncate(label, 27), x + 60, rowY + 3, Gump.hues["text"])

    def _draw_points_panel(self, panel):
        x = panel["x"]
        y = panel["y"]
        width = panel["width"]

        self.gump.addLabel("Recent captured coordinates", x + 4, y + 2, Gump.hues["muted"])
        self.gump.addLabel("Unsaved changes" if self.dirty else "Saved", x + width - 112, y + 2, Gump.hues["text"])

        start = max(0, len(self.points) - self.POINT_LIST_SIZE)
        colWidth = int((width - 8) / 3)
        for row in range(self.POINT_LIST_SIZE):
            pointIndex = start + row
            col = row // 3
            slot = row % 3
            rowX = x + 4 + col * colWidth
            rowY = y + 26 + slot * 26
            self.gump.addFlatRow(rowX, rowY - 2, colWidth - 6, 24, False)
            label = self.gump.addLabel("", rowX + 6, rowY + 2, Gump.hues["text"])
            self.pointLabels.append({"label": label, "index": pointIndex})

    def _draw_visualizer(self, panel):
        x = panel["x"]
        y = panel["y"]
        width = panel["width"]
        height = panel["height"]

        grid = self.gump.addChartGrid(x + 2, y + 2, width - 4, height - 4)
        routeX = grid["x"]
        routeY = grid["y"]
        routeWidth = grid["width"]
        routeHeight = grid["height"]

        if not self.points:
            self.gump.addLabel("No route recorded.", routeX + 12, routeY + 12, Gump.hues["muted"])
            self.gump.addLabel("Press Record and move your character.", routeX + 12, routeY + 32, Gump.hues["muted"])
            return

        bounds = self._route_bounds(self.points)
        visualPoints = self._sample_points(self.points, self.MAX_VISUAL_POINTS)
        scaled = [self._scale_point(point, bounds, routeX, routeY, routeWidth, routeHeight) for point in visualPoints]

        for index in range(1, len(scaled)):
            self._draw_segment(scaled[index - 1], scaled[index], "#7ecf57")

        for point, screenPoint in zip(visualPoints, scaled):
            self._draw_marker(screenPoint[0], screenPoint[1], "#7ecf57", 4)

        startPoint = self._scale_point(self.points[0], bounds, routeX, routeY, routeWidth, routeHeight)
        endPoint = self._scale_point(self.points[-1], bounds, routeX, routeY, routeWidth, routeHeight)
        self._draw_marker(startPoint[0], startPoint[1], "#ffd74a", 8)
        self._draw_marker(endPoint[0], endPoint[1], "#4fd3ff", 8)

        if self.playing and self.playbackIndex < len(self.points):
            activePoint = self._scale_point(self.points[self.playbackIndex], bounds, routeX, routeY, routeWidth, routeHeight)
            self._draw_marker(activePoint[0], activePoint[1], "#ffffff", 10)

        current = self._current_point()
        if self._point_in_bounds(current, bounds):
            playerPoint = self._scale_point(current, bounds, routeX, routeY, routeWidth, routeHeight)
            self._draw_marker(playerPoint[0], playerPoint[1], "#ff7b42", 7)

        self.gump.addLabel("Start", startPoint[0] + 7, startPoint[1] - 10, Gump.hues["text"])
        self.gump.addLabel("End", endPoint[0] + 7, endPoint[1] - 10, Gump.hues["text"])

    def _button(self, text, x, y, width, callback, height=24):
        return self.gump.addTextButton(
            text,
            x,
            y,
            width,
            height,
            self.gump.onClick(lambda: self._safe_action(callback)),
            10,
        )

    def _safe_action(self, callback):
        try:
            callback()
        except Exception as e:
            self._set_status("Error: {}".format(e), 33)
            try:
                API.SysMsg(traceback.format_exc(), 33)
            except Exception:
                pass

    def _add_textbox(self, text, x, y, width, height):
        self.gump.addColorBox(x - 2, y - 2, height + 4, width + 4, Gump.theme["buttonFrame"], 1)
        self.gump.addColorBox(x - 1, y - 1, height + 2, width + 2, Gump.theme["inputFill"], 1)
        box = API.CreateGumpTextBox(str(text or ""), width, height, False)
        box.SetX(x)
        box.SetY(y)
        self.gump.gump.Add(box)
        return box

    def _redraw_gump(self):
        self._needsRedraw = False
        if self._captureNameOnRedraw:
            self._capture_route_name()
        self._captureNameOnRedraw = True
        if self.gump:
            try:
                self._redrawing = True
                self.gump.gump.Dispose()
            except Exception:
                pass
            finally:
                self._redrawing = False
                self.gump = None

        self._show_gump()

    def _request_redraw(self, captureName=True):
        if self._needsRedraw:
            self._captureNameOnRedraw = self._captureNameOnRedraw and captureName
        else:
            self._captureNameOnRedraw = captureName
        self._needsRedraw = True

    def _reload_routes(self):
        self._capture_route_name()
        self._load_route_index()
        self._set_status("Route list reloaded.")
        self._request_redraw()

    def _update_dynamic_labels(self):
        self._set_label(
            self.statLabels.get("points"),
            "Points: {}{}".format(len(self.points), " *" if self.dirty else ""),
        )
        state = "Recording" if self.recording else "Playing" if self.playing else "Idle"
        self._set_label(self.statLabels.get("state"), "State: {}".format(state))
        current = self._current_point()
        self._set_label(
            self.statLabels.get("position"),
            "Position: {}, {}, {}".format(current["x"], current["y"], current["z"]),
        )
        fileName = os.path.basename(self.routePath) if self.routePath else "Not saved"
        self._set_label(self.statLabels.get("file"), "File: {}".format(self._truncate(fileName, 28)))

        start = max(0, len(self.points) - self.POINT_LIST_SIZE)
        for row, item in enumerate(self.pointLabels):
            pointIndex = start + row
            item["index"] = pointIndex
            if pointIndex >= len(self.points):
                self._set_label(item["label"], "")
                continue
            point = self.points[pointIndex]
            text = "{}. {}, {}, {}".format(pointIndex + 1, point["x"], point["y"], point["z"])
            self._set_label(item["label"], text)

    def _set_status(self, text, hue=None):
        self._statusText = str(text)
        self._statusHue = hue
        if self.gump:
            self.gump.setStatus(self._statusText, hue)

    def _set_label(self, label, text):
        if not label:
            return
        try:
            label.Text = str(text)
        except Exception:
            try:
                label.SetText(str(text))
            except Exception:
                pass

    # ------------------------------
    # Visual helpers
    # ------------------------------
    def _route_bounds(self, points):
        minX = min(point["x"] for point in points)
        maxX = max(point["x"] for point in points)
        minY = min(point["y"] for point in points)
        maxY = max(point["y"] for point in points)

        if minX == maxX:
            minX -= 1
            maxX += 1
        if minY == maxY:
            minY -= 1
            maxY += 1

        padX = max(1, int((maxX - minX) * 0.08))
        padY = max(1, int((maxY - minY) * 0.08))
        return {
            "minX": minX - padX,
            "maxX": maxX + padX,
            "minY": minY - padY,
            "maxY": maxY + padY,
        }

    def _sample_points(self, points, maxCount):
        if len(points) <= maxCount:
            return points[:]

        sampled = []
        lastIndex = len(points) - 1
        for index in range(maxCount):
            sourceIndex = int(round(index * lastIndex / float(maxCount - 1)))
            sampled.append(points[sourceIndex])
        return sampled

    def _scale_point(self, point, bounds, x, y, width, height):
        routeWidth = max(1, bounds["maxX"] - bounds["minX"])
        routeHeight = max(1, bounds["maxY"] - bounds["minY"])
        px = x + int((point["x"] - bounds["minX"]) * (width - 1) / float(routeWidth))
        py = y + int((point["y"] - bounds["minY"]) * (height - 1) / float(routeHeight))
        return px, py

    def _point_in_bounds(self, point, bounds):
        return (
            bounds["minX"] <= point["x"] <= bounds["maxX"]
            and bounds["minY"] <= point["y"] <= bounds["maxY"]
        )

    def _draw_segment(self, first, second, color):
        dx = second[0] - first[0]
        dy = second[1] - first[1]
        steps = max(abs(dx), abs(dy), 1)
        stride = max(1, int(math.ceil(steps / 9.0)))
        for step in range(0, steps + 1, stride):
            px = first[0] + int(dx * step / float(steps))
            py = first[1] + int(dy * step / float(steps))
            self.gump.addColorBox(px - 1, py - 1, 3, 3, color, 0.9)

    def _draw_marker(self, x, y, color, size):
        half = int(size / 2)
        self.gump.addColorBox(x - half, y - half, size, size, "#030201", 0.95)
        self.gump.addColorBox(x - half + 1, y - half + 1, max(1, size - 2), max(1, size - 2), color, 0.96)

    # ------------------------------
    # Utilities
    # ------------------------------
    def _current_point(self):
        return {
            "x": int(API.Player.X),
            "y": int(API.Player.Y),
            "z": int(API.Player.Z),
        }

    def _point_key(self, point):
        return int(point["x"]), int(point["y"]), int(point["z"])

    def _at_point(self, point):
        current = self._current_point()
        return self._point_key(current) == self._point_key(point)

    def _capture_route_name(self):
        if not self.routeNameInput:
            return

        try:
            value = str(self.routeNameInput.Text or "").strip()
        except Exception:
            value = ""

        if value:
            self.routeName = value

    def _ensure_routes_dir(self):
        if not os.path.isdir(self.ROUTES_DIR):
            os.makedirs(self.ROUTES_DIR)

    def _route_path_for_name(self, name):
        cleanName = self._sanitize_file_name(name or self._default_route_name())
        return os.path.join(self.ROUTES_DIR, "{}.json".format(cleanName))

    def _sanitize_file_name(self, value):
        clean = re.sub(r"[^A-Za-z0-9_. -]+", "_", str(value).strip())
        clean = re.sub(r"\s+", "_", clean)
        clean = clean.strip("._ ")
        if not clean:
            clean = self._default_route_name()
        return clean[:80]

    def _default_route_name(self):
        return "rail_{}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    def _now_iso(self):
        return datetime.datetime.now().replace(microsecond=0).isoformat()

    def _truncate(self, text, limit):
        text = str(text)
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 3)] + "..."


railCreator = RailCreator()
railCreator.main()
railCreator.run()
