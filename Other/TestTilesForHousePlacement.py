import json
import time

import API


# Name: Test Tiles for House Placement
# Description: Displays likely valid tiles for house placement.
# Usage: Stand where you want to place a house and hit play.
# Original: github.com/UltimaScripts/PublicScriptLibrary
# Port: LegioScript/TazUO API version


# ===== Options Start =====
# Set to True to remove the last display made by this script.
remove_display = False

# Keep updating the display as you move. Stop the script when you are done.
track_while_running = True

# How often to check whether you moved while tracking.
refresh_delay = 0.03

# Paint every Nth tile while moving. Use 1 for full detail while moving.
# Higher values are much faster because TazUO has no batch MarkTile API.
moving_display_stride = 3

# After standing still this many seconds, repaint at full detail.
idle_full_detail_delay = 0.35

# Clear the current display when the tracking script is stopped.
# Leave False if you want to inspect the last calculated area.
clear_on_stop = False

# Never set square_size higher than 24.
square_size = 10

# height_tolerance is usually 0.
height_tolerance = 0
# ===== Options End =====


MAX_SQUARE_SIZE = 24
MAX_INCREMENTAL_STEP = 4
MARKED_TILES_VAR = "TestTilesForHousePlacement.MarkedTiles"

BLOCKED_HUE = 0
WARNING_HUE = 1259
VALID_HUE = 1271

STATIC_NONE = 0
STATIC_PASSABLE = 1
STATIC_IMPASSIBLE = 2

# Roads list is technically incomplete.
# May lead to false results, outside of roads.
ROADS = {
    0x0071,
    0x0078,
    0x00E8,
    0x00EB,
    0x07AE,
    0x07B1,
    0x3FF4,
    0x3FF8,
    0x3FFB,
    0x0442,
    0x0479,
    0x0501,
    0x0510,
    0x0009,
    0x0015,
    0x0150,
    0x015C,
    0x0170,
    0x0072,
    0x0073,
    0x0074,
    0x0075,
    0x0076,
    0x0077,
    0x0079,
    0x007A,
    0x007C,
    0x007D,
    0x007E,
    0x0082,
    0x0083,
    0x0085,
    0x0086,
    0x0087,
    0x0088,
    0x0089,
    0x008A,
    0x008B,
    0x008C,
    0x016F,
}


def _current_map():
    try:
        return int(getattr(API.Player, "Map", -1))
    except Exception:
        return -1


def _player_position():
    return (
        int(API.Player.X),
        int(API.Player.Y),
        int(API.Player.Z),
        _current_map(),
    )


def _normalized_square_size():
    size = abs(int(square_size))
    if size > MAX_SQUARE_SIZE:
        API.SysMsg("square_size is capped at 24.", 33)
        return MAX_SQUARE_SIZE

    return size


def _stop_requested():
    return bool(getattr(API, "StopRequested", False))


def _has_any_attr(obj, names):
    if obj is None:
        return False

    for name in names:
        try:
            if bool(getattr(obj, name)):
                return True
        except Exception:
            pass

    return False


def _area_xy(center_x, center_y, size):
    for x_offset in range(-size, size + 1):
        for y_offset in range(-size, size + 1):
            yield (center_x + x_offset, center_y + y_offset)


def _area_keys(center_x, center_y, size, map_index, stride=1):
    for x, y in _area_xy(center_x, center_y, size):
        if stride <= 1 or (x % stride == 0 and y % stride == 0):
            yield (x, y, map_index)


def _bounds_from_keys(keys, margin=0):
    xs = []
    ys = []

    for key in keys:
        xs.append(int(key[0]))
        ys.append(int(key[1]))

    if not xs:
        return None

    return (
        min(xs) - margin,
        min(ys) - margin,
        max(xs) + margin,
        max(ys) + margin,
    )


def _read_tile_data(x, y, fallback_z):
    try:
        tile = API.GetTile(x, y)
    except Exception:
        tile = None

    if tile is None:
        return {
            "z": int(fallback_z),
            "graphic": -1,
            "impassible": False,
        }

    return {
        "z": int(getattr(tile, "Z", fallback_z)),
        "graphic": int(getattr(tile, "Graphic", -1)),
        "impassible": _has_any_attr(tile, ("Impassible", "IsImpassible", "IsImpassable")),
    }


def _static_state(static):
    if _has_any_attr(static, ("IsImpassible", "Impassible", "IsImpassable")):
        return STATIC_IMPASSIBLE

    return STATIC_PASSABLE


def _iter_tile_keys(tiles):
    if hasattr(tiles, "keys"):
        tiles = tiles.keys()

    for tile in tiles:
        try:
            x = int(tile[0])
            y = int(tile[1])
            map_index = int(tile[2]) if len(tile) > 2 else -1
        except Exception:
            continue

        yield (x, y, map_index)


