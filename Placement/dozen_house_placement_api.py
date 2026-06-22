# Name: Fast House Placement Scanner
# Description: House placement scanner using the new LegionScript placement APIs.
# Usage: Stand near the area to scan, run the script, then use the menu buttons.
# Author: Dozen / updated for LegionScript placement APIs
# Version: 4.0.0

import json
import os
import threading
import time


CONFIG_FILE = "Data/house_placement_config.json"

DEFAULT_COLORS = {
    "valid": 64,
    "invalid": 38,
    "border": 1259,
    "7x7": 888,
    "2-story": 888,
    "3-story": 40,
    "largest": 46,
}

ROAD_GRAPHICS = {
    0x0071, 0x0078, 0x00E8, 0x00EB, 0x07AE, 0x07B1, 0x3FF4, 0x3FF8, 0x3FFB,
    0x0442, 0x0479, 0x0501, 0x0510, 0x0009, 0x0015, 0x0150, 0x015C, 0x0170,
    0x0072, 0x0073, 0x0074, 0x0075, 0x0076, 0x0077, 0x0079, 0x007A, 0x007C,
    0x007D, 0x007E, 0x0082, 0x0083, 0x0085, 0x0086, 0x0087, 0x0088, 0x0089,
    0x008A, 0x008B, 0x008C, 0x016F,
}

tile_scan_radius = 12
house_search_radius = 12
height_tolerance = 2
display_duration = 60
remove_display = False

direction = "south"
front_clearance = 6
back_clearance = 5
side_clearance = 1
allow_small_plants = True
include_steps = True

ALLOWED_2_STORY_SIZES = (
    [(7, depth) for depth in range(7, 13)] +
    [(width, depth) for width in range(8, 14) for depth in range(7, 14)]
)

ALLOWED_3_STORY_SIZES = [
    (width, depth)
    for width in range(9, 19)
    for depth in range(14, 19)
]

ALLOWED_PLOT_SIZES = ALLOWED_2_STORY_SIZES + ALLOWED_3_STORY_SIZES

marked_tiles_global = []


class ConfigManager:
    @staticmethod
    def load_colors():
        try:
            if not os.path.exists(CONFIG_FILE):
                return DEFAULT_COLORS.copy()

            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)

            colors = DEFAULT_COLORS.copy()
            colors.update(data.get("colors", {}))
            return colors
        except Exception as e:
            API.SysMsg("Warning: Could not load config: {0}".format(str(e)), 33)
            return DEFAULT_COLORS.copy()

    @staticmethod
    def save_colors(colors):
        try:
            directory = os.path.dirname(CONFIG_FILE)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with open(CONFIG_FILE, "w") as f:
                json.dump({"colors": colors}, f, indent=2)

            return True
        except Exception as e:
            API.SysMsg("Error: Could not save config: {0}".format(str(e)), 33)
            return False


def get_player():
    player = API.Player
    if not player:
        API.SysMsg("Error: Could not get player information.", 33)
        return None
    return player


def as_int(value, default_value=0):
    try:
        return int(value)
    except Exception:
        return default_value


def unique_points(points):
    seen = set()
    result = []

    for point in points:
        if not point or len(point) < 2:
            continue

        x = as_int(point[0])
        y = as_int(point[1])
        key = (x, y)

        if key in seen:
            continue

        seen.add(key)
        result.append(key)

    return result


def track_points(points):
    global marked_tiles_global

    tracked = set(marked_tiles_global)
    for point in points:
        if point not in tracked:
            tracked.add(point)
            marked_tiles_global.append(point)


def rectangle_border_points(x, y, width, depth):
    points = []
    max_x = x + width - 1
    max_y = y + depth - 1

    for tx in range(x, max_x + 1):
        points.append((tx, y))
        points.append((tx, max_y))

    for ty in range(y + 1, max_y):
        points.append((x, ty))
        points.append((max_x, ty))

    return unique_points(points)


def get_points_from_blockers(blockers, limit=100):
    points = []

    try:
        for blocker in blockers:
            x = getattr(blocker, "X", 0)
            y = getattr(blocker, "Y", 0)
            if x > 0 and y > 0:
                points.append((x, y))
                if len(points) >= limit:
                    break
    except Exception:
        pass

    return unique_points(points)


def result_reasons(result, limit=3):
    reasons = []

    try:
        for reason in result.Reasons:
            if reason:
                reasons.append(str(reason))
            if len(reasons) >= limit:
                return reasons
    except Exception:
        pass

    reason = getattr(result, "Reason", "")
    if reason:
        reasons.append(str(reason))

    return reasons


def clear_all_markers():
    global marked_tiles_global

    try:
        points = unique_points(marked_tiles_global)
        count = len(points)

        if count:
            API.RemoveMarkedTiles(points)

        marked_tiles_global = []
        API.SysMsg("Cleared {0} markers.".format(count), 88)
    except Exception as e:
        API.SysMsg("Error clearing markers: {0}".format(str(e)), 33)


def schedule_auto_clear(points):
    if not remove_display:
        return

    def delayed_clear():
        try:
            time.sleep(display_duration)
            API.RemoveMarkedTiles(points)
        except Exception:
            pass

    t = threading.Thread(target=delayed_clear)
    t.daemon = True
    t.start()


