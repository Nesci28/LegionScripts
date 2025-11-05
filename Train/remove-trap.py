import API
import time
import random
from enum import Enum
from math import sqrt

class Dir(Enum):
    Invalid = 0
    Up = 1
    Right = 2
    Down = 3
    Left = 4

dir_offsets = {
    Dir.Up: (0, -1),
    Dir.Right: (1, 0),
    Dir.Down: (0, 1),
    Dir.Left: (-1, 0)
}

def direction_to_string(direction):
    if isinstance(direction, Dir):
        return {
            Dir.Up: "U",
            Dir.Right: "R",
            Dir.Down: "D",
            Dir.Left: "L"
        }.get(direction, "?")
    return str(direction)

def direction_list_to_string(directions):
    return "".join([direction_to_string(d) for d in directions])

def save_success_path(path):
    with open("successful_trap_paths.txt", "a") as f:
        f.write(direction_list_to_string(path) + "\n")

def open_trap():
    trap = API.FindType(0xA393, API.Backpack)
    hasGump = API.HasGump(10000)
    while not hasGump:
        API.UseSkill("Remove Trap")
        API.WaitForTarget("any", 3)
        API.Target(trap.Serial)
        API.Pause(1)
        hasGump = API.HasGump(10000)
    return 10000

def count_grey_crystals():
    gump = API.GetGump()
    if not gump:
        return 0
    return sum("9720" in line for line in gump.PacketGumpText.split("\n"))

def calculate_trap_size():
    return count_grey_crystals() + 2

def replay_path(path):
    for direction in path:
        API.ClearJournal()
        API.ReplyGump(direction.value, 10000)
        API.Pause(0.8)
        if not API.HasGump(10000):
            return False
    return True

def solve_trap_dynamic(size):
    grid_size = int(size ** 0.5)
    visited_template = [[False] * grid_size for _ in range(grid_size)]
    max_attempts = 100
    attempts = 0

    while attempts < max_attempts:
        if not API.HasGump(10000):
            try:
                open_trap()
                API.Pause(1)
            except:
                return False

        API.ClearJournal()
        visited = [row[:] for row in visited_template]
        crystal_start = count_grey_crystals()

        def dfs(x, y, path, last_crystal_count):
            visited[y][x] = True
            directions = [Dir.Right, Dir.Down, Dir.Left, Dir.Up]
            random.shuffle(directions)

            for direction in directions:
                dx, dy = dir_offsets[direction]
                nx, ny = x + dx, y + dy

                if not (0 <= nx < grid_size and 0 <= ny < grid_size):
                    continue
                if visited[ny][nx]:
                    continue

                if not API.HasGump(10000):
                    try:
                        open_trap()
                        API.Pause(1)
                        if not replay_path(path):
                            return False
                    except:
                        return False

                new_path = path + [direction]
                msg = "Trying path: " + direction_list_to_string(new_path)
                API.SysMsg(msg, 1153)

                API.ClearJournal()
                before = count_grey_crystals()
                API.ReplyGump(direction.value, 10000)
                API.Pause(0.8)
                after = count_grey_crystals()

                if API.InJournal("successfully disarm"):
                    save_success_path(new_path)
                    return True

                if not API.HasGump(10000):
                    after = before
                    try:
                        open_trap()
                        API.Pause(1)
                        if not replay_path(path):
                            return False
                    except:
                        return False

                if after < before:
                    if dfs(nx, ny, new_path, after):
                        return True

            visited[y][x] = False
            return False

        if dfs(0, 0, [], crystal_start):
            return True
        else:
            API.SysMsg("Retrying trap from beginning...", 33)
            attempts += 1
            API.Pause(1)

    API.SysMsg("Max attempts reached. Could not disarm trap.", 33)
    return False

def run_remove_traps_trainer():
    total = 0
    start_time = time.time()

    while True:
        try:
            open_trap()
        except:
            return

        size = calculate_trap_size()
        s = int(sqrt(size))
        API.SysMsg(f"Detected trap size: {s}x{s}", 1153)

        solved = solve_trap_dynamic(size)
        total += 1
        elapsed = int(time.time() - start_time)
        avg = elapsed / total if total > 0 else 0

        if solved:
            API.SysMsg(f"Disarmed #{total} | Time: {elapsed}s | Avg: {avg:.2f}s", 1153)
        else:
            API.SysMsg("Failed to solve trap.", 33)

        API.Pause(1)

run_remove_traps_trainer()