def _load_marked_tiles():
    try:
        raw = API.GetPersistentVar(MARKED_TILES_VAR, "[]", API.PersistentVar.Char)
    except Exception:
        return []

    if not raw:
        return []

    try:
        tiles = json.loads(raw)
    except Exception:
        return []

    return list(_iter_tile_keys(tiles))


def _save_marked_tiles(marks):
    if hasattr(marks, "items"):
        data = [
            [int(x), int(y), int(map_index), int(hue)]
            for (x, y, map_index), hue in marks.items()
        ]
    else:
        data = [[int(x), int(y), int(map_index)] for x, y, map_index in _iter_tile_keys(marks)]

    API.SavePersistentVar(MARKED_TILES_VAR, json.dumps(data), API.PersistentVar.Char)


def _forget_marked_tiles():
    try:
        API.RemovePersistentVar(MARKED_TILES_VAR, API.PersistentVar.Char)
    except Exception:
        _save_marked_tiles([])


def _remove_marks(tiles):
    seen = set()

    for x, y, map_index in _iter_tile_keys(tiles):
        key = (x, y, map_index)
        if key in seen:
            continue

        seen.add(key)
        API.RemoveMarkedTile(x, y, map_index)


def _clear_display(size, include_current_area=False):
    tiles = _load_marked_tiles()

    if include_current_area:
        player_x, player_y, _, map_index = _player_position()
        tiles += list(_area_keys(player_x, player_y, size, map_index))

    _remove_marks(tiles)
    _forget_marked_tiles()


