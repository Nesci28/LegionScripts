try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass

# API is injected by TazUO at runtime; the import above is IDE-only.
import importlib
import re
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump

importlib.reload(Gump)

from Gump import Gump


EQUIPPED_LAYERS = [
    "OneHanded",
    "TwoHanded",
    "Shoes",
    "Pants",
    "Shirt",
    "Helmet",
    "Gloves",
    "Ring",
    "Talisman",
    "Necklace",
    "Hair",
    "Waist",
    "Torso",
    "Bracelet",
    "Face",
    "Beard",
    "Tunic",
    "Earrings",
    "Arms",
    "Cloak",
    "Robe",
    "Skirt",
    "Legs",
]


PROPERTY_ALIASES = {
    "Strength Bonus": ["Strength Bonus"],
    "Dexterity Bonus": ["Dexterity Bonus"],
    "Intelligence Bonus": ["Intelligence Bonus"],
    "Hit Points Increase": ["Hit Point Increase", "Hit Points Increase"],
    "Stamina Increase": ["Stamina Increase"],
    "Mana Increase": ["Mana Increase"],
    "Hit Point Regeneration": ["Hit Point Regeneration", "Hit Points Regeneration"],
    "Stamina Regeneration": ["Stamina Regeneration"],
    "Mana Regeneration": ["Mana Regeneration"],
    "Physical Resist": ["Physical Resist"],
    "Fire Resist": ["Fire Resist"],
    "Cold Resist": ["Cold Resist"],
    "Poison Resist": ["Poison Resist"],
    "Energy Resist": ["Energy Resist"],
    "Damage Eater": ["Damage Eater"],
    "Kinetic Eater": ["Kinetic Eater"],
    "Fire Eater": ["Fire Eater"],
    "Cold Eater": ["Cold Eater"],
    "Poison Eater": ["Poison Eater"],
    "Energy Eater": ["Energy Eater"],
    "Damage Increase": ["Damage Increase"],
    "Defense Chance Increase": ["Defense Chance Increase"],
    "Hit Chance Increase": ["Hit Chance Increase"],
    "Swing Speed Increase": ["Swing Speed Increase"],
    "Lower Mana Cost": ["Lower Mana Cost"],
    "Reflect Physical Damage": ["Reflect Physical Damage"],
    "Enhance Potions": ["Enhance Potions"],
    "Luck": ["Luck"],
}


BOOLEAN_ALIASES = {
    "Medable Armor": ["Mage Armor", "Medable Armor"],
}


CAPS = {
    "Hit Points Increase": 25,
    "Stamina Increase": 25,
    "Mana Increase": 25,
    "Hit Point Regeneration": 18,
    "Stamina Regeneration": 24,
    "Mana Regeneration": 30,
    "Damage Eater": 18,
    "Kinetic Eater": 30,
    "Fire Eater": 30,
    "Cold Eater": 30,
    "Poison Eater": 30,
    "Energy Eater": 30,
    "Damage Increase": 100,
    "Defense Chance Increase": 45,
    "Hit Chance Increase": 45,
    "Swing Speed Increase": 60,
    "Lower Mana Cost": 40,
}


PROPERTY_ICONS = {
    "Strength Bonus": 0x1CE5,
    "Dexterity Bonus": 0x0F7A,
    "Intelligence Bonus": 0x1CF0,
    "Hit Points Increase": 0x0F0B,
    "Stamina Increase": 0x1B17,
    "Mana Increase": 0x0F8D,
    "Hit Point Regeneration": 0x0F0C,
    "Stamina Regeneration": 0x1B17,
    "Mana Regeneration": 0x0F8D,
    "Physical Resist": 0x1B74,
    "Fire Resist": 0x0F8C,
    "Cold Resist": 0x0F11,
    "Poison Resist": 0x0F8A,
    "Energy Resist": 0x0F0D,
    "Damage Eater": 0x0F5E,
    "Kinetic Eater": 0x1B74,
    "Fire Eater": 0x0F8C,
    "Cold Eater": 0x0F11,
    "Poison Eater": 0x0F8A,
    "Energy Eater": 0x0F0D,
    "Damage Increase": 0x0F5E,
    "Defense Chance Increase": 0x1B74,
    "Hit Chance Increase": 0x0F51,
    "Swing Speed Increase": 0x13FF,
    "Lower Mana Cost": 0x0F8D,
    "Medable Armor": 0x1F03,
    "Reflect Physical Damage": 0x1B74,
    "Enhance Potions": 0x0F0E,
    "Luck": 0x0EED,
}


