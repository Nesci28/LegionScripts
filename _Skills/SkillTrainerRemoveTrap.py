import json
import os
import time
import traceback
from enum import Enum
from math import sqrt

from Util import Util


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
    Dir.Left: (-1, 0),
}


def direction_to_string(direction):
    if isinstance(direction, Dir):
        return {
            Dir.Up: "U",
            Dir.Right: "R",
            Dir.Down: "D",
            Dir.Left: "L",
        }.get(direction, "?")
    return str(direction)


def direction_list_to_string(directions):
    return "".join([direction_to_string(d) for d in directions])


def direction_string_to_list(path):
    direction_by_letter = {
        "U": Dir.Up,
        "R": Dir.Right,
        "D": Dir.Down,
        "L": Dir.Left,
    }
    return [direction_by_letter[letter] for letter in path if letter in direction_by_letter]


def path_starts_with(path, prefix):
    return len(path) >= len(prefix) and path[: len(prefix)] == prefix


def script_root():
    module_file = globals().get("__file__")
    if module_file:
        return os.path.dirname(os.path.dirname(os.path.abspath(module_file)))

    cwd = os.getcwd()
    if os.path.basename(cwd) == "_Skills":
        return os.path.dirname(cwd)
    return cwd


class RemoveTrap:
    skillName = "Remove Trap"
    trapGraphic = 0xA393
    gumpId = 10000
    codeVersion = "2026-06-13-success-reopen-delay"
    scriptRoot = script_root()
    logFile = os.path.join(scriptRoot, "_Logs", "remove_trap_solver.jsonl")

    @staticmethod
    def _findTrap():
        return API.FindType(RemoveTrap.trapGraphic, API.Backpack)

    @staticmethod
    def validate(skillCap=None):
        errors = []
        if not RemoveTrap._findTrap():
            errors.append("Remove Trap - Missing trap training kit.")
        return errors

    def __init__(self, skillCap, label=None, skillLevelLabel=None, statusCallback=None):
        self.skillCap = skillCap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.statusCallback = statusCallback
        self.total = 0
        self.startTime = time.time()
        self.sessionId = time.strftime("%Y%m%d-%H%M%S")
        self.searchAttemptCount = 0
        self.directionOrders = [(Dir.Right, Dir.Down, Dir.Left, Dir.Up)]
        self.lastSuccessSource = None
        self.moveSettleAttempts = 12
        self.gumpReopenAttempts = 8
        self.openTrapAttempts = 3
        self.openTrapTargetTimeout = 1
        self.openTrapSettleAttempts = 20
        self.openTrapSettleDelay = 0.05
        self.openTrapStableChecks = 2
        self.postSuccessOpenDelay = 2.0
        self.nextOpenAllowedAt = 0
        self.rootClosedRetryAttempts = 3
        self.rootSkillFailRetryAttempts = 8
        self.moveSkillFailRetryAttempts = 4
        self.replayAttempts = 2
        API.SetSkillLock(self.skillName, "up")
        self.ensure_parent_dir(self.logFile)
        self.log_event(
            "session_start",
            logFile=self.logFile,
            skillCap=str(skillCap),
            codeVersion=self.codeVersion,
            moduleFile=globals().get("__file__"),
        )

    def set_status(self, text, hue=1153):
        if self.statusCallback:
            self.statusCallback(text, hue)
        else:
            API.SysMsg(text, hue)

    def ensure_parent_dir(self, path):
        directory = os.path.dirname(path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)

    def log_event(self, event, **details):
        try:
            self.ensure_parent_dir(self.logFile)
            record = {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "session": self.sessionId,
                "event": event,
            }
            record.update(details)
            with open(self.logFile, "a") as f:
                f.write(json.dumps(record, default=str, sort_keys=True) + "\n")
        except Exception:
            pass

    def journal_has(self, text):
        try:
            return bool(API.InJournal(text))
        except Exception:
            return False

    def is_wrong_route_journal(self):
        return self.journal_has("fail to disarm") or self.journal_has("reset it")

    def trap_snapshot(self):
        text = self.get_trap_gump_text()
        journal_success = self.journal_has("successfully disarm")
        journal_failure = self.is_wrong_route_journal()
        return {
            "hasGump": bool(API.HasGump(self.gumpId)),
            "grey": int(sum("9720" in line for line in text.split("\n"))),
            "successText": bool("successfully disarm" in text.lower()),
            "journalSuccess": journal_success,
            "journalFailure": journal_failure,
            "textPreview": text.replace("\n", " | ")[:500],
        }




    def wait_for_stable_trap_gump(self, reason="open_trap"):
        last_grey = None
        stable_checks = 0
        for wait_index in range(self.openTrapSettleAttempts):
            if API.HasGump(self.gumpId):
                grey = self.count_grey_crystals()
                if grey > 0:
                    if grey == last_grey:
                        stable_checks += 1
                    else:
                        last_grey = grey
                        stable_checks = 1
                    if stable_checks >= self.openTrapStableChecks:
                        self.log_event(
                            "gump_stable",
                            reason=reason,
                            grey=grey,
                            waitAttempts=wait_index + 1,
                        )
                        return True
            else:
                last_grey = None
                stable_checks = 0
            API.Pause(self.openTrapSettleDelay)

        self.log_event(
            "gump_stable_timeout",
            reason=reason,
            snapshot=self.trap_snapshot(),
        )
        return API.HasGump(self.gumpId)

    def wait_for_open_cooldown(self):
        remaining = self.nextOpenAllowedAt - time.time()
        if remaining <= 0:
            return

        self.log_event("open_trap_wait_success_cooldown", seconds=round(remaining, 2))
        while time.time() < self.nextOpenAllowedAt:
            API.Pause(min(0.1, self.nextOpenAllowedAt - time.time()))

    def open_trap(self):
        hasGump = API.HasGump(self.gumpId)
        self.log_event("open_trap_start", hasGump=hasGump)
        if hasGump:
            return self.wait_for_stable_trap_gump("already_open")

        trap = self._findTrap()
        if not trap:
            self.set_status("Remove Trap - Missing trap training kit.", 33)
            self.log_event("open_trap_failed_missing_kit", snapshot=self.trap_snapshot())
            API.Stop()
            return False

        for attempt in range(self.openTrapAttempts):
            self.wait_for_open_cooldown()
            API.UseSkill(self.skillName)
            target_ready = API.WaitForTarget("any", self.openTrapTargetTimeout)
            if not target_ready:
                self.log_event(
                    "open_trap_no_target",
                    attempt=attempt + 1,
                    snapshot=self.trap_snapshot(),
                )
                continue
            API.Target(trap.Serial)
            opened = self.wait_for_stable_trap_gump("open_trap")
            hasGump = API.HasGump(self.gumpId)
            self.log_event(
                "open_trap_attempt",
                attempt=attempt + 1,
                hasGump=hasGump,
                opened=opened,
                snapshot=self.trap_snapshot(),
            )
            if opened:
                return True

        return False

    def get_trap_gump_text(self):
        gump = API.GetGump(self.gumpId)
        if not gump:
            return ""
        return gump.PacketGumpText or ""

    def is_success_gump(self):
        return "successfully disarm" in self.get_trap_gump_text().lower()

    def count_grey_crystals(self):
        return sum("9720" in line for line in self.get_trap_gump_text().split("\n"))

    def calculate_trap_size(self):
        return self.count_grey_crystals() + 2

    def reset_trap(self):
        close_attempts = 0
        self.log_event("reset_start", hasGump=API.HasGump(self.gumpId))
        while API.HasGump(self.gumpId) and close_attempts < 5:
            API.CloseGump(self.gumpId)
            API.Pause(0.05)
            close_attempts += 1
        if API.HasGump(self.gumpId):
            self.set_status("Remove Trap - Could not reset trap gump.", 33)
            self.log_event("reset_failed", closeAttempts=close_attempts)
            return False
        opened = self.open_trap()
        self.log_event("reset_done", opened=opened, closeAttempts=close_attempts, snapshot=self.trap_snapshot())
        return opened

    def wait_for_move_result(self, before_count, path_length=0, path_key=""):
        current_count = before_count
        observed_journal_failure = False
        self.lastSuccessSource = None

        def journal_success(source):
            try:
                if not API.InJournal("successfully disarm"):
                    return False
            except Exception:
                return False

            self.lastSuccessSource = source
            return True

        def journal_failure(source):
            nonlocal observed_journal_failure
            if observed_journal_failure or not self.is_wrong_route_journal():
                return False
            self.log_event(
                "move_wrong_route_journal",
                path=path_key,
                length=path_length,
                beforeCount=before_count,
                source=source,
            )
            observed_journal_failure = True
            return True

        for _ in range(self.moveSettleAttempts):
            API.Pause(0.1)
            if self.is_success_gump():
                self.lastSuccessSource = "gump_text"
                return "solved", 0
            if journal_success("journal"):
                return "solved", 0
            if journal_failure("journal"):
                return "wrong_route", current_count

            if not API.HasGump(self.gumpId):
                reopened = False
                for wait_index in range(self.gumpReopenAttempts):
                    API.Pause(0.1)
                    if journal_success("journal_after_close"):
                        return "solved", 0
                    if journal_failure("journal_after_close"):
                        return "wrong_route", current_count
                    if self.is_success_gump():
                        self.lastSuccessSource = "gump_text_after_close"
                        return "solved", 0
                    if API.HasGump(self.gumpId):
                        reopened = True
                        self.log_event(
                            "gump_reopened_after_move",
                            path=path_key,
                            length=path_length,
                            waitAttempts=wait_index + 1,
                            snapshot=self.trap_snapshot(),
                        )
                        break
                if not reopened:
                    return "closed", current_count

            current_count = self.count_grey_crystals()
            if current_count != before_count:
                break

        if current_count < before_count:
            return "advanced", current_count
        if current_count > before_count:
            return "reset", current_count
        return "failed", current_count

    def try_live_move(self, direction, before_count, path, skill_fail_retry_limit=None, root_closed_retry_limit=None):
        path_key = direction_list_to_string(path)
        parent_path = path[:-1]
        last_result = "failed"
        last_count = before_count
        current_before = before_count
        skill_fail_attempts = 0
        closed_attempts = 0
        needs_restore = False

        while True:
            if needs_restore:
                if parent_path:
                    valid, solved, valid_prefix = self.replay_path(parent_path)
                    if solved:
                        return "solved", 0
                    if not valid or len(valid_prefix) != len(parent_path):
                        self.log_event(
                            "move_retry_restore_failed",
                            path=path_key,
                            parentPath=direction_list_to_string(parent_path),
                            validPrefix=direction_list_to_string(valid_prefix),
                            previousResult=last_result,
                        )
                        return last_result, last_count
                else:
                    if not self.reset_trap():
                        self.log_event(
                            "root_move_retry_failed_reset",
                            path=path_key,
                            direction=direction_to_string(direction),
                            previousResult=last_result,
                        )
                        return last_result, last_count

                current_before = self.count_grey_crystals()

            result, current_count = self._try_live_move_once(direction, current_before, path)
            self.log_event(
                "try_live_move_result",
                path=path_key,
                direction=direction_to_string(direction),
                result=result,
                beforeCount=current_before,
                afterCount=current_count,
            )
            if result == "skill_fail":
                skill_fail_attempts += 1
                if skill_fail_retry_limit is None:
                    retry_limit = self.rootSkillFailRetryAttempts if len(path) == 1 else self.moveSkillFailRetryAttempts
                else:
                    retry_limit = skill_fail_retry_limit

                if skill_fail_attempts < retry_limit:
                    gump_still_at_parent = API.HasGump(self.gumpId) and current_count == current_before
                    self.log_event(
                        "move_skill_fail_retry",
                        path=path_key,
                        direction=direction_to_string(direction),
                        attempt=skill_fail_attempts + 1,
                        maxAttempts=retry_limit,
                        previousResult=last_result,
                        willRestore=not gump_still_at_parent,
                        gumpStillAtParent=gump_still_at_parent,
                    )
                    last_result = result
                    last_count = current_count
                    needs_restore = not gump_still_at_parent
                    continue

            if result in ("closed", "failed") and len(path) == 1:
                closed_attempts += 1
                retry_limit = self.rootClosedRetryAttempts if root_closed_retry_limit is None else root_closed_retry_limit
                if closed_attempts < retry_limit:
                    self.log_event(
                        "root_move_retry",
                        path=path_key,
                        direction=direction_to_string(direction),
                        attempt=closed_attempts + 1,
                        maxAttempts=retry_limit,
                        previousResult=result,
                    )
                    last_result = result
                    last_count = current_count
                    needs_restore = True
                    continue

            return result, current_count

    def _try_live_move_once(self, direction, before_count, path):
        path_key = direction_list_to_string(path)
        before_state = self.trap_snapshot()
        self.log_event(
            "move_try",
            path=path_key,
            direction=direction_to_string(direction),
            beforeCount=before_count,
            before=before_state,
        )
        try:
            API.ClearJournal()
        except Exception:
            pass
        API.ReplyGump(direction.value, self.gumpId)
        result, current_count = self.wait_for_move_result(before_count, len(path), path_key)
        after_state = self.trap_snapshot()

        if result == "solved":
            self.set_status(f"Unlocked with {path_key}", 1153)
            self.log_event(
                "move_solved_click",
                path=path_key,
                direction=direction_to_string(direction),
                beforeCount=before_count,
                afterCount=current_count,
                successSource=self.lastSuccessSource,
            )
        elif result == "advanced":
            self.set_status(f"Move ok: {path_key} | grey {before_count}->{current_count}", 1153)
        elif result == "reset":
            self.set_status(f"Move reset: {path_key} | grey {before_count}->{current_count}", 33)
        elif result == "wrong_route":
            self.set_status(f"Wrong route: {path_key}", 33)
        elif result == "skill_fail":
            self.set_status(f"Skill fail; retrying: {path_key}", 33)
        elif result == "closed":
            self.set_status(f"Move closed gump: {path_key}", 33)
        else:
            self.set_status(f"Move failed: {path_key} | grey {before_count}->{current_count}", 33)

        self.log_event(
            "move_result",
            path=path_key,
            direction=direction_to_string(direction),
            result=result,
            successSource=self.lastSuccessSource,
            beforeCount=before_count,
            afterCount=current_count,
            after=after_state,
        )
        return result, current_count

    def replay_path(self, path):
        path_key = direction_list_to_string(path)
        best_prefix = []
        last_result = None
        replay_attempts = self.replayAttempts

        for attempt in range(replay_attempts):
            self.log_event("replay_start", path=path_key, attempt=attempt + 1)
            if not self.reset_trap():
                self.log_event("replay_failed_reset", path=path_key, attempt=attempt + 1)
                return False, False, best_prefix

            last_count = self.count_grey_crystals()
            valid_prefix = []
            for direction in path:
                attempted_path = valid_prefix + [direction]
                result, current_count = self.try_live_move(direction, last_count, attempted_path)
                last_result = result

                if result == "solved":
                    valid_prefix.append(direction)
                    self.log_event(
                        "replay_solved",
                        path=direction_list_to_string(valid_prefix),
                        attempt=attempt + 1,
                        successSource=self.lastSuccessSource,
                        beforeCount=last_count,
                        afterCount=current_count,
                    )
                    return True, True, valid_prefix
                if result != "advanced":
                    if len(valid_prefix) > len(best_prefix):
                        best_prefix = list(valid_prefix)
                    self.log_event(
                        "replay_stopped",
                        path=path_key,
                        validPrefix=direction_list_to_string(valid_prefix),
                        result=result,
                        attempt=attempt + 1,
                    )
                    break

                last_count = current_count
                valid_prefix.append(direction)

            else:
                self.log_event("replay_valid", path=path_key, grey=last_count, attempt=attempt + 1)
                return True, False, valid_prefix

            if last_result not in ("closed", "failed", "skill_fail"):
                return False, False, best_prefix

            self.log_event(
                "replay_retry_unstable",
                path=path_key,
                validPrefix=direction_list_to_string(best_prefix),
                result=last_result,
                attempt=attempt + 1,
            )

        return False, False, best_prefix

    def get_path_state(self, path):
        x, y = 0, 0
        visited = {(0, 0)}
        for direction in path:
            dx, dy = dir_offsets[direction]
            x += dx
            y += dy
            visited.add((x, y))
        return x, y, visited

    def is_end_cell(self, x, y, grid_size):
        return x == grid_size - 1 and y == grid_size - 1



    def solve_trap_dynamic(self, size):
        grid_size = int(size ** 0.5)
        attempt_index = self.searchAttemptCount
        self.searchAttemptCount += 1
        directions = list(self.directionOrders[attempt_index % len(self.directionOrders)])
        max_paths = 20000
        tested_paths = set()
        failed_paths = set()
        attempt_dead = False
        self.log_event(
            "solve_start",
            size=size,
            gridSize=grid_size,
            attempt=attempt_index + 1,
            directionOrder="".join(direction_to_string(direction) for direction in directions),
            knownFailedPaths=len(failed_paths),
            startCell="0,0",
            endCell=f"{grid_size - 1},{grid_size - 1}",
            firstMoves="RD",
            snapshot=self.trap_snapshot(),
        )

        start_path = []
        start_x, start_y, start_visited = self.get_path_state(start_path)
        self.set_status("Starting pathfinder from root.", 1153)

        live_path = []
        live_count = self.count_grey_crystals()

        def restore_state(path):
            nonlocal live_path, live_count

            if live_path == path and API.HasGump(self.gumpId):
                live_count = self.count_grey_crystals()
                self.log_event(
                    "restore_skip_live",
                    path=direction_list_to_string(path),
                    grey=live_count,
                    snapshot=self.trap_snapshot(),
                )
                return True, False

            path_key = direction_list_to_string(path)
            self.log_event(
                "restore_start",
                path=path_key,
                currentLivePath=direction_list_to_string(live_path),
                snapshot=self.trap_snapshot(),
            )
            if path_key:
                self.set_status(f"Restoring prefix: {path_key}", 1153)

            valid, solved, valid_prefix = self.replay_path(path)
            live_path = list(valid_prefix)
            live_count = self.count_grey_crystals() if API.HasGump(self.gumpId) else 0
            self.log_event(
                "restore_result",
                requestedPath=path_key,
                valid=valid,
                solved=solved,
                validPrefix=direction_list_to_string(valid_prefix),
                grey=live_count,
                snapshot=self.trap_snapshot(),
            )

            if solved:
                return True, True

            if not valid or len(valid_prefix) != len(path):
                self.set_status(
                    f"Could not restore prefix: {path_key or '(start)'}",
                    33,
                )
                self.log_event(
                    "restore_failed",
                    requestedPath=path_key,
                    validPrefix=direction_list_to_string(valid_prefix),
                )
                return False, False

            return True, False

        restored, solved = restore_state(start_path)
        if solved:
            return True
        if not restored:
            return False

        def search(x, y, path, visited, current_count):
            nonlocal attempt_dead, live_path, live_count

            if attempt_dead:
                return False

            if self.is_end_cell(x, y, grid_size):
                self.log_event(
                    "search_at_end_without_solution",
                    path=direction_list_to_string(path),
                    grey=current_count,
                )
                return False

            if len(tested_paths) >= max_paths:
                self.set_status("Remove Trap - Search limit reached.", 33)
                return False

            tried_candidate = False
            for direction in directions:
                dx, dy = dir_offsets[direction]
                nx, ny = x + dx, y + dy

                if not (0 <= nx < grid_size and 0 <= ny < grid_size):
                    continue
                if (nx, ny) in visited:
                    continue
                if not path and direction not in (Dir.Right, Dir.Down):
                    continue
                if current_count <= 0 and not self.is_end_cell(nx, ny, grid_size):
                    continue

                new_path = path + [direction]
                path_key = direction_list_to_string(new_path)
                if path_key in failed_paths:
                    continue
                if path_key in tested_paths:
                    continue

                tested_paths.add(path_key)
                tried_candidate = True
                self.log_event(
                    "search_try",
                    tested=len(tested_paths),
                    maxPaths=max_paths,
                    basePath=direction_list_to_string(path),
                    path=path_key,
                    direction=direction_to_string(direction),
                    grey=current_count,
                )
                self.set_status(
                    f"Traverse {len(tested_paths)}/{max_paths}: {path_key}",
                    1153,
                )

                restored, solved = restore_state(path)
                if solved:
                    return True
                if not restored:
                    return False
                current_count = live_count

                result, next_count = self.try_live_move(direction, current_count, new_path)
                self.log_event(
                    "search_move_returned",
                    path=path_key,
                    result=result,
                    beforeCount=current_count,
                    afterCount=next_count,
                    tested=len(tested_paths),
                )
                if result == "wrong_route":
                    live_path = []
                    live_count = next_count
                    failed_paths.add(path_key)
                    self.log_event(
                        "search_wrong_route",
                        path=path_key,
                        grey=next_count,
                        tested=len(tested_paths),
                    )
                    continue

                if result == "solved":
                    live_path = list(new_path)
                    live_count = next_count
                    self.log_event(
                        "search_solved",
                        path=path_key,
                        tested=len(tested_paths),
                        successSource=self.lastSuccessSource,
                        beforeCount=current_count,
                        afterCount=next_count,
                    )
                    return True

                if result != "advanced":
                    if result == "failed":
                        live_path = list(path)
                        live_count = current_count
                    elif result == "closed":
                        live_path = []
                        live_count = next_count
                        failed_paths.add(path_key)
                    elif result == "wrong_route":
                        live_path = []
                        live_count = next_count
                        failed_paths.add(path_key)
                    elif result == "skill_fail":
                        if API.HasGump(self.gumpId) and next_count == current_count:
                            live_path = list(path)
                            live_count = current_count
                        else:
                            live_path = []
                            live_count = next_count
                    else:
                        live_path = []
                        live_count = next_count
                        failed_paths.add(path_key)
                        attempt_dead = True
                    self.log_event(
                        "search_rejected",
                        path=path_key,
                        result=result,
                        grey=next_count,
                        livePath=direction_list_to_string(live_path),
                        attemptDead=attempt_dead,
                        willRestoreParent=result in ("closed", "wrong_route", "skill_fail"),
                    )
                    if attempt_dead:
                        return False
                    continue

                live_path = list(new_path)
                live_count = next_count
                self.log_event(
                    "search_advanced",
                    path=path_key,
                    grey=next_count,
                    tested=len(tested_paths),
                )

                if search(nx, ny, new_path, visited | {(nx, ny)}, next_count):
                    return True

                if attempt_dead:
                    self.log_event(
                        "search_abort_unwind",
                        path=path_key,
                        backTo=direction_list_to_string(path),
                    )
                    return False

                attempt_dead = True
                self.log_event(
                    "search_committed_branch_failed",
                    path=path_key,
                    backTo=direction_list_to_string(path),
                    grey=next_count,
                    tested=len(tested_paths),
                    reason="advanced_moves_are_committed",
                )
                return False

            if not tried_candidate:
                self.log_event(
                    "search_no_candidates",
                    path=direction_list_to_string(path),
                    grey=current_count,
                    failedPaths=len(failed_paths),
                    tested=len(tested_paths),
                )
            return False

        if search(start_x, start_y, start_path, start_visited, live_count):
            self.log_event("solve_success", tested=len(tested_paths))
            return True

        if attempt_dead:
            self.log_event(
                "solve_attempt_dead",
                tested=len(tested_paths),
                knownFailedPaths=len(failed_paths),
                snapshot=self.trap_snapshot(),
            )
            self.set_status("Remove Trap - Attempt reset; starting a fresh trap.", 33)
            return False

        self.set_status("Remove Trap - No valid path found; restarting.", 33)
        self.log_event("solve_failed", tested=len(tested_paths), snapshot=self.trap_snapshot())
        return False

    def trainOnce(self):
        try:
            if not self.reset_trap():
                self.log_event("train_once_failed_reset")
                return False

            size = self.calculate_trap_size()
            side = int(sqrt(size))
            self.log_event("train_once_start", size=size, side=side, snapshot=self.trap_snapshot())
            self.set_status(f"Detected trap size: {side}x{side}", 1153)
            solved = self.solve_trap_dynamic(size)
            self.total += 1
            elapsed = int(time.time() - self.startTime)
            avg = elapsed / self.total if self.total > 0 else 0

            if solved:
                self.set_status(
                    f"Disarmed #{self.total} | Time: {elapsed}s | Avg: {avg:.2f}s",
                    1153,
                )
                self.nextOpenAllowedAt = time.time() + self.postSuccessOpenDelay
            else:
                self.set_status("Failed to solve trap.", 33)
            self.log_event(
                "train_once_done",
                solved=solved,
                total=self.total,
                elapsed=elapsed,
                avg=avg,
                snapshot=self.trap_snapshot(),
            )
            API.Pause(1)
            return solved
        except Exception as exc:
            self.log_event(
                "train_once_exception",
                error=str(exc),
                traceback=traceback.format_exc(),
                snapshot=self.trap_snapshot(),
            )
            self.set_status(f"Remove Trap error: {exc}", 33)
            return False

    def train(self, calculateSkillLabels=None):
        while Util.getSkillInfo(self.skillName)["value"] < self.skillCap:
            self.trainOnce()
            if calculateSkillLabels:
                calculateSkillLabels()