def tile_land_z(tile, default_z=0):
    land = getattr(tile, "Land", None)
    return getattr(land, "Z", default_z)


def tile_land_graphic(tile):
    land = getattr(tile, "Land", None)
    return getattr(land, "Graphic", None)


def tile_has_static_impassable(tile):
    try:
        for static in tile.Statics:
            flags = getattr(static, "Flags", None)
            if flags and getattr(flags, "IsImpassable", False):
                return True
    except Exception:
        pass

    return False


def clearance_static_blocker_reason(tile):
    try:
        for static in tile.Statics:
            flags = getattr(static, "Flags", None)

            if getattr(static, "IsTree", False):
                return "tree"

            if getattr(static, "IsCave", False):
                return "cave"

            if not flags:
                continue

            if getattr(flags, "IsWall", False):
                return "wall"

            if getattr(flags, "IsDoor", False):
                return "door"

            if getattr(flags, "IsBridge", False):
                return "bridge"

            if getattr(flags, "IsNoHouse", False):
                return "no-house"

            if getattr(flags, "IsWet", False):
                return "wet"
    except Exception:
        pass

    return None


def tile_has_multi(tile):
    try:
        return len(tile.Multis) > 0
    except Exception:
        return False


def tile_region_blocks_housing(tile):
    region = getattr(tile, "Region", None)
    if not region:
        return False

    return (
        getattr(region, "NoHousing", False)
        or getattr(region, "IsGuardZone", False)
    )


def tile_region_is_guard_zone(tile):
    region = getattr(tile, "Region", None)
    if not region:
        return False

    return getattr(region, "IsGuardZone", False)


def static_is_small_buildover(static):
    flags = getattr(static, "Flags", None)
    if not flags:
        return False

    return (
        getattr(flags, "IsFoliage", False)
        or getattr(flags, "IsBackground", False)
        or getattr(static, "IsVegetation", False)
    )


def tile_has_major_static_blocker(tile):
    try:
        for static in tile.Statics:
            flags = getattr(static, "Flags", None)
            is_small = static_is_small_buildover(static)

            if getattr(static, "IsTree", False) or getattr(static, "IsCave", False):
                return True

            if flags:
                if (
                    getattr(flags, "IsNoHouse", False)
                    or getattr(flags, "IsWall", False)
                    or getattr(flags, "IsDoor", False)
                    or getattr(flags, "IsBridge", False)
                    or getattr(flags, "IsWet", False)
                    or getattr(flags, "IsImpassable", False)
                ):
                    return True

            if is_small and allow_small_plants:
                continue

            if getattr(static, "Height", 0) > 0:
                return True
    except Exception:
        pass

    return False


def is_house_rule_tile_valid(tile, player_z, tile_lookup):
    if not tile:
        return False

    if not getattr(tile, "InMapBounds", True):
        return False

    if not getattr(tile, "HasLand", False):
        return False

    if tile_region_blocks_housing(tile):
        return False

    land = getattr(tile, "Land", None)
    land_flags = getattr(land, "Flags", None)

    if land_flags:
        if (
            getattr(land_flags, "IsNoHouse", False)
            or getattr(land_flags, "IsImpassable", False)
            or getattr(land_flags, "IsWet", False)
        ):
            return False

    if tile_land_graphic(tile) in ROAD_GRAPHICS:
        return False

    if tile_has_multi(tile):
        return False

    if tile_has_major_static_blocker(tile):
        return False

    land_z = tile_land_z(tile, player_z)
    if abs(land_z - player_z) > height_tolerance:
        return False

    return True


def classify_tile(tile, player_z, tile_lookup):
    if not tile:
        return "invalid"

    if not getattr(tile, "InMapBounds", True):
        return "invalid"

    if not getattr(tile, "HasLand", False):
        return "invalid"

    if tile_land_graphic(tile) in ROAD_GRAPHICS:
        return "invalid"

    if tile_has_static_impassable(tile):
        return "invalid"

    if tile_has_multi(tile):
        return "invalid"

    land_z = tile_land_z(tile, player_z)
    if abs(land_z - player_z) > height_tolerance:
        return "border"

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        adjacent = tile_lookup.get((tile.X + dx, tile.Y + dy))

        if not adjacent or not getattr(adjacent, "InMapBounds", True):
            return "border"

        if tile_has_multi(adjacent):
            return "border"

        if tile_has_static_impassable(adjacent):
            return "border"

        if getattr(adjacent, "HasLand", False):
            adjacent_z = tile_land_z(adjacent, land_z)
            if abs(adjacent_z - land_z) > height_tolerance:
                return "border"

    return "valid"