SECTIONS = [
    (
        "Attributes",
        [
            ["Strength Bonus", "Dexterity Bonus", "Intelligence Bonus", "Hit Points Increase", "Stamina Increase"],
            ["Mana Increase", "Hit Point Regeneration", "Stamina Regeneration", "Mana Regeneration"],
        ],
    ),
    (
        "Resistances",
        [
            ["Physical Resist", "Fire Resist", "Cold Resist", "Poison Resist", "Energy Resist"],
            ["Damage Eater", "Kinetic Eater", "Fire Eater", "Cold Eater", "Poison Eater", "Energy Eater"],
        ],
    ),
    (
        "Combat",
        [
            [
                "Damage Increase",
                "Defense Chance Increase",
                "Hit Chance Increase",
                "Swing Speed Increase",
                "Lower Mana Cost",
                "Medable Armor",
                "Reflect Physical Damage",
                "Enhance Potions",
            ],
            ["Luck"],
        ],
    ),
]


def _normalize(text):
    text = re.sub(r"<[^>]*>", "", str(text or ""))
    text = text.replace("\r", " ").replace("\n", " ")
    text = text.replace("'", "")
    text = re.sub(r"[^A-Za-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _build_alias_lookup(alias_map):
    lookup = []
    for prop, aliases in alias_map.items():
        for alias in aliases:
            lookup.append((_normalize(alias), prop))
    lookup.sort(key=lambda item: len(item[0]), reverse=True)
    return lookup


NUMERIC_LOOKUP = _build_alias_lookup(PROPERTY_ALIASES)
BOOLEAN_LOOKUP = _build_alias_lookup(BOOLEAN_ALIASES)


class SuitProperties:
    WIDTH = 640
    HEIGHT = 686
    ROW_HEIGHT = 22
    LABEL_COLOR = "#f0c892"
    VALUE_COLOR = "#b7d9ff"
    ZERO_COLOR = "#7f8790"
    ICON_BACK = "#05181d"

    def __init__(self):
        self._running = True
        self.gump = None
        self.valueLabels = {}
        self.scannedItemsLabel = None
        self.scanMessage = "Ready."
        self.scannedCount = 0
        self.totals = {}
        self.flags = {}

    def main(self):
        try:
            self._scan()
            self._showGump()
        except Exception as e:
            API.SysMsg("Suit Properties error: {}".format(e), 33)
            API.SysMsg(traceback.format_exc(), 33)
            self._onClose()

    def _isRunning(self):
        return self._running

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            self.gump.tick()
            self.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            self.gump.destroy()
            self.gump = None
        API.Stop()

    def _refresh(self):
        self._scan()
        self._updateLabels()

    def _scan(self):
        self.totals = dict((prop, 0) for prop in PROPERTY_ALIASES.keys())
        self.flags = dict((prop, False) for prop in BOOLEAN_ALIASES.keys())
        seen = set()
        scanned = 0

        for layer in EQUIPPED_LAYERS:
            item = self._findLayer(layer)
            if not item:
                continue
            serial = self._serial(item)
            if not serial or serial in seen:
                continue
            seen.add(serial)
            scanned += 1
            self._scanItem(serial)

        self.scannedCount = scanned
        self.scanMessage = "Scanned {} equipped item{}.".format(scanned, "" if scanned == 1 else "s")

    def _findLayer(self, layer):
        try:
            return API.FindLayer(layer)
        except Exception:
            return None

    def _serial(self, item):
        try:
            return int(item.Serial)
        except Exception:
            try:
                return int(item)
            except Exception:
                return 0

    def _scanItem(self, serial):
        try:
            tooltip = API.ItemNameAndProps(serial, True)
        except Exception:
            return

        for raw_line in str(tooltip or "").split("\n"):
            line = raw_line.strip()
            if not line:
                continue
            normalized = _normalize(line)
            if not normalized:
                continue

            for alias, prop in BOOLEAN_LOOKUP:
                if normalized == alias or normalized.startswith(alias + " "):
                    self.flags[prop] = True
                    break

            parsed = self._parseNumericLine(normalized)
            if parsed:
                prop, value = parsed
                self.totals[prop] = self.totals.get(prop, 0) + value

    def _parseNumericLine(self, normalized):
        for alias, prop in NUMERIC_LOOKUP:
            if not (normalized == alias or normalized.startswith(alias + " ")):
                continue

            tail = normalized[len(alias):].strip()
            match = re.search(r"[-+]?\d+", tail)
            if not match:
                return None
            return prop, int(match.group(0))

        return None

    def _showGump(self):
        self.gump = Gump(self.WIDTH, self.HEIGHT, self._onClose, withStatus=False)
        self.gump.addTitle("SUIT PROPERTIES")
        self._drawHeader()
        self._drawSections()
        self._updateLabels()
        self.gump.create()

    def _drawHeader(self):
        self.gump.addColorBox(18, 38, 30, self.WIDTH - 36, Gump.theme["panelHeader"], 0.82, withTexture=True)
        self.gump.addTtfLabel(
            "Equipped suit totals",
            28,
            43,
            230,
            22,
            12,
            Gump.theme["buttonText"],
            "left",
            None,
        )
        self.scannedItemsLabel = self.gump.addTtfLabel(
            "",
            264,
            43,
            260,
            22,
            11,
            self.VALUE_COLOR,
            "left",
            None,
        )
        self.gump.addTextButton(
            "Refresh",
            self.WIDTH - 108,
            42,
            84,
            22,
            self.gump.onClick(self._refresh, "Refreshing suit totals...", "Ready."),
            fontSize=10,
        )

    def _drawSections(self):
        section_y = 78
        section_heights = [152, 194, 228]
        for index, section in enumerate(SECTIONS):
            title, columns = section
            height = section_heights[index]
            panel = self.gump.addSectionPanel(index + 1, title, 16, section_y, self.WIDTH - 32, height)
            self._drawSectionRows(panel, columns)
            section_y += height + 8

    def _drawSectionRows(self, panel, columns):
        content_x = panel["x"] + 10
        content_y = panel["y"] + 26
        col_width = (panel["width"] - 34) // 2
        col_gap = 26
        row_h = self.ROW_HEIGHT

        for col_index, props in enumerate(columns):
            x = content_x + col_index * (col_width + col_gap)
            for row_index, prop in enumerate(props):
                y = content_y + row_index * row_h
                selected = row_index % 2 == 0
                self.gump.addFlatRow(x, y, col_width, row_h, selected)
                self._drawPropIcon(prop, x + 5, y + 2)
                self.gump.addTtfLabel(
                    prop,
                    x + 30,
                    y + 1,
                    col_width - 110,
                    row_h,
                    11,
                    self.LABEL_COLOR,
                    "left",
                    None,
                )
                self.valueLabels[prop] = self.gump.addTtfLabel(
                    "",
                    x + col_width - 78,
                    y + 1,
                    70,
                    row_h,
                    11,
                    self.VALUE_COLOR,
                    "right",
                    None,
                )

    def _drawPropIcon(self, prop, x, y):
        self.gump.addColorBox(x - 2, y - 1, 20, 20, self.ICON_BACK, 0.86, withTexture=False)
        self.gump.addColorBox(x - 2, y - 1, 1, 20, Gump.theme["panelHeaderLine"], 0.42, withTexture=False)
        icon = PROPERTY_ICONS.get(prop)
        if icon:
            self.gump.addItemPic(icon, x, y - 1, 18, 18)

    def _updateLabels(self):
        for prop, label in self.valueLabels.items():
            self._setText(label, self._formatValue(prop))
            self._setHue(label, self._valueHue(prop))

        if self.scannedItemsLabel:
            self._setText(self.scannedItemsLabel, self.scanMessage)

    def _setText(self, control, text):
        if not control:
            return
        text = str(text)
        try:
            if hasattr(control, "SetText"):
                control.SetText(text)
            else:
                control.Text = text
        except Exception:
            try:
                control.Text = text
            except Exception:
                pass

    def _setHue(self, control, hue):
        if not control:
            return
        try:
            control.Hue = hue
        except Exception:
            pass

    def _formatValue(self, prop):
        if prop in self.flags:
            return "Yes" if self.flags.get(prop, False) else "No"

        value = self.totals.get(prop, 0)
        cap = CAPS.get(prop)
        if cap is not None:
            return "{}/{}".format(value, cap)
        return str(value)

    def _valueHue(self, prop):
        if prop in self.flags:
            return Gump.hues["accent"] if self.flags.get(prop, False) else Gump.hues["muted"]

        cap = CAPS.get(prop)
        if cap is not None and self.totals.get(prop, 0) >= cap:
            return Gump.hues["accent"]
        if self.totals.get(prop, 0):
            return Gump.hues["text"]
        return Gump.hues["muted"]


suitProperties = SuitProperties()
suitProperties.main()

while suitProperties._isRunning():
    if not suitProperties.tick():
        break
    API.Pause(0.1)
