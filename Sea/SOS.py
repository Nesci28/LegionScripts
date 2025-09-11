import API
import re
import importlib
import math
from collections import defaultdict
import json
import os
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Debug
import Error
import Util
import Math
import Gump
import Item

importlib.reload(Debug)
importlib.reload(Error)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Gump)
importlib.reload(Item)

from Debug import debug
from Error import Error
from Util import Util
from Math import Math
from Gump import Gump
from Item import Item


class SOS:
    GUMP_ID = 999019
    SOS_GRAPHIC = 5358
    COORD_PATTERN = re.compile(
        r"(\d{1,3})o ?(\d{1,2})'([NS]),\s+(\d{1,3})o ?(\d{1,2})'([EW])"
    )
    GUMP_WIDTH = 83
    GUMP_HEIGHT = 500
    MAIN_GUMP_WIDTH = 400
    TIMEOUT = 0.3
    SAVE_FILE = f"{Util.getPlayerName()}_sos_data.json"
    USER_MARKERS_FILE = r".\\TazUO\\Data\\Client\\userMarkers.usr"

    REGION_NAMES = [
        "Yew",
        "Shame",
        "Skara",
        "Destard",
        "Jhelom",
        "Wrong",
        "Britain",
        "Cove",
        "Trinsic",
        "Valor",
        "Vesper",
        "Nujel'm",
        "Bucca",
        "Fire",
        "Moonglow",
        "Sea Market",
        "Hythloth",
    ]

    COLOR_PALETTE = [
        "red",
        "blue",
        "green",
        "orange",
        "purple",
        "cyan",
        "yellow",
        "white",
        "gray",
    ]

    # ------------------------------
    # Lifecycle
    # ------------------------------
    def __init__(self):
        self._running = True
        self._started = False

        # parsing/scan state
        self._sosSerials = []
        self._scanIndex = 0
        self._rawRows = []  # temporary rows before clustering
        # row shape: [x, y, mapIndex, name, pinType, color, size, isDone, sosSerial]
        self.rows = []

        # UI
        self.markerNames = []
        self.regionGumps = {}
        self.gump = Gump(self.GUMP_WIDTH, self.GUMP_HEIGHT, self._onClose, False)
        self.statusGump = self.gump.createSubGump(483, 100, withStatus=True)
        self.progressBar = None

        # inventory
        self.fishingPoleSerial = self._findItem(0x0DBF)

        # movement
        self._moveActive = False
        self._moveTarget = (0, 0)
        self._lastDirectionSent = None
        self._lockedDirection = None

        # fishing
        self._fishingActive = False
        self._fishingResult = []
        self._fishingOffset = (3, -3)
        self._fishingName = None
        self._fishingLabel = None
        self._fishingRegionGump = None
        self._fishingX = None
        self._fishingY = None
        self._fishingRowX = None
        self._fishingRowY = None

    def main(self):
        self._showGump()
        self._loadScan()

    def tick(self):
        if self._started:
            self._processParsing()
        if self._moveActive:
            self._processMovement()
        if self._fishingActive:
            self._processFishing()

    # ------------------------------
    # JSON helpers
    # ------------------------------
    @staticmethod
    def _json_default(o):
        # Future-proof CLR numerics/objects coming from .NET
        try:
            return int(o)
        except Exception:
            pass
        try:
            return float(o)
        except Exception:
            pass
        return str(o)

    def _save_rows(self):
        try:
            with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.rows, f, default=self._json_default)
        except Exception as e:
            API.SysMsg(str(e))

    # ------------------------------
    # Fishing pipeline
    # ------------------------------
    def _processFishing(self):
        if not self._fishingResult:
            xOffset, yOffset = self._fishingOffset
            self._fishingResult = self._fish(xOffset, yOffset)

        if "Finish" in self._fishingResult:
            self.statusGump.setStatus("Fishing complete!")
            self._fishingActive = False
            self._fishingResult = []
            if self._fishingName:
                API.RemoveMapMarker(self._fishingName)
                # keep markerNames list consistent
                if self._fishingName in self.markerNames:
                    self.markerNames.remove(self._fishingName)
                self._fishingName = None
            if self._fishingRegionGump:
                self._scratch(
                    self._fishingRegionGump,
                    self._fishingX,
                    self._fishingY,
                    self._fishingRowX,
                    self._fishingRowY,
                    self._fishingLabel,
                )
                self._fishingRegionGump = None
                self._fishingX = None
                self._fishingY = None
                self._fishingRowX = None
                self._fishingRowY = None
            if self._fishingLabel:
                self._fishingLabel.Hue = 996
                self._fishingLabel = None

        elif "Continue" in self._fishingResult:
            self._fishingResult = []

        else:
            self.statusGump.setStatus("Fishing stopped (no result).")
            self._fishingActive = False

    def _startFishing(self, name, label, regionGump, fishingX, fishingY, rowX, rowY):
        self._fishingActive = True
        self._fishingResult = []
        self._fishingName = name
        self._fishingLabel = label
        label.Hue = 80
        self._fishingRegionGump = regionGump
        self._fishingX = fishingX
        self._fishingY = fishingY
        self._fishingRowX = rowX
        self._fishingRowY = rowY

    def _fish(self, xOffset, yOffset):
        self.statusGump.setStatus("Fishing...")
        API.ClearJournal()
        Util.useObjectWithTarget(self.fishingPoleSerial)
        API.TargetLandRel(xOffset, yOffset)
        API.CreateCooldownBar(11, "Fishing...", 88)
        return self._scanJournal()

    def _scanJournal(self):
        while True:
            res = []
            if API.InJournalAny(
                [
                    "You pull out torso!",
                    "You pull out bone pile!",
                    "You pull out barrel staves!",
                    "You pull out skullcap!",
                    "You pull out nautilus!",
                    "You pull out painting!",
                    "You pull out anchor!",
                    "You pull out porthole!",
                    "You pull out fish heads!",
                    "You pull out skull!",
                    "You pull out leg!",
                    "You pull out shoes!",
                    "You pull out pillow!",
                    "You pull out shells!",
                    "You pull out stool!",
                    "You pull out portrait!",
                    "You pull out chain!",
                    "You pull out ship in a bottle!",
                    "You pull out candelabra!",
                    "You pull out shell!",
                    "You pull out conch shell!",
                    "You pull out boots!",
                    "You pull out thigh boots!",
                    "You pull out globe!",
                    "You pull out tricorne hat!",
                    "You pull out head!",
                    "You pull out unfinished barrel!",
                    "You pull out chest of drawers!",
                    "You pull out arm!",
                    "You pull out pelvis bone!",
                    "You pull out table legs!",
                    "You pull out sandals!",
                    "You pull out broken clock!",
                    "You pull out oars!",
                    "You pull out Yellow Polkadot Bikini Top!",
                    "$You pull out.*!",
                ]
            ):
                res.append("Continue")
            if API.InJournal("You pull up a heavy chest from the depths of the ocean!"):
                res.append("Finish")
            if res:
                return res
            API.Pause(0.5)

    # ------------------------------
    # Scan / parse
    # ------------------------------
    def _loadScan(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Basic sanity: each row should have 9 fields
                if isinstance(data, list) and all(
                    isinstance(r, (list, tuple)) and len(r) == 9 for r in data
                ):
                    self.rows = data
                    self.statusGump.setStatus("Loaded saved SOS data.")
                    self._updateRegionGump()
                    # Re-add markers for loaded rows
                    for x, y, mapIndex, name, _, color, _, _, _ in self.rows:
                        API.AddMapMarker(name, x, y, mapIndex, color)
                        if name not in self.markerNames:
                            self.markerNames.append(name)
                    return
                else:
                    self.statusGump.setStatus("Saved data corrupted; re-scanning.")
            except Exception as e:
                API.SysMsg(str(e))
                self.statusGump.setStatus("Error loading saved SOS data; re-scanning.")
        self._scan()

    def _scan(self):
        self._clearExistingMarkers()
        self._sosSerials = [
            item.Serial
            for item in Util.itemsInContainer(API.Backpack)
            if item.Graphic == self.SOS_GRAPHIC and item.Hue == 0
        ]
        self.statusGump.setStatus("Scanning SOS...")
        self.progressBar = API.CreateGumpSimpleProgressBar(
            453, 25, value=0, max=len(self._sosSerials)
        )
        self.progressBar.SetX(10)
        self.progressBar.SetY(10)
        self.statusGump.gump.Add(self.progressBar)
        self._started = True

    def _processParsing(self):
        if self._scanIndex >= len(self._sosSerials):
            # Cluster and create final rows
            self.rows = self._groupBySector(self._rawRows)
            # Add markers and remember names for cleanup
            for x, y, mapIndex, name, _, color, _, _, _ in self.rows:
                API.AddMapMarker(name, x, y, mapIndex, color)
                if name not in self.markerNames:
                    self.markerNames.append(name)
            self._started = False
            self._save_rows()
            self._updateRegionGump()
            return

        sosSerial = self._sosSerials[self._scanIndex]
        while True:
            API.UseObject(sosSerial)
            API.Pause(self.TIMEOUT)
            gump = API.GetGump(self.GUMP_ID)
            if gump:
                break

        lines = gump.PacketGumpText.split("\n")
        coord = self._extractCoords(lines[0])
        if coord:
            x, y = Math.latLonToTiles(*coord)
            # raw row (pre-cluster): [x, y, mapIndex, "", "", "", "", False, sosSerial]
            self._rawRows.append([x, y, 1, "", "", "", "", False, int(sosSerial)])
        else:
            debug(f"Could not parse coordinates from: {lines[0]}")

        API.CloseGump(self.GUMP_ID)
        API.Pause(self.TIMEOUT)

        self._scanIndex += 1
        if self.progressBar:
            self.progressBar.SetProgress(self._scanIndex, len(self._sosSerials))

    # ------------------------------
    # Grouping / route
    # ------------------------------
    def _groupBySector(self, rows):
        """
        Input rows (raw) shape:
            [x, y, mapIndex, "", "", "", "", False, sosSerial]
        Output clustered rows shape:
            [x, y, mapIndex, name, "PIN", color, 3, False, sosSerial]
        """
        sectorClusters = defaultdict(list)

        for x, y, mapIndex, _, _, _, _, _, sosSerial in rows:
            sector = self._getSector(x, y)
            # Keep serial with point
            sectorClusters[sector].append([x, y, mapIndex, int(sosSerial)])

        clustered = []

        # Deterministic ordering by REGION_NAMES, then any leftover sectors
        ordered_sectors = [s for s in self.REGION_NAMES if s in sectorClusters] + [
            s for s in sectorClusters.keys() if s not in self.REGION_NAMES
        ]

        for idx, sector in enumerate(ordered_sectors):
            cluster = sectorClusters[sector]
            ordered = self._optimizeRoute(cluster)  # keeps 4-field shape
            color = self.COLOR_PALETTE[idx % len(self.COLOR_PALETTE)]
            for i, (x, y, mapIndex, sosSerial) in enumerate(ordered, 1):
                name = f"{sector} - {i}"
                clustered.append(
                    [x, y, mapIndex, name, "PIN", color, 3, False, int(sosSerial)]
                )

        return clustered

    def _optimizeRoute(self, points):
        """
        points: list[[x, y, mapIndex, sosSerial]]
        returns ordered list with same shape
        """
        if not points:
            return []
        points = points[:]  # don't mutate caller list
        ordered = [points.pop(0)]
        while points:
            last = ordered[-1]
            next_point = min(
                points, key=lambda p: math.hypot(last[0] - p[0], last[1] - p[1])
            )
            points.remove(next_point)
            ordered.append(next_point)
        return ordered

    # ------------------------------
    # Movement
    # ------------------------------
    def _move(self, x, y, name, label, regionGump, fishingX, fishingY):
        self._moveTarget = (x, y)
        self._moveActive = True
        self._lastDirectionSent = None
        self.statusGump.setStatus(f"Moving to ({x}, {y})...")
        self._fishingName = name
        self._fishingLabel = label
        label.Hue = 80
        self._fishingRegionGump = regionGump
        self._fishingX = fishingX
        self._fishingY = fishingY
        self._fishingRowX = x
        self._fishingRowY = y

    def _processMovement(self):
        if not self._moveActive:
            return

        targetX, targetY = self._moveTarget
        currentX, currentY = API.Player.X, API.Player.Y
        dx, dy = targetX - currentX, targetY - currentY

        if abs(dx) <= 2 and abs(dy) <= 2:
            API.Msg("Stop")
            self.statusGump.setStatus("Arrived at destination.")
            self._moveActive = False
            self._lastDirectionSent = None
            self._fishingActive = True
            self._fishingResult = []
            return

        direction = self._getDirection(dx, dy)
        if direction and direction != self._lastDirectionSent:
            API.Msg(direction)
            self._lastDirectionSent = direction

        if API.InJournalAny(
            [
                "You can't move that way.",
                "You must lower the anchor.",
            ]
        ):
            API.Msg("Stop")
            self.statusGump.setStatus("Movement blocked!")
            self._moveActive = False
            self._lastDirectionSent = None

    def _getDirection(self, dx, dy):
        if abs(dx) <= 2:
            dx = 0
        if abs(dy) <= 2:
            dy = 0

        # Clear lock if one delta is now 0-ish
        if dx == 0 or dy == 0:
            self._lockedDirection = None

        # Use locked direction if available
        if self._lockedDirection:
            return self._lockedDirection

        dir_x = ""
        dir_y = ""

        if dy < 0:
            dir_y = "forward"
        elif dy > 0:
            dir_y = "back"

        if dx < 0:
            dir_x = "left"
        elif dx > 0:
            dir_x = "right"

        if dir_x and dir_y:
            self._lockedDirection = f"{dir_y} {dir_x}"
            return self._lockedDirection

        return dir_y or dir_x

    # ------------------------------
    # UI
    # ------------------------------
    def _showGump(self):
        for region in self.REGION_NAMES:
            tab = self.gump.addTabButton(
                region,
                "default",
                self.MAIN_GUMP_WIDTH,
                yOffset=25,
                label=region,
                isDarkMode=True,
            )
            tab.addLabel(region, 10, 10)
            tab.addButton(
                "",
                200,
                8,
                "radioBlue",
                self.gump.onClick(lambda region=region: self._onMarkAllClicked(region)),
            )
            tab.addLabel("Mark", 225, 10)
            tab.addButton(
                "",
                270,
                8,
                "radioBlue",
                self.gump.onClick(lambda region=region: self._onMoveAllClicked(region)),
            )
            tab.addLabel("Move", 295, 10)
            self.regionGumps[region] = tab

        self.gump.addButton(
            "Scan",
            5,
            self.gump.height - 38,
            "default",
            self.gump.onClick(self._scan, "", ""),
            True,
        )
        self.gump.create()
        self.gump.setActiveTab("Yew")

    def _updateRegionGump(self):
        tabX1 = self.MAIN_GUMP_WIDTH - 40
        tabX2 = self.MAIN_GUMP_WIDTH - 63 - 40 - 5
        tabX3 = self.MAIN_GUMP_WIDTH - 63 - 63 - 40 - 5 - 5
        x = 10
        yOffset = 35

        for region in self.REGION_NAMES:
            regionGump = self.regionGumps[region]
            y = yOffset
            for rowX, rowY, _, name, _, _, _, isDone, _ in self.rows:
                if name.split(" - ")[0] != region:
                    continue
                label = regionGump.addLabel(name, x, y)
                regionGump.addButton(
                    "Move",
                    tabX3,
                    y,
                    "default",
                    self.gump.onClick(
                        lambda x=rowX, y=rowY, name=name, label=label, regionGump=regionGump, fishingX=10, fishingY=y: self._move(
                            x, y, name, label, regionGump, fishingX, fishingY
                        ),
                        "Moving...",
                        "",
                    ),
                    True,
                )
                regionGump.addButton(
                    "Fish",
                    tabX2,
                    y,
                    "default",
                    self.gump.onClick(
                        lambda rowX=rowX, rowY=rowY, name=name, label=label, regionGump=regionGump, fishingX=10, fishingY=y: self._startFishing(
                            name, label, regionGump, fishingX, fishingY, rowX, rowY
                        ),
                        "Fishing...",
                        "",
                    ),
                    True,
                )
                regionGump.addButton(
                    "",
                    tabX1,
                    y,
                    "squareX",
                    self.gump.onClick(
                        lambda rowX=rowX, rowY=rowY, regionGump=regionGump, x=10, y=y, label=label: self._scratch(
                            regionGump, x, y, rowX, rowY, label
                        ),
                        "",
                        "",
                    ),
                )
                if isDone:
                    self._addColorBox(regionGump, x, y)
                y += 25

  # ------------------------------
    # Bulk actions: Mark / Move
    # ------------------------------
    def _onMoveAllClicked(self, region: str):
        """
        Prompt for a container, then move all SOS bottles belonging to `region`
        into that container.
        """
        try:
            containerSerial = API.RequestTarget()
            if not containerSerial:
                self.statusGump.setStatus("No container targeted.")
                return

            container = API.FindItem(int(containerSerial))
            if not container or not Item.isItemContainer(container):
                API.SysMsg("Target is not a container.", 33)
                self.statusGump.setStatus("Move aborted: invalid container.")
                return

            moved = 0
            for _, _, _, name, _, _, _, _, sosSerial in self.rows:
                # match e.g. "Yew - 1" -> "Yew"
                if name.split(" - ")[0] != region:
                    continue
                if sosSerial is None:
                    continue

                sos = API.FindItem(int(sosSerial))
                if sos:
                    Util.moveItem(int(sosSerial), int(containerSerial))
                    moved += 1

            self.statusGump.setStatus(f"Moved {moved} SOS to the target container.")
        except Exception as e:
            API.SysMsg(str(e))
            self.statusGump.setStatus("Error while moving SOS.")

    def _onMarkAllClicked(self, region: str):
        """
        Hue all SOS bottles belonging to `region` so they stand out in your pack.
        """
        try:
            marked = 0
            for _, _, _, name, _, _, _, _, sosSerial in self.rows:
                if name.split(" - ")[0] != region:
                    continue
                if sosSerial is None:
                    continue

                sos = API.FindItem(int(sosSerial))
                if sos:
                    # 11 = the hue you were using previously
                    sos.SetHue(11)
                    marked += 1

            self.statusGump.setStatus(f"Marked {marked} SOS in {region}.")
        except Exception as e:
            API.SysMsg(str(e))
            self.statusGump.setStatus("Error while marking SOS.")

    def _addColorBox(self, regionGump, x, y):
        rowY = int(y + ((23 - 4) / 2))
        regionGump.addColorBox(x, rowY, 3, self.MAIN_GUMP_WIDTH - 30)

    def _scratch(self, regionGump, x, y, sosX, sosY, label):
        label.Hue = 996
        self._addColorBox(regionGump, x, y)
        for i, row in enumerate(self.rows):
            rowX, rowY, a, b, c, d, e, isDone, sosSerial = row  # 9 fields
            if rowX == sosX and rowY == sosY:
                self.rows[i] = [rowX, rowY, a, b, c, d, e, True, int(sosSerial)]
        self._save_rows()

    # ------------------------------
    # Map markers file cleanup
    # ------------------------------
    def _clearExistingMarkers(self):
        marker_path = self.USER_MARKERS_FILE
        if not os.path.exists(marker_path):
            return
        row_pattern = re.compile(
            r"^\d{1,4},\d{1,4},1,[^,]+ - \d+,\s*,(red|blue|green|orange|purple|cyan|yellow|white|gray),\d+\s*$"
        )
        try:
            with open(marker_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            filtered_lines = [
                line for line in lines if not row_pattern.match(line.strip())
            ]
            with open(marker_path, "w", encoding="utf-8") as f:
                f.writelines(filtered_lines)
        except Exception as e:
            debug(f"Failed to clean userMarkers.usr: {e}")

    # ------------------------------
    # Inventory
    # ------------------------------
    def _findItem(self, itemId):
        API.Pause(1)
        fishingPole = Util.findType(API.Backpack, itemId)
        if not fishingPole:
            API.SysMsg(f"No: {str(itemId)}", 33)
            API.Stop()
        return fishingPole.Serial

    # ------------------------------
    # Utils
    # ------------------------------
    def _extractCoords(self, line):
        match = self.COORD_PATTERN.search(line)
        if not match:
            return None
        latDeg, latMin, latDir, lonDeg, lonMin, lonDir = match.groups()
        return int(latDeg), int(latMin), latDir, int(lonDeg), int(lonMin), lonDir

    def _getSector(self, x, y):
        if x < 1385 and 0 <= y < 1280:
            return "Yew"
        if x < 1000 and 1280 <= y < 2027:
            return "Shame"
        if x < 1000 and 2036 <= y < 2450:
            return "Skara"
        if x < 1300 and 2450 <= y < 3200:
            return "Destard"
        if x < 1900 and 3200 <= y <= 4096:
            return "Jhelom"
        if 1385 <= x < 2690 and y < 900:
            return "Wrong"
        if 1385 <= x < 2100 and 1280 <= y < 2030:
            return "Britain"
        if 2100 <= x < 2690 and 1280 <= y < 2030:
            return "Cove"
        if 1385 <= x < 2690 and 2030 <= y < 3075:
            return "Trinsic"
        if 1900 <= x < 2690 and 3075 <= y <= 4096:
            return "Valor"
        if 2580 <= x < 3250 and y < 1890:
            return "Vesper"
        if 3250 <= x < 4100 and y < 1890:
            return "Nujel'm"
        if 2100 <= x < 3850 and 1890 <= y < 3075:
            return "Bucca"
        if 2690 <= x < 3850 and 3075 <= y <= 4096:
            return "Fire"
        if x >= 4100 and y < 1890:
            return "Moonglow"
        if x >= 3850 and 1890 <= y < 2890:
            return "Sea Market"
        if x >= 3850 and y >= 2890:
            return "Hythloth"
        return "None"

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        for sub in self.gump.subGumps:
            sub.destroy()
        self.gump.destroy()
        for name in list(self.markerNames):
            API.RemoveMapMarker(name)
        self.markerNames = []
        API.Stop()

    def _isRunning(self):
        return self._running


sos = SOS()
sos.main()
while sos._isRunning():
    sos.gump.tick()
    sos.gump.tickSubGumps()
    sos.tick()
    API.Pause(0.1)