def describe_tile_classification(tile, player_z, tile_lookup):
    if not tile:
        return "missing tile data"

    x = getattr(tile, "X", 0)
    y = getattr(tile, "Y", 0)

    if not getattr(tile, "InMapBounds", True):
        return "{0},{1}: outside map bounds".format(x, y)

    if not getattr(tile, "HasLand", False):
        return "{0},{1}: no land tile".format(x, y)

    graphic = tile_land_graphic(tile)
    if graphic in ROAD_GRAPHICS:
        return "{0},{1}: road graphic {2}".format(x, y, graphic)

    if tile_has_static_impassable(tile):
        return "{0},{1}: impassable static".format(x, y)

    if tile_has_multi(tile):
        return "{0},{1}: multi/house component".format(x, y)

    land_z = tile_land_z(tile, player_z)
    if abs(land_z - player_z) > height_tolerance:
        return "{0},{1}: z {2} outside player z {3} +/- {4}".format(x, y, land_z, player_z, height_tolerance)

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        adjacent = tile_lookup.get((x + dx, y + dy))

        if not adjacent or not getattr(adjacent, "InMapBounds", True):
            return "{0},{1}: border, adjacent {2},{3} missing/out of bounds".format(x, y, x + dx, y + dy)

        if tile_has_multi(adjacent):
            return "{0},{1}: border, adjacent {2},{3} has multi".format(x, y, x + dx, y + dy)

        if tile_has_static_impassable(adjacent):
            return "{0},{1}: border, adjacent {2},{3} has impassable static".format(x, y, x + dx, y + dy)

        if getattr(adjacent, "HasLand", False):
            adjacent_z = tile_land_z(adjacent, land_z)
            if abs(adjacent_z - land_z) > height_tolerance:
                return "{0},{1}: border, adjacent {2},{3} z delta {4}".format(x, y, x + dx, y + dy, abs(adjacent_z - land_z))

    return "{0},{1}: valid".format(x, y)


def sample_invalid_footprint_tiles(tile_lookup, player_z, x, y, width, depth, limit=5):
    samples = []

    for tx in range(x, x + width):
        for ty in range(y, y + depth):
            tile = tile_lookup.get((tx, ty))
            if classify_tile(tile, player_z, tile_lookup) != "valid":
                samples.append(describe_tile_classification(tile, player_z, tile_lookup))
                if len(samples) >= limit:
                    return samples

    return samples


def is_clearance_tile_free(tile):
    if not tile:
        return False

    if not getattr(tile, "InMapBounds", True):
        return False

    if not getattr(tile, "HasLand", False):
        return False

    # Existing-house NoHousing regions can overlap the required free rows.
    # For clearance, reject physical blockers but keep NoHousing footprint-only.
    if tile_region_is_guard_zone(tile):
        return False

    if tile_land_graphic(tile) in ROAD_GRAPHICS:
        return False

    if tile_has_multi(tile):
        return False

    if clearance_static_blocker_reason(tile):
        return False

    return True


def describe_clearance_tile(tile):
    if not tile:
        return "missing tile data"

    x = getattr(tile, "X", 0)
    y = getattr(tile, "Y", 0)

    if not getattr(tile, "InMapBounds", True):
        return "{0},{1}: clearance outside map bounds".format(x, y)

    if not getattr(tile, "HasLand", False):
        return "{0},{1}: clearance no land tile".format(x, y)

    if tile_region_is_guard_zone(tile):
        return "{0},{1}: clearance guard zone".format(x, y)

    graphic = tile_land_graphic(tile)
    if graphic in ROAD_GRAPHICS:
        return "{0},{1}: clearance road graphic {2}".format(x, y, graphic)

    if tile_has_multi(tile):
        return "{0},{1}: clearance multi/house component".format(x, y)

    static_reason = clearance_static_blocker_reason(tile)
    if static_reason:
        return "{0},{1}: clearance {2} static".format(x, y, static_reason)

    return "{0},{1}: clearance free".format(x, y)


def sample_invalid_clearance_tiles(tile_lookup, x, y, width, depth, limit=5):
    samples = []

    for name, cx, cy, cwidth, cdepth in clearance_rects(x, y, width, depth):
        for tx in range(cx, cx + cwidth):
            for ty in range(cy, cy + cdepth):
                tile = tile_lookup.get((tx, ty))
                if not is_clearance_tile_free(tile):
                    samples.append("{0}: {1}".format(name, describe_clearance_tile(tile)))
                    if len(samples) >= limit:
                        return samples

    return samples


