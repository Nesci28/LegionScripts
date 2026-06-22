from .SuitPresetBase import SuitPresetBase


class _ResistPlanSuitPreset(SuitPresetBase):
    require_exceptional = True

    def plan_matches(self, plan):
        raise NotImplementedError

    def _plan_counts_text(self, plan):
        counts = self._suit_plan_resist_row_counts(plan)
        return ",".join(str(count) for count in counts)

    def _solve_plan(self, candidates_by_slot):
        return self._suit_solve_mage(
            candidates_by_slot,
            plan_filter=self.plan_matches,
            include_required_rows=False,
            choose_optional=False,
            solve_label=self.label,
        )

    def scan_good_pieces(self, body, required=True, notify=True):
        selected_by_slot, candidates_by_slot, loaded, plan = self._suit_scan_saved_mage_plan(
            body,
            update_rows=True,
            required=required,
            plan_filter=self.plan_matches,
            include_required_rows=False,
            choose_optional=False,
            solve_label=self.label,
            allow_started_mage=False,
        )
        if plan:
            self._set_scan_message(
                "Scan selected {} suit from {} saved piece{}.".format(
                    self.label,
                    loaded,
                    "" if loaded == 1 else "s",
                ),
                69,
                notify,
            )
        elif loaded:
            self._set_scan_message(
                "No {} plan yet; need more matching saved pieces.".format(self.label),
                55,
                notify,
            )
        else:
            self._set_scan_message("No saved {} candidates found.".format(self.label), 33, notify)
        return selected_by_slot, candidates_by_slot, loaded, plan

    def craft(self, body):
        self._suit_get_keep_container(required=True)
        slot_names = list(self._suit_body_items(body))
        candidates_by_slot = dict((slot_name, []) for slot_name in slot_names)
        active_by_slot = dict((slot_name, None) for slot_name in slot_names)
        craft = None
        material = self._suit_current_material()
        self.SuitLog("{} start: material={}".format(self.key, material["key"]))

        loaded = self._suit_load_kept_candidates(
            body,
            candidates_by_slot,
            require_exceptional=self.require_exceptional,
            require_high_resists=True,
            required=False,
            allow_started_mage=False,
        )
        if loaded:
            self._suit_set_msg(
                "Loaded {} saved {} candidate{}.".format(
                    loaded,
                    self.label,
                    "" if loaded == 1 else "s",
                ),
                55,
            )

        self._suit_refresh_active_mage_combo(candidates_by_slot, active_by_slot, slot_names)
        plan = self._solve_plan(candidates_by_slot)
        if plan:
            self._suit_select_plan(plan, active_by_slot)
            self.SuitLog("{} selected saved-only plan rows={}".format(self.key, self._plan_counts_text(plan)))
            self._suit_set_msg("{} suit plan selected from saved pieces.".format(self.label), 69)
            return

        while not plan:
            if self._suit_should_stop():
                self._suit_set_msg("Suit crafting stopped.", 33)
                return

            target_slot, craft_reason = self._suit_choose_next_mage_craft_slot(
                candidates_by_slot,
                active_by_slot,
                slot_names,
            )
            if not target_slot:
                self._suit_set_msg("Could not choose next {} suit slot.".format(self.label), 33)
                return

            self._suit_set_msg(
                "Searching {} suit: crafting {} ({})".format(self.label, target_slot, craft_reason),
                55,
            )
            self._suit_update_slot(target_slot, status="Crafting", plan=craft_reason)

            if craft is None:
                craft = self._suit_get_craft()
                self.SuitLog("{} acquired crafting resource container".format(self.key))

            candidate = self._suit_craft_piece(craft, target_slot, self.require_exceptional)
            if not candidate:
                self._suit_update_slot(target_slot, status="Rejected")
                continue

            high_resists = candidate.get("HighResists", ())
            if len(high_resists) != self.SUIT_HIGH_RESIST_COUNT:
                self.SuitLog("{} reject: high-resist count mismatch {}".format(self.key, self._suit_log_candidate(candidate)))
                self._suit_update_slot(
                    target_slot,
                    candidate["Serial"],
                    "Flat rejected",
                    self._suit_resist_text(candidate["Resists"]),
                    self._suit_high_text(high_resists),
                )
                craft.dispose_item(candidate.get("Item"), self.SUIT_ITEM_DEFS[target_slot])
                continue

            if not self._suit_keep_candidate(candidate):
                self._suit_update_slot(
                    target_slot,
                    candidate["Serial"],
                    "Keep failed",
                    self._suit_resist_text(candidate["Resists"]),
                    self._suit_high_text(high_resists),
                )
                self._suit_set_msg("Could not move {} to good-piece container.".format(target_slot), 33)
                return

            candidates_by_slot[target_slot].append(candidate)
            self._suit_refresh_active_mage_combo(candidates_by_slot, active_by_slot, slot_names)
            plan = self._solve_plan(candidates_by_slot)
            if not plan:
                next_slot, reason = self._suit_choose_next_mage_craft_slot(
                    candidates_by_slot,
                    active_by_slot,
                    slot_names,
                )
                self._suit_set_msg(
                    "No {} plan yet. Next: {} ({})".format(self.label, next_slot or "unknown", reason),
                    55,
                )
                self.Misc.Pause(250)

        self._suit_select_plan(plan, active_by_slot)
        self.SuitLog("{} complete: rows={} plan={}".format(
            self.key,
            self._plan_counts_text(plan),
            " | ".join(self._suit_log_candidate(piece) for piece in plan),
        ))
        self._suit_set_msg("{} suit plan selected and kept.".format(self.label), 69)


