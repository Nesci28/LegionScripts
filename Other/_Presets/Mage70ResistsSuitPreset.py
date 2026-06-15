from .SuitPresetBase import SuitPresetBase


class Mage70ResistsSuitPreset(SuitPresetBase):
    key = "Mage 70 Resists"
    label = "Mage 70"
    control_key = "suitPresetMage"

    def scan_good_pieces(self, body, required=True, notify=True):
        selected_by_slot, candidates_by_slot, loaded, plan = self._suit_scan_saved_mage_plan(
            body,
            update_rows=True,
            required=required,
        )
        selected_count = len(selected_by_slot)
        missing_slots = [
            slot_name for slot_name in self.SUIT_BODY_ITEMS.get(body, ())
            if not selected_by_slot.get(slot_name)
        ]
        self.SuitLog("mage scan complete: selected={} loaded={} missing={} counts=[{}]".format(
            selected_count,
            loaded,
            ",".join(missing_slots) if missing_slots else "none",
            self._suit_log_slot_counts(candidates_by_slot),
        ))
        if notify:
            if plan:
                self._set_scan_message(
                    "Scan selected README-valid Mage suit from {} saved piece{}.".format(
                        loaded,
                        "" if loaded == 1 else "s",
                    ),
                    69,
                    notify,
                )
            elif loaded:
                self._set_scan_message(self._suit_mage_incomplete_message(candidates_by_slot, loaded), 55, notify)
            else:
                self._set_scan_message("No saved Mage suit candidates found.", 33, notify)
        else:
            if plan:
                self._set_scan_message(
                    "Selected README-valid Mage suit from {} saved piece{}.".format(
                        loaded,
                        "" if loaded == 1 else "s",
                    ),
                    55,
                    notify,
                )
            elif loaded:
                self._set_scan_message(self._suit_mage_incomplete_message(candidates_by_slot, loaded), 55, notify)
            else:
                self._set_scan_message("Good-piece container scanned; no Mage candidates found.", 33, notify)
        return selected_by_slot, candidates_by_slot, loaded, plan

    def craft(self, body):
        craft = None
        self._suit_get_keep_container(required=True)
        self.SuitLog("mage start: good-piece container present")
        candidates_by_slot = dict((slot_name, []) for slot_name in self.SUIT_BODY_ITEMS[body])
        active_by_slot = dict((slot_name, None) for slot_name in self.SUIT_BODY_ITEMS[body])
        plan = None
        slot_names = list(self.SUIT_BODY_ITEMS[body])
        loaded = self._suit_load_kept_candidates(body, candidates_by_slot)
        self.SuitLog("mage saved scan: loaded={} counts=[{}]".format(loaded, self._suit_log_slot_counts(candidates_by_slot)))
        for slot_name in slot_names:
            active = self._suit_best_candidate(candidates_by_slot.get(slot_name, []))
            if not active:
                self.SuitLog("mage initial active: slot={} none".format(slot_name))
                continue
            active_by_slot[slot_name] = active
            self.SuitLog("mage initial active: slot={} {}".format(slot_name, self._suit_log_candidate(active)))
            self._suit_update_slot(
                slot_name,
                active["Serial"],
                "Saved candidate",
                self._suit_resist_text(active["Resists"]),
                self._suit_high_text(active.get("HighResists", ())),
            )
            if loaded:
                self._suit_set_msg(
                    "Selected {} saved Mage candidate{} from good-piece container.".format(
                        loaded,
                        "" if loaded == 1 else "s",
                    ),
                    55,
                )
        self._suit_refresh_active_mage_combo(candidates_by_slot, active_by_slot, slot_names)
        plan = self._suit_solve_mage(candidates_by_slot)
        if plan:
            self._suit_select_plan(plan, active_by_slot)
            self.SuitLog("mage selected saved-only plan")
            self._suit_set_msg("Selected saved Mage suit pieces from good-piece container.", 69)

        while not plan:
            target_slot, craft_reason = self._suit_choose_next_mage_craft_slot(
                candidates_by_slot,
                active_by_slot,
                slot_names,
            )
            missing_slots = [target_slot] if target_slot else []
            self.SuitLog("mage loop: missing={} active={} counts=[{}]".format(
                ",".join(missing_slots),
                ",".join(slot for slot in slot_names if active_by_slot.get(slot)),
                self._suit_log_slot_counts(candidates_by_slot),
            ))
            self.SuitLog("mage next craft: slot={} reason={}".format(target_slot, craft_reason))
            if not target_slot:
                self._suit_set_msg("Could not choose next Mage suit slot.", 33)
                return
            self._suit_set_msg("Searching Mage suit: crafting {} ({})".format(target_slot, craft_reason), 55)
            for slot_name in missing_slots:
                if self._suit_should_stop():
                    self.SuitLog("mage stopped before slot={}".format(slot_name))
                    self._suit_set_msg("Suit crafting stopped.", 33)
                    return
                self._suit_update_slot(slot_name, status="Crafting", plan=craft_reason)
                if craft is None:
                    craft = self._suit_get_craft()
                    self.SuitLog("mage acquired crafting resource container")
                candidate = self._suit_craft_piece(craft, slot_name, True)
                if not candidate:
                    self.SuitLog("mage craft returned no candidate: slot={}".format(slot_name))
                    self._suit_update_slot(slot_name, status="Rejected")
                    continue

                high_resists = candidate.get("HighResists", ())
                if len(high_resists) != self.SUIT_HIGH_RESIST_COUNT:
                    self.SuitLog("mage reject: high-resist count mismatch {}".format(self._suit_log_candidate(candidate)))
                    self._suit_update_slot(
                        slot_name,
                        candidate["Serial"],
                        "Flat rejected",
                        self._suit_resist_text(candidate["Resists"]),
                        self._suit_high_text(high_resists),
                    )
                    craft.dispose_item(candidate.get("Item"), self.SUIT_ITEM_DEFS[slot_name])
                    continue

                if not self._suit_keep_candidate(candidate):
                    self.SuitLog("mage keep failed: {}".format(self._suit_log_candidate(candidate)))
                    self._suit_update_slot(
                        slot_name,
                        candidate["Serial"],
                        "Keep failed",
                        self._suit_resist_text(candidate["Resists"]),
                        self._suit_high_text(high_resists),
                    )
                    self._suit_set_msg("Could not move {} to good-piece container.".format(slot_name), 33)
                    return

                candidates_by_slot[slot_name].append(candidate)
                self._suit_refresh_active_mage_combo(candidates_by_slot, active_by_slot, slot_names)
                self.SuitLog("mage accept crafted: {}".format(self._suit_log_candidate(candidate)))
                self._suit_update_slot(
                    slot_name,
                    candidate["Serial"],
                    "Good {}".format(len(candidates_by_slot[slot_name])),
                    self._suit_resist_text(candidate["Resists"]),
                    self._suit_high_text(high_resists),
                )
                plan = self._suit_solve_mage(candidates_by_slot)
                if plan:
                    self._suit_select_plan(plan, active_by_slot)
                    self.SuitLog("mage plan found after slot={}".format(slot_name))
                    break

            if plan:
                break

            still_missing = [slot_name for slot_name in slot_names if not active_by_slot.get(slot_name)]
            if still_missing:
                self.SuitLog("mage still missing after pass: {}".format(", ".join(still_missing)))
                self._suit_set_msg("Filling Mage suit slots: {}".format(", ".join(still_missing)), 55)
                self.Misc.Pause(250)
                continue

            plan = self._suit_solve_mage(candidates_by_slot)
            if plan:
                self._suit_select_plan(plan, active_by_slot)
                self.SuitLog("mage plan found before recraft")
                break

            next_slot, reason = self._suit_choose_next_mage_craft_slot(
                candidates_by_slot,
                active_by_slot,
                slot_names,
            )
            self.SuitLog("mage no plan yet: next slot={} reason={}".format(next_slot, reason))
            self._suit_set_msg(
                "No Mage plan yet. Next: {} ({})".format(next_slot or "unknown", reason),
                55,
            )
            self.Misc.Pause(250)
            continue

        if not plan:
            next_slot, reason = self._suit_choose_next_mage_craft_slot(
                candidates_by_slot,
                active_by_slot,
                slot_names,
            )
            self.SuitLog("mage no plan exit: next slot={} reason={}".format(next_slot, reason))
            self._suit_set_msg(
                "No Mage plan yet. Next craft: {} ({})".format(next_slot or "unknown", reason),
                55,
            )
            return

        self._suit_select_plan(plan, active_by_slot)
        if not self._suit_imbue_plan(plan, verify_resist_target=True):
            self.SuitLog("mage failed during imbue plan")
            return
        self.SuitLog("mage complete: plan={}".format(" | ".join(self._suit_log_candidate(piece) for piece in plan)))
        self._suit_set_msg("Mage suit complete.", 69)