def run_tile_scan(colors):
    global marked_tiles_global

    player = get_player()
    if not player:
        return

    try:
        px, py, pz = player.X, player.Y, player.Z
        radius = abs(tile_scan_radius)
        x1 = px - radius
        y1 = py - radius
        x2 = px + radius
        y2 = py + radius
        fetch_x1 = x1 - 1
        fetch_y1 = y1 - 1
        fetch_x2 = x2 + 1
        fetch_y2 = y2 + 1
        max_tiles = (radius * 2 + 3) * (radius * 2 + 3)

        API.SysMsg("Scanning tiles around {0},{1},{2} radius={3}...".format(px, py, pz, radius), 88)
        clear_all_markers()

        tiles = API.GetTilesInArea(fetch_x1, fetch_y1, fetch_x2, fetch_y2, max_tiles)
        tile_lookup = {}

        for tile in tiles:
            tile_lookup[(tile.X, tile.Y)] = tile

        valid_points = []
        invalid_points = []
        border_points = []

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                tile = tile_lookup.get((x, y))

                if not tile:
                    invalid_points.append((x, y))
                    continue

                point = (tile.X, tile.Y)
                classification = classify_tile(tile, pz, tile_lookup)

                if classification == "valid":
                    valid_points.append(point)
                elif classification == "border":
                    border_points.append(point)
                else:
                    invalid_points.append(point)

        if valid_points:
            API.MarkTiles(valid_points, colors.get("valid", DEFAULT_COLORS["valid"]))
        if invalid_points:
            API.MarkTiles(invalid_points, colors.get("invalid", DEFAULT_COLORS["invalid"]))
        if border_points:
            API.MarkTiles(border_points, colors.get("border", DEFAULT_COLORS["border"]))

        marked_tiles_global = unique_points(valid_points + invalid_points + border_points)
        schedule_auto_clear(marked_tiles_global[:])

        API.SysMsg("Tile scan complete:", 88)
        API.SysMsg(
            " Valid={0} Invalid={1} Border={2} Total={3}".format(
                len(valid_points),
                len(invalid_points),
                len(border_points),
                len(marked_tiles_global),
            ),
            88,
        )
        API.SysMsg("Use Check 7x7, Best 2-Story, Best 3-Story, or Largest next.", 88)
    except Exception as e:
        API.SysMsg("Error in tile scan: {0}".format(str(e)), 33)


def draw_house_result(result, hue, label):
    if not result or not getattr(result, "Ok", False):
        return False

    width = getattr(result, "Width", 0)
    depth = getattr(result, "Depth", 0)
    if width <= 0 or depth <= 0:
        return False

    x = result.X
    y = result.Y
    API.MarkTileRectangle(x, y, x + width - 1, y + depth - 1, hue, True)
    points = rectangle_border_points(x, y, width, depth)
    track_points(points)
    schedule_auto_clear(points)

    API.SysMsg(
        "{0}: found {1}x{2} at {3},{4}. CheckedTiles={5} TestedPlacements={6}".format(
            label,
            width,
            depth,
            x,
            y,
            getattr(result, "CheckedTiles", 0),
            getattr(result, "TestedPlacements", 0),
        ),
        88,
    )
    return True


def report_failed_house_result(result, label, colors):
    API.SysMsg("{0}: no valid placement found.".format(label), 33)

    if result:
        for reason in result_reasons(result):
            API.SysMsg(" - {0}".format(reason), 33)


def sorted_plot_sizes(sizes):
    return sorted(
        set(sizes),
        key=lambda size: (size[0] * size[1], max(size), min(size), size[0], size[1]),
        reverse=True,
    )


def load_house_search_tiles(player, sizes):
    sizes = sorted_plot_sizes(sizes)
    max_width = max(width for width, _ in sizes)
    max_depth = max(depth for _, depth in sizes)
    radius = abs(house_search_radius)
    clearance_margin = max(front_clearance, back_clearance, side_clearance)
    min_top_left_x = player.X - radius - max_width + 1
    min_top_left_y = player.Y - radius - max_depth + 1
    max_top_left_x = player.X + radius
    max_top_left_y = player.Y + radius

    fetch_x1 = min_top_left_x - clearance_margin - 1
    fetch_y1 = min_top_left_y - clearance_margin - 1
    fetch_x2 = max_top_left_x + max_width + clearance_margin
    fetch_y2 = max_top_left_y + max_depth + clearance_margin
    max_tiles = (fetch_x2 - fetch_x1 + 1) * (fetch_y2 - fetch_y1 + 1)

    tiles = API.GetTilesInArea(fetch_x1, fetch_y1, fetch_x2, fetch_y2, max_tiles)
    tile_lookup = {}

    for tile in tiles:
        tile_lookup[(tile.X, tile.Y)] = tile

    return tile_lookup, min_top_left_x, min_top_left_y, max_top_left_x, max_top_left_y


def build_invalid_prefix(tile_lookup, player_z, min_x, min_y, max_x, max_y):
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    prefix = [[0 for _ in range(height + 1)] for _ in range(width + 1)]

    for ix in range(width):
        x = min_x + ix
        row_total = 0

        for iy in range(height):
            y = min_y + iy
            tile = tile_lookup.get((x, y))
            invalid = 0 if classify_tile(tile, player_z, tile_lookup) == "valid" else 1
            row_total += invalid
            prefix[ix + 1][iy + 1] = prefix[ix][iy + 1] + row_total

    return prefix


def build_clearance_prefix(tile_lookup, min_x, min_y, max_x, max_y):
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    prefix = [[0 for _ in range(height + 1)] for _ in range(width + 1)]

    for ix in range(width):
        x = min_x + ix
        row_total = 0

        for iy in range(height):
            y = min_y + iy
            tile = tile_lookup.get((x, y))
            invalid = 0 if is_clearance_tile_free(tile) else 1
            row_total += invalid
            prefix[ix + 1][iy + 1] = prefix[ix][iy + 1] + row_total

    return prefix


def count_invalid(prefix, min_x, min_y, x, y, width, depth):
    x0 = x - min_x
    y0 = y - min_y
    x1 = x0 + width
    y1 = y0 + depth

    return prefix[x1][y1] - prefix[x0][y1] - prefix[x1][y0] + prefix[x0][y0]