class HousePlacementTiles:
    def __init__(self, size):
        self.size = size
        self.tile_cache = {}
        self.static_cache = {}
        self.marks = {}
        self.center_x = None
        self.center_y = None
        self.player_z = None
        self.map_index = None
        self.stride = 1

    def reset_cache(self):
        self.tile_cache = {}
        self.static_cache = {}

    def ensure_rect(self, x1, y1, x2, y2, fallback_z):
        self.ensure_tiles_rect(x1, y1, x2, y2, fallback_z)
        self.ensure_statics_rect(x1, y1, x2, y2)

    def ensure_tiles_rect(self, x1, y1, x2, y2, fallback_z):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                key = (x, y)
                if key not in self.tile_cache:
                    self.tile_cache[key] = _read_tile_data(x, y, fallback_z)

    def ensure_statics_rect(self, x1, y1, x2, y2):
        missing = []

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                key = (x, y)
                if key not in self.static_cache:
                    self.static_cache[key] = STATIC_NONE
                    missing.append(key)

        if not missing:
            return

        missing_set = set(missing)

        try:
            statics = API.GetStaticsInArea(x1, y1, x2, y2)
        except Exception:
            statics = None

        if statics is None:
            for x, y in missing:
                try:
                    tile_statics = API.GetStaticsAt(x, y)
                except Exception:
                    tile_statics = []

                if not tile_statics:
                    continue

                state = STATIC_NONE
                for static in tile_statics:
                    static_state = _static_state(static)
                    if static_state == STATIC_IMPASSIBLE:
                        state = STATIC_IMPASSIBLE
                        break
                    state = max(state, static_state)

                self.static_cache[(x, y)] = state

            return

        for static in statics or []:
            try:
                key = (int(static.X), int(static.Y))
            except Exception:
                continue

            if key not in missing_set:
                continue

            static_state = _static_state(static)
            if static_state == STATIC_IMPASSIBLE:
                self.static_cache[key] = STATIC_IMPASSIBLE
            elif self.static_cache[key] == STATIC_NONE:
                self.static_cache[key] = STATIC_PASSABLE

    def ensure_for_tiles(self, keys, player_z):
        bounds = _bounds_from_keys(keys, margin=1)
        if bounds is None:
            return

        self.ensure_rect(bounds[0], bounds[1], bounds[2], bounds[3], player_z)

    def is_impassible(self, x, y):
        key = (x, y)
        static_state = self.static_cache.get(key, STATIC_NONE)

        if static_state != STATIC_NONE:
            return static_state == STATIC_IMPASSIBLE

        tile_data = self.tile_cache.get(key)
        if tile_data is None:
            tile_data = _read_tile_data(x, y, self.player_z or 0)
            self.tile_cache[key] = tile_data

        return bool(tile_data["impassible"])

    def has_impassible_neighbor(self, x, y):
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                if self.is_impassible(x + x_offset, y + y_offset):
                    return True

        return False

    def hue_for_tile(self, x, y, player_z):
        tile_data = self.tile_cache.get((x, y))
        if tile_data is None:
            tile_data = _read_tile_data(x, y, player_z)
            self.tile_cache[(x, y)] = tile_data

        z = int(tile_data["z"])
        blocked = self.is_impassible(x, y)
        warned = self.has_impassible_neighbor(x, y)

        if z != player_z and not blocked and not warned:
            minimum_z = player_z - int(height_tolerance)
            maximum_z = player_z + int(height_tolerance)
            if not minimum_z <= z <= maximum_z:
                warned = True

        if blocked or tile_data["graphic"] in ROADS:
            return BLOCKED_HUE

        if warned:
            return WARNING_HUE

        return VALID_HUE

    def full_repaint(self, player_x, player_y, player_z, map_index, stride=1):
        if self.map_index is not None and self.map_index != map_index:
            self.reset_cache()

        keys = set(_area_keys(player_x, player_y, self.size, map_index, stride))
        self.ensure_for_tiles(keys, player_z)

        new_marks = {}
        for x, y, key_map in keys:
            new_marks[(x, y, key_map)] = self.hue_for_tile(x, y, player_z)

        self.apply_full_diff(new_marks)
        self.center_x = player_x
        self.center_y = player_y
        self.player_z = player_z
        self.map_index = map_index
        self.stride = stride

    def apply_full_diff(self, new_marks):
        stale_keys = set(self.marks.keys()) - set(new_marks.keys())

        for x, y, map_index in stale_keys:
            API.RemoveMarkedTile(x, y, map_index)

        for key, hue in new_marks.items():
            if self.marks.get(key) != hue:
                x, y, map_index = key
                API.MarkTile(x, y, hue, map_index)

        self.marks = dict(new_marks)

    def incremental_step(self, next_x, next_y):
        old_keys = set(_area_keys(self.center_x, self.center_y, self.size, self.map_index, self.stride))
        new_keys = set(_area_keys(next_x, next_y, self.size, self.map_index, self.stride))
        stale_keys = old_keys - new_keys
        entering_keys = new_keys - old_keys

        for x, y, map_index in stale_keys:
            API.RemoveMarkedTile(x, y, map_index)
            self.marks.pop((x, y, map_index), None)

        self.ensure_for_tiles(entering_keys, self.player_z)

        for x, y, map_index in entering_keys:
            hue = self.hue_for_tile(x, y, self.player_z)
            API.MarkTile(x, y, hue, map_index)
            self.marks[(x, y, map_index)] = hue

        self.center_x = next_x
        self.center_y = next_y

    def move_to(self, player_x, player_y, player_z, map_index, stride=1):
        stride = max(1, int(stride))

        if self.center_x is None:
            self.full_repaint(player_x, player_y, player_z, map_index, stride)
            return

        if map_index != self.map_index or player_z != self.player_z or stride != self.stride:
            self.full_repaint(player_x, player_y, player_z, map_index, stride)
            return

        dx = player_x - self.center_x
        dy = player_y - self.center_y

        if dx == 0 and dy == 0:
            return

        if abs(dx) > MAX_INCREMENTAL_STEP or abs(dy) > MAX_INCREMENTAL_STEP:
            self.full_repaint(player_x, player_y, player_z, map_index, stride)
            return

        while self.center_x != player_x:
            step = 1 if player_x > self.center_x else -1
            self.incremental_step(self.center_x + step, self.center_y)

        while self.center_y != player_y:
            step = 1 if player_y > self.center_y else -1
            self.incremental_step(self.center_x, self.center_y + step)


def _run_once(size):
    scanner = HousePlacementTiles(size)
    scanner.move_to(*_player_position())
    _save_marked_tiles(scanner.marks)
    API.SysMsg("House placement test tiles marked.", 68)


def _run_tracking(size):
    scanner = HousePlacementTiles(size)
    API.SysMsg("House placement tracking started.", 68)
    last_position = None
    last_move_time = time.monotonic()

    try:
        scanner.move_to(*_player_position(), stride=moving_display_stride)
        _save_marked_tiles(scanner.marks)

        while not _stop_requested():
            position = _player_position()
            now = time.monotonic()

            if position != last_position:
                last_position = position
                last_move_time = now

            stride = moving_display_stride
            if idle_full_detail_delay >= 0 and now - last_move_time >= idle_full_detail_delay:
                stride = 1

            scanner.move_to(*position, stride=stride)
            API.Pause(float(refresh_delay))
    finally:
        if clear_on_stop:
            _remove_marks(scanner.marks)
            _forget_marked_tiles()
        else:
            _save_marked_tiles(scanner.marks)


size = _normalized_square_size()

if remove_display:
    _clear_display(size, include_current_area=True)
    API.SysMsg("House placement test tiles removed.", 68)
    API.Stop()
else:
    _clear_display(size)

    if track_while_running:
        _run_tracking(size)
    else:
        _run_once(size)
