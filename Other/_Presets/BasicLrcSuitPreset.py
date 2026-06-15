from .SuitPresetBase import SuitPresetBase


class BasicLrcSuitPreset(SuitPresetBase):
    key = "Basic LRC Training"
    label = "Basic LRC"
    control_key = "suitPresetBasic"

    def rows_for_piece(self):
        return [dict(row) for row in self.SUIT_BASIC_ROWS]

    def craft(self, body):
        craft = None
        plan = []
        self.SuitLog("basic start")
        saved_by_slot, _, loaded = self._suit_scan_good_pieces(
            body,
            require_exceptional=False,
            require_high_resists=False,
            update_rows=True,
            required=False,
        )
        if loaded:
            self._suit_set_msg(
                "Selected {} saved Basic piece{}.".format(
                    len(saved_by_slot),
                    "" if len(saved_by_slot) == 1 else "s",
                ),
                55,
            )
        self.SuitLog("basic saved scan: loaded={} selected={}".format(loaded, len(saved_by_slot)))
        for slot_name in self.SUIT_BODY_ITEMS[body]:
            if self._suit_should_stop():
                self.SuitLog("basic stopped before slot={}".format(slot_name))
                self._suit_set_msg("Suit crafting stopped.", 33)
                return
            saved = saved_by_slot.get(slot_name)
            if saved:
                saved["Rows"] = self.rows_for_piece()
                plan.append(saved)
                self.SuitLog("basic reuse saved: {}".format(self._suit_log_candidate(saved)))
                self._suit_update_slot(
                    slot_name,
                    saved["Serial"],
                    "Chosen: Saved",
                    self._suit_resist_text(saved["Resists"]),
                    self._suit_plan_text(saved["Rows"]),
                )
                continue

            self._suit_update_slot(slot_name, status="Crafting")
            if craft is None:
                craft = self._suit_get_craft()
                self.SuitLog("basic acquired crafting resource container")
            candidate = self._suit_craft_piece(craft, slot_name, False)
            if not candidate:
                self.SuitLog("basic craft failed: slot={}".format(slot_name))
                self._suit_update_slot(slot_name, status="Craft failed")
                self._suit_set_msg("Could not craft {}.".format(slot_name), 33)
                return
            candidate["Rows"] = self.rows_for_piece()
            plan.append(candidate)
            self.SuitLog("basic crafted: {}".format(self._suit_log_candidate(candidate)))
            self._suit_update_slot(
                slot_name,
                candidate["Serial"],
                "Crafted",
                self._suit_resist_text(candidate["Resists"]),
                self._suit_plan_text(candidate["Rows"]),
            )
        if not self._suit_imbue_plan(plan):
            self.SuitLog("basic failed during imbue plan")
            return
        self.SuitLog("basic complete: plan={}".format(" | ".join(self._suit_log_candidate(piece) for piece in plan)))
        self._suit_set_msg("Basic LRC suit complete.", 69)