def rect_has_invalid(prefix, min_x, min_y, x, y, width, depth):
    if width <= 0 or depth <= 0:
        return False

    return count_invalid(prefix, min_x, min_y, x, y, width, depth) != 0


def normalized_direction():
    value = (direction or "south").lower()
    if value in ("north", "n"):
        return "north"
    if value in ("east", "e"):
        return "east"
    if value in ("west", "w"):
        return "west"
    return "south"


def clearance_rects(x, y, width, depth):
    facing = normalized_direction()
    front = max(0, front_clearance)
    back = max(0, back_clearance)
    side = max(0, side_clearance)
    rects = []

    if facing == "north":
        rects.append(("front", x, y - front, width, front))
        rects.append(("back", x, y + depth, width, back))
        rects.append(("left", x - side, y, side, depth))
        rects.append(("right", x + width, y, side, depth))
    elif facing == "east":
        rects.append(("front", x + width, y, front, depth))
        rects.append(("back", x - back, y, back, depth))
        rects.append(("left", x, y - side, width, side))
        rects.append(("right", x, y + depth, width, side))
    elif facing == "west":
        rects.append(("front", x - front, y, front, depth))
        rects.append(("back", x + width, y, back, depth))
        rects.append(("left", x, y + depth, width, side))
        rects.append(("right", x, y - side, width, side))
    else:
        rects.append(("front", x, y + depth, width, front))
        rects.append(("back", x, y - back, width, back))
        rects.append(("left", x + width, y, side, depth))
        rects.append(("right", x - side, y, side, depth))

    return rects


def is_flat_footprint(tile_lookup, x, y, width, depth):
    min_z = None
    max_z = None

    for tx in range(x, x + width):
        for ty in range(y, y + depth):
            tile = tile_lookup.get((tx, ty))
            if not tile:
                return False

            z = tile_land_z(tile, None)
            if z is None:
                return False

            min_z = z if min_z is None else min(min_z, z)
            max_z = z if max_z is None else max(max_z, z)

    return min_z is not None and max_z is not None and max_z - min_z <= height_tolerance


def candidate_invalid_counts(footprint_prefix, clearance_prefix, prefix_min_x, prefix_min_y, x, y, width, depth):
    footprint_invalid = count_invalid(footprint_prefix, prefix_min_x, prefix_min_y, x, y, width, depth)
    clearance_invalid = 0

    for _, cx, cy, cwidth, cdepth in clearance_rects(x, y, width, depth):
        clearance_invalid += count_invalid(clearance_prefix, prefix_min_x, prefix_min_y, cx, cy, cwidth, cdepth)

    return footprint_invalid, clearance_invalid


def is_valid_house_candidate(footprint_prefix, clearance_prefix, prefix_min_x, prefix_min_y, x, y, width, depth):
    footprint_invalid, clearance_invalid = candidate_invalid_counts(
        footprint_prefix,
        clearance_prefix,
        prefix_min_x,
        prefix_min_y,
        x,
        y,
        width,
        depth,
    )

    return footprint_invalid == 0 and clearance_invalid == 0


def placement_distance_score(player, x, y, width, depth):
    candidate_center_x2 = x * 2 + width - 1
    candidate_center_y2 = y * 2 + depth - 1
    player_x2 = player.X * 2
    player_y2 = player.Y * 2
    dx = candidate_center_x2 - player_x2
    dy = candidate_center_y2 - player_y2
    return dx * dx + dy * dy


def candidate_top_left_bounds(player, width, depth):
    radius = abs(house_search_radius)
    return (
        player.X - radius - width + 1,
        player.Y - radius - depth + 1,
        player.X + radius,
        player.Y + radius,
    )


def log_near_misses(tile_lookup, player_z, near_misses):
    if not near_misses:
        API.SysMsg("Diagnostics: no candidate footprints were evaluated.", 33)
        return

    API.SysMsg("Diagnostics: closest failed footprints:", 33)

    for index, (invalid_count, footprint_invalid, clearance_invalid, score, x, y, width, depth) in enumerate(near_misses[:3]):
        API.SysMsg(
            " #{0}: {1}x{2} at {3},{4}, invalid={5} footprint={6} clearance={7}, score={8}".format(
                index + 1,
                width,
                depth,
                x,
                y,
                invalid_count,
                footprint_invalid,
                clearance_invalid,
                score,
            ),
            33,
        )

        samples = sample_invalid_footprint_tiles(tile_lookup, player_z, x, y, width, depth, 4)
        for sample in samples:
            API.SysMsg("   footprint {0}".format(sample), 33)

        clearance_samples = sample_invalid_clearance_tiles(tile_lookup, x, y, width, depth, 4)
        for sample in clearance_samples:
            API.SysMsg("   clearance {0}".format(sample), 33)


