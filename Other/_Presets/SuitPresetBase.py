import re


class SuitPresetBase(object):
    key = None
    label = None
    control_key = None
    placeholder = False

    def __init__(self, context):
        self.context = context
        if not self.key:
            raise Exception("Suit preset missing key")
        if not self.label:
            self.label = self.key
        if not self.control_key:
            safe_key = re.sub(r"[^A-Za-z0-9]+", "", self.key)
            self.control_key = "suitPreset{}".format(safe_key)

    def __getattr__(self, name):
        try:
            return self.context[name]
        except KeyError:
            raise AttributeError(name)

    def _set_scan_message(self, message, hue=55, notify=True):
        if notify:
            self._suit_set_msg(message, hue)
        else:
            self._suit_store_msg(message)

    def scan_good_pieces(self, body, required=True, notify=True):
        selected_by_slot, candidates_by_slot, loaded = self._suit_scan_good_pieces(
            body,
            require_exceptional=False,
            require_high_resists=False,
            update_rows=True,
            required=required,
        )
        selected_count = len(selected_by_slot)
        missing_slots = [
            slot_name for slot_name in self.SUIT_BODY_ITEMS.get(body, ())
            if not selected_by_slot.get(slot_name)
        ]
        self.SuitLog("{} scan complete: selected={} loaded={} missing={} counts=[{}]".format(
            self.key,
            selected_count,
            loaded,
            ",".join(missing_slots) if missing_slots else "none",
            self._suit_log_slot_counts(candidates_by_slot),
        ))

        if notify:
            if selected_count and missing_slots:
                self._set_scan_message(
                    "Scan selected {} saved piece{}; missing {} slot{}.".format(
                        selected_count,
                        "" if selected_count == 1 else "s",
                        len(missing_slots),
                        "" if len(missing_slots) == 1 else "s",
                    ),
                    55,
                    notify,
                )
            elif selected_count:
                self._set_scan_message(
                    "Scan selected all {} saved suit pieces.".format(selected_count),
                    69,
                    notify,
                )
            elif loaded:
                self._set_scan_message(
                    "Scanned {} saved piece{}; none matched suit.".format(
                        loaded,
                        "" if loaded == 1 else "s",
                    ),
                    33,
                    notify,
                )
            else:
                self._set_scan_message("No saved suit pieces found in good-piece container.", 33, notify)
            return selected_by_slot, candidates_by_slot, loaded

        if selected_count:
            self._set_scan_message(
                "Selected {} saved good piece{}.".format(
                    selected_count,
                    "" if selected_count == 1 else "s",
                ),
                55,
                notify,
            )
        elif loaded:
            self._set_scan_message(
                "Scanned {} saved piece{}; none selected.".format(
                    loaded,
                    "" if loaded == 1 else "s",
                ),
                55,
                notify,
            )
        else:
            self._set_scan_message("Good-piece container scanned; no matching gear found.", 33, notify)
        return selected_by_slot, candidates_by_slot, loaded

    def craft(self, body):
        self._suit_init_rows(body)
        self.SuitLog("craft suit stopped: placeholder preset {}".format(self.key))
        self._suit_set_msg("{} preset is a placeholder.".format(self.key), 33)