class BasicSuitPreset(_ResistPlanSuitPreset):
    key = "Basic"
    label = "Basic"
    control_key = "suitPresetBasic"

    def plan_matches(self, plan):
        counts = self._suit_plan_resist_row_counts(plan)
        return len(counts) == len(plan) and all(count == 2 for count in counts)


class AdvancedSuitPreset(_ResistPlanSuitPreset):
    key = "Advanced"
    label = "Advanced"
    control_key = "suitPresetAdvanced"

    one_row_minimum_by_material = {
        "normal leather": 2,
        "spined leather": 4,
        "horned leather": 6,
        "barbed leather": 6,
    }

    def plan_matches(self, plan):
        counts = self._suit_plan_resist_row_counts(plan)
        material_key = self._suit_current_material()["key"]
        required = self.one_row_minimum_by_material.get(material_key, 2)
        return sum(1 for count in counts if count == 1) >= required


class _LuckSuitPreset(SuitPresetBase):
    require_exceptional = True
    physical_values = ()
    free_physical_plan = "Free Phys+9"

    def _candidate_matches(self, candidate):
        return self._suit_candidate_physical_resist(candidate) in self.physical_values

    def _candidate_sort_key(self, candidate):
        phys = self._suit_candidate_physical_resist(candidate)
        total = sum(candidate.get("Resists", {}).values())
        return phys, -total, candidate.get("Serial", 0)

    def _select_saved_candidates(self, body, update_rows=True, required=False):
        slot_names = list(self._suit_body_items(body))
        candidates_by_slot = dict((slot_name, []) for slot_name in slot_names)
        loaded = self._suit_load_kept_candidates(
            body,
            candidates_by_slot,
            require_exceptional=self.require_exceptional,
            require_high_resists=False,
            required=required,
            allow_started_mage=False,
        )
        selected_by_slot = {}
        for slot_name in slot_names:
            matches = [
                candidate
                for candidate in candidates_by_slot.get(slot_name, [])
                if self._candidate_matches(candidate)
            ]
            if not matches:
                continue
            selected = sorted(matches, key=self._candidate_sort_key)[0]
            selected_by_slot[slot_name] = selected
            if update_rows:
                self._suit_update_slot(
                    slot_name,
                    selected["Serial"],
                    "Saved luck",
                    self._suit_resist_text(selected["Resists"]),
                    self.free_physical_plan,
                )
        return selected_by_slot, candidates_by_slot, loaded

    def scan_good_pieces(self, body, required=True, notify=True):
        selected_by_slot, candidates_by_slot, loaded = self._select_saved_candidates(
            body,
            update_rows=True,
            required=required,
        )
        selected_count = len(selected_by_slot)
        if selected_count:
            self._set_scan_message(
                "Scan selected {} saved {} piece{}.".format(
                    selected_count,
                    self.label,
                    "" if selected_count == 1 else "s",
                ),
                69,
                notify,
            )
        elif loaded:
            self._set_scan_message("No saved {} pieces matched physical rule.".format(self.label), 55, notify)
        else:
            self._set_scan_message("No saved {} candidates found.".format(self.label), 33, notify)
        return selected_by_slot, candidates_by_slot, loaded

    def craft(self, body):
        self._suit_get_keep_container(required=True)
        craft = None
        slot_names = list(self._suit_body_items(body))
        selected_by_slot, candidates_by_slot, loaded = self._select_saved_candidates(
            body,
            update_rows=True,
            required=False,
        )
        self.SuitLog("{} start: loaded={} selected={}".format(self.key, loaded, len(selected_by_slot)))

        for slot_name in slot_names:
            if selected_by_slot.get(slot_name):
                continue
            while not selected_by_slot.get(slot_name):
                if self._suit_should_stop():
                    self._suit_set_msg("Suit crafting stopped.", 33)
                    return
                self._suit_update_slot(slot_name, status="Crafting", plan=self.free_physical_plan)
                if craft is None:
                    craft = self._suit_get_craft()
                    self.SuitLog("{} acquired crafting resource container".format(self.key))
                candidate = self._suit_craft_piece(craft, slot_name, self.require_exceptional)
                if not candidate:
                    self._suit_update_slot(slot_name, status="Rejected")
                    continue

                phys = self._suit_candidate_physical_resist(candidate)
                if not self._candidate_matches(candidate):
                    self.SuitLog("{} reject: phys={} {}".format(self.key, phys, self._suit_log_candidate(candidate)))
                    self._suit_update_slot(
                        slot_name,
                        candidate["Serial"],
                        "Phys {} rejected".format(phys),
                        self._suit_resist_text(candidate["Resists"]),
                        self.free_physical_plan,
                    )
                    craft.dispose_item(candidate.get("Item"), self.SUIT_ITEM_DEFS[slot_name])
                    continue

                if not self._suit_keep_candidate(candidate):
                    self._suit_update_slot(
                        slot_name,
                        candidate["Serial"],
                        "Keep failed",
                        self._suit_resist_text(candidate["Resists"]),
                        self.free_physical_plan,
                    )
                    self._suit_set_msg("Could not move {} to good-piece container.".format(slot_name), 33)
                    return

                candidates_by_slot[slot_name].append(candidate)
                selected_by_slot[slot_name] = candidate
                self._suit_set_selected_item_hue(candidate, "selected-luck")
                self._suit_update_slot(
                    slot_name,
                    candidate["Serial"],
                    "Selected luck",
                    self._suit_resist_text(candidate["Resists"]),
                    self.free_physical_plan,
                )

        self._suit_set_msg("{} pieces selected and kept.".format(self.label), 69)


class LuckBasicSuitPreset(_LuckSuitPreset):
    key = "Luck Basic"
    label = "Luck Basic"
    control_key = "suitPresetLuckBasic"
    physical_values = (2, 3)


class LuckAdvancedSuitPreset(_LuckSuitPreset):
    key = "Luck Advanced"
    label = "Luck Advanced"
    control_key = "suitPresetLuckAdvanced"
    physical_values = (2,)