def find_valid_plot(player, sizes):
    sizes = sorted_plot_sizes(sizes)
    max_width = max(width for width, _ in sizes)
    max_depth = max(depth for _, depth in sizes)
    clearance_margin = max(front_clearance, back_clearance, side_clearance)

    API.SysMsg("Loading house search tiles...", 88)
    tile_lookup, min_top_left_x, min_top_left_y, max_top_left_x, max_top_left_y = load_house_search_tiles(player, sizes)
    API.SysMsg(
        "Search top-left range x={0}..{1}, y={2}..{3}, loaded tiles={4}".format(
            min_top_left_x,
            max_top_left_x,
            min_top_left_y,
            max_top_left_y,
            len(tile_lookup),
        ),
        88,
    )
    prefix_min_x = min_top_left_x - clearance_margin
    prefix_min_y = min_top_left_y - clearance_margin
    prefix_max_x = max_top_left_x + max_width + clearance_margin - 1
    prefix_max_y = max_top_left_y + max_depth + clearance_margin - 1
    API.SysMsg("Classifying house search area...", 88)
    footprint_prefix = build_invalid_prefix(
        tile_lookup,
        player.Z,
        prefix_min_x,
        prefix_min_y,
        prefix_max_x,
        prefix_max_y,
    )
    clearance_prefix = build_clearance_prefix(
        tile_lookup,
        prefix_min_x,
        prefix_min_y,
        prefix_max_x,
        prefix_max_y,
    )
    prefix_width = prefix_max_x - prefix_min_x + 1
    prefix_height = prefix_max_y - prefix_min_y + 1
    prefix_invalid = count_invalid(footprint_prefix, prefix_min_x, prefix_min_y, prefix_min_x, prefix_min_y, prefix_width, prefix_height)
    clearance_invalid_total = count_invalid(clearance_prefix, prefix_min_x, prefix_min_y, prefix_min_x, prefix_min_y, prefix_width, prefix_height)
    API.SysMsg(
        "Search grid {0}x{1}: footprint valid={2}, footprint invalid={3}, clearance blockers={4}".format(
            prefix_width,
            prefix_height,
            prefix_width * prefix_height - prefix_invalid,
            prefix_invalid,
            clearance_invalid_total,
        ),
        88,
    )

    tested = 0
    near_misses = []

    for index, (width, depth) in enumerate(sizes):
        candidate_min_x, candidate_min_y, candidate_max_x, candidate_max_y = candidate_top_left_bounds(player, width, depth)
        best_x = None
        best_y = None
        best_score = None

        if index == 0 or index % 10 == 0:
            API.SysMsg("Checking {0}/{1}: {2}x{3}...".format(index + 1, len(sizes), width, depth), 88)

        size_best_invalid = None
        size_best_x = None
        size_best_y = None

        for x in range(candidate_min_x, candidate_max_x + 1):
            for y in range(candidate_min_y, candidate_max_y + 1):
                tested += 1
                footprint_invalid, clearance_invalid = candidate_invalid_counts(
                    footprint_prefix,
                    clearance_prefix,
                    prefix_min_x,
                    prefix_min_y,
                    x,
                    y,
                    width,
                    depth,
                )
                invalid_count = footprint_invalid + clearance_invalid
                score = placement_distance_score(player, x, y, width, depth)

                if invalid_count != 0:
                    if size_best_invalid is None or invalid_count < size_best_invalid:
                        size_best_invalid = invalid_count
                        size_best_x = x
                        size_best_y = y

                    near_misses.append((invalid_count, footprint_invalid, clearance_invalid, score, x, y, width, depth))
                    near_misses.sort(key=lambda item: (item[0], item[3]))
                    del near_misses[8:]
                    continue

                if best_score is None or score < best_score:
                    best_x = x
                    best_y = y
                    best_score = score

        if best_score is not None:
            return best_x, best_y, width, depth, tested

        if size_best_invalid is not None and (index == 0 or index % 10 == 0 or len(sizes) == 1):
            API.SysMsg(
                "No {0}x{1}: closest failed footprint invalid tiles={2} at {3},{4}".format(
                    width,
                    depth,
                    size_best_invalid,
                    size_best_x,
                    size_best_y,
                ),
                33,
            )

    log_near_misses(tile_lookup, player.Z, near_misses)
    return None, None, 0, 0, tested


def draw_house_border(x, y, width, depth, hue, label, tested):
    API.MarkTileRectangle(x, y, x + width - 1, y + depth - 1, hue, True)
    points = rectangle_border_points(x, y, width, depth)
    track_points(points)
    schedule_auto_clear(points)

    API.SysMsg(
        "{0}: found {1}x{2} at {3},{4}. TestedPlacements={5}".format(
            label,
            width,
            depth,
            x,
            y,
            tested,
        ),
        88,
    )


def plot_sizes_to_string(sizes):
    return ",".join(["{0}x{1}".format(width, depth) for width, depth in sizes])


def log_house_plot_failure(label, result):
    tested = getattr(result, "TestedPlacements", 0)
    reason = getattr(result, "Reason", "")
    API.SysMsg("{0}: no valid placement found. TestedPlacements={1}".format(label, tested), 33)

    if reason:
        API.SysMsg("{0}: {1}".format(label, reason), 33)

    blockers = getattr(result, "Blockers", [])
    count = 0

    for blocker in blockers:
        if count >= 5:
            break

        area = getattr(blocker, "ClearanceArea", "")
        area_text = " {0}".format(area) if area else ""
        graphic = getattr(blocker, "GraphicHex", "")
        name = getattr(blocker, "Name", "")
        detail_parts = []

        if graphic:
            detail_parts.append(graphic)

        if name:
            detail_parts.append(name)

        detail_text = " [{0}]".format(", ".join(detail_parts)) if detail_parts else ""
        API.SysMsg(
            " blocker {0}{1}: {2} at {3},{4}{5}".format(
                getattr(blocker, "Kind", ""),
                area_text,
                getattr(blocker, "Reason", ""),
                getattr(blocker, "X", 0),
                getattr(blocker, "Y", 0),
                detail_text,
            ),
            33,
        )
        count += 1


def find_house_plot(colors, sizes, label, hue_key):
    player = get_player()
    if not player:
        return

    try:
        radius = abs(house_search_radius)
        sizes_text = plot_sizes_to_string(sizes)

        API.SysMsg(
            "Searching {0} near {1},{2} radius={3}...".format(label, player.X, player.Y, radius),
            88,
        )

        result = API.FindHousePlotFromSizes(
            player.X,
            player.Y,
            radius,
            sizes_text,
            direction,
            front_clearance,
            back_clearance,
            side_clearance,
            height_tolerance,
            allow_small_plants,
            include_steps,
        )

        if result and getattr(result, "Ok", False):
            x = result.X
            y = result.Y
            width = result.Width
            depth = result.Depth
            tested = getattr(result, "TestedPlacements", 0)
            hue = colors.get(hue_key, DEFAULT_COLORS.get(hue_key, DEFAULT_COLORS["largest"]))

            if hue_key == "largest" and (width, depth) in ALLOWED_3_STORY_SIZES:
                hue = colors.get("3-story", DEFAULT_COLORS["3-story"])
            elif hue_key == "largest" and (width, depth) == (7, 7):
                hue = colors.get("7x7", DEFAULT_COLORS["7x7"])
            elif hue_key == "largest" and (width, depth) in ALLOWED_2_STORY_SIZES:
                hue = colors.get("2-story", DEFAULT_COLORS["2-story"])

            draw_house_border(x, y, width, depth, hue, label, tested)
        else:
            log_house_plot_failure(label, result)
    except Exception as e:
        API.SysMsg("Error searching {0}: {1}".format(label, str(e)), 33)


def check_house_size(colors, width, depth, size_name):
    find_house_plot(colors, [(width, depth)], size_name, size_name)


def find_best_2_story_plot(colors):
    find_house_plot(colors, ALLOWED_2_STORY_SIZES, "Best 2-Story Plot", "2-story")


def find_best_3_story_plot(colors):
    find_house_plot(colors, ALLOWED_3_STORY_SIZES, "Best 3-Story Plot", "3-story")


def find_largest_house_plot(colors):
    find_house_plot(colors, ALLOWED_PLOT_SIZES, "Largest Custom Plot", "largest")


def start_worker(name, target, *args):
    try:
        API.SysMsg("{0} started.".format(name), 88)
        t = threading.Thread(target=target, args=args)
        t.daemon = True
        t.start()
    except Exception as e:
        API.SysMsg("Error starting {0}: {1}".format(name, str(e)), 33)


def add_label(gump, text, x, y, width, height, size=14, color="#FFFFFF"):
    label = API.CreateGumpTTFLabel(text, size, color, "alagard")
    label.SetRect(x, y, width, height)
    gump.Add(label)
    return label


def add_button(gump, text, x, y, width, height, callback):
    button = API.CreateSimpleButton(text, width, height)
    button.SetRect(x, y, width, height)
    gump.Add(button)
    API.AddControlOnClick(button, callback)
    return button


def show_color_customization_menu():
    colors = ConfigManager.load_colors()

    gump = API.CreateGump(True, True)
    gump.SetRect(200, 200, 520, 620)
    gump.CenterXInViewPort()
    gump.CenterYInViewPort()

    bg = API.CreateGumpColorBox(0.85, "#0a0a0a")
    bg.SetRect(0, 0, 520, 620)
    gump.Add(bg)

    add_label(gump, "House Placement Scanner", 20, 15, 480, 40, 26, "#FFD700")
    add_label(gump, "Custom Plot Mode", 350, 24, 150, 24, 12, "#88FF88")

    add_label(gump, "Scan Options", 30, 70, 450, 30, 18, "#FFD700")

    add_label(gump, "1. Run Tile Scan", 40, 110, 280, 25, 16, "#FFFFFF")
    add_label(gump, "Bulk reads tile info and marks valid, invalid, and border tiles.", 40, 134, 360, 20, 12, "#AAAAAA")
    add_button(gump, "Tile Scan", 370, 108, 120, 35, lambda: start_worker("Tile scan", run_tile_scan, ConfigManager.load_colors()))

    add_label(gump, "2. Check 7x7 Plot", 40, 165, 280, 25, 16, "#FFFFFF")
    add_label(gump, "Checks exactly 7x7.", 40, 189, 360, 20, 12, "#AAAAAA")
    add_button(gump, "Check 7x7", 370, 163, 120, 35, lambda: start_worker("7x7 check", check_house_size, ConfigManager.load_colors(), 7, 7, "7x7"))

    add_label(gump, "3. Best 2-Story Plot", 40, 220, 280, 25, 16, "#FFFFFF")
    add_label(gump, "Checks allowed 2-story sizes, excluding 13x13.", 40, 244, 360, 20, 12, "#AAAAAA")
    add_button(gump, "2-Story", 370, 218, 120, 35, lambda: start_worker("2-story search", find_best_2_story_plot, ConfigManager.load_colors()))

    add_label(gump, "4. Best 3-Story Plot", 40, 275, 280, 25, 16, "#FFFFFF")
    add_label(gump, "Checks width 9..18 and length 14..18 only.", 40, 299, 380, 20, 12, "#AAAAAA")
    add_button(gump, "3-Story", 370, 273, 120, 35, lambda: start_worker("3-story search", find_best_3_story_plot, ConfigManager.load_colors()))

    add_label(gump, "5. Largest Custom Plot", 40, 330, 280, 25, 16, "#FFFFFF")
    add_label(gump, "Searches only the allowed 2-story and 3-story sizes.", 40, 354, 380, 20, 12, "#AAAAAA")
    add_button(gump, "Largest", 370, 328, 120, 35, lambda: start_worker("Largest plot search", find_largest_house_plot, ConfigManager.load_colors()))

    add_label(gump, "Utilities", 30, 400, 450, 30, 18, "#FFD700")
    add_button(gump, "Clear Markers", 40, 437, 170, 35, clear_all_markers)
    add_button(gump, "Customize Colors", 240, 437, 190, 35, lambda: show_manual_color_editor(ConfigManager.load_colors()))

    add_label(gump, "Current Settings", 30, 495, 450, 25, 16, "#FFD700")
    settings = (
        "Tile radius: {0} | House radius: {1} | Z delta: {2}\n"
        "Valid: {3} | Invalid: {4} | Border: {5}\n"
        "7x7: {6} | 2-story: {7} | 3-story: {8} | Largest: {9}"
    ).format(
        tile_scan_radius,
        house_search_radius,
        height_tolerance,
        colors.get("valid", DEFAULT_COLORS["valid"]),
        colors.get("invalid", DEFAULT_COLORS["invalid"]),
        colors.get("border", DEFAULT_COLORS["border"]),
        colors.get("7x7", DEFAULT_COLORS["7x7"]),
        colors.get("2-story", DEFAULT_COLORS["2-story"]),
        colors.get("3-story", DEFAULT_COLORS["3-story"]),
        colors.get("largest", DEFAULT_COLORS["largest"]),
    )
    add_label(gump, settings, 40, 523, 440, 64, 12, "#CCCCCC")

    API.AddGump(gump)


def show_manual_color_editor(colors):
    try:
        gump = API.CreateGump(True, True)
        gump.SetRect(260, 160, 440, 340)
        gump.CenterXInViewPort()
        gump.CenterYInViewPort()

        bg = API.CreateGumpColorBox(0.9, "#101010")
        bg.SetRect(0, 0, 440, 340)
        gump.Add(bg)

        add_label(gump, "Customize Marker Hues", 20, 15, 400, 35, 22, "#FFD700")
        add_label(gump, "Enter UO hue values from 0 to 65535.", 20, 50, 400, 24, 12, "#CCCCCC")

        text_controls = {}
        color_items = [
            ("Valid Tiles", "valid"),
            ("Invalid Tiles", "invalid"),
            ("Border Issues", "border"),
            ("7x7 Plots", "7x7"),
            ("2-Story Plots", "2-story"),
            ("3-Story Plots", "3-story"),
            ("Largest Plot", "largest"),
        ]

        y = 90
        for label, key in color_items:
            add_label(gump, label, 30, y, 220, 24, 14, "#FFFFFF")

            textbox = API.CreateGumpTextBox(str(colors.get(key, DEFAULT_COLORS.get(key, 0))), 100, 25)
            textbox.SetRect(270, y, 100, 25)
            textbox.NumbersOnly = True
            gump.Add(textbox)
            text_controls[key] = textbox
            y += 32

        def on_save():
            try:
                new_colors = {}
                for key, control in text_controls.items():
                    text = control.Text if control.Text else "0"
                    value = int(text)
                    if value < 0 or value > 65535:
                        API.SysMsg("Invalid hue for {0}: {1}".format(key, value), 33)
                        return
                    new_colors[key] = value

                if ConfigManager.save_colors(new_colors):
                    API.SysMsg("Colors saved.", 88)
                    if not gump.IsDisposed:
                        gump.Dispose()
            except Exception as e:
                API.SysMsg("Error saving colors: {0}".format(str(e)), 33)

        def on_cancel():
            try:
                if not gump.IsDisposed:
                    gump.Dispose()
            except Exception:
                pass

        add_button(gump, "Save", 90, 292, 120, 32, on_save)
        add_button(gump, "Cancel", 235, 292, 120, 32, on_cancel)

        API.AddGump(gump)
    except Exception as e:
        API.SysMsg("Error creating color editor: {0}".format(str(e)), 33)


def main():
    try:
        show_color_customization_menu()

        while True:
            try:
                API.ProcessCallbacks()
                time.sleep(0.1)
            except Exception:
                break
    except Exception as e:
        API.SysMsg("Fatal error: {0}".format(str(e)), 33)


main()
