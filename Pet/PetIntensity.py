import API
import re
import importlib
from decimal import Decimal
import urllib.request
from urllib.parse import urlencode
import os
import json
from datetime import datetime
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump
import Util

importlib.reload(Gump)
importlib.reload(Util)

from Gump import Gump
from Util import Util


class PetIntensity:
    SAVE_FILE = f"{Util.getPlayerName()}_pet_intensity_history.json"
    RATING_COLORS = {
        "below": "#b51d2a",
        "poor": "#d17a22",
        "average": "#d17a22",
        "good": "#36a852",
        "perfect": "#277bd8",
    }

    loreGumpId = 0x1DB
    statRe = re.compile(
        r"<div align=right>(\d+(?:\.\d+)?)(?:/\d+)?%?</div>", re.IGNORECASE
    )
    resistRe = re.compile(
        r"(?:<BASEFONT[^>]*>)?<div align=right>(\d+(?:\.\d+)?)(?:/\d+)?%?</div>",
        re.IGNORECASE,
    )

    cuSidheColors = {
        0: ("Original", "84%"),
        2426: ("Agapite", "2.1%"),
        2218: ("Bronze", "2.1%"),
        1447: ("Copper", "2.1%"),
        2424: ("Dull Copper", "2.1%"),
        2305: ("Grey", "2.1%"),
        1319: ("Echo Blue", "2.1%"),
        2220: ("Valorite Blue", "2.1%"),
        1301: ("Sky Blue", "0.2%"),
        1154: ("Ice Blue", "0.2%"),
        1201: ("Pink", "0.2%"),
        1652: ("Red", "0.2%"),
        1109: ("Black", "0.2%"),
        1153: ("Pure White", "0.2%"),
        1161: ("Blaze", "0.004%"),
    }

    resistTemplates = [
        {"Physical": 80, "Fire": 75, "Cold": 70, "Poison": 70, "Energy": 70},
        {"Physical": 80, "Fire": 80, "Cold": 65, "Poison": 70, "Energy": 70},
        {"Physical": 80, "Fire": 80, "Cold": 70, "Poison": 65, "Energy": 70},
        {"Physical": 80, "Fire": 80, "Cold": 65, "Poison": 65, "Energy": 75},
    ]

    petConfigs = {
        "nightmare": {
            "min": 3951,
            "max": 4254,
            "dmg": 75,
            "magical": 1500,
            "ability": 100,
        },
        "drake": {"min": 2820, "max": 3144, "dmg": 60, "magical": 0, "ability": 100},
        "greater dragon": {
            "min": 6139,
            "max": 9439,
            "dmg": 110,
            "magical": 1500,
            "ability": 200,
            "reduce": True,
        },
        "dragon": {
            "min": 6599,
            "max": 6936,
            "dmg": 75,
            "magical": 1500,
            "ability": 100,
        },
        "giant beetle": {
            "min": 1680,
            "max": 1830,
            "dmg": 70,
            "magical": 0,
            "ability": 0,
        },
        "fire beetle": {
            "min": 1890,
            "max": 1905,
            "dmg": 70,
            "magical": 0,
            "ability": 0,
        },
        "fire steed": {
            "min": 2870,
            "max": 3170,
            "dmg": 80,
            "magical": 0,
            "ability": 100,
        },
        "clydesdale": {"min": 2102, "max": 2818, "dmg": 70, "magical": 0, "ability": 0},
        "cu sidhe": {
            "min": 4624,
            "max": 5261,
            "dmg": 95,
            "magical": 0,
            "ability": 200,
            "reduce": True,
        },
        "high plains boura": {
            "min": 3701,
            "max": 4255,
            "dmg": 80,
            "magical": 0,
            "ability": 100,
        },
        "gaman": {"min": 1495, "max": 2001, "dmg": 40, "magical": 0, "ability": 0},
        "hell hound": {
            "min": 2581,
            "max": 3207,
            "dmg": 60,
            "magical": 1500,
            "ability": 100,
        },
        "hiryu": {"min": 4340, "max": 5272, "dmg": 100, "magical": 0, "ability": 200},
        "ki-rin": {"min": 3774, "max": 4117, "dmg": 75, "magical": 1500, "ability": 0},
        "unicorn": {"min": 3834, "max": 4222, "dmg": 75, "magical": 1500, "ability": 0},
        "lesser hiryu": {
            "min": 2070,
            "max": 2882,
            "dmg": 80,
            "magical": 0,
            "ability": 200,
        },
        "rune beetle": {
            "min": 5111,
            "max": 5760,
            "dmg": 75,
            "magical": 1600,
            "ability": 200,
        },
        "shadowmane": {
            "min": 4248,
            "max": 4248,
            "dmg": 75,
            "magical": 1500,
            "ability": 0,
        },
        "white wyrm": {
            "min": 5097,
            "max": 5760,
            "dmg": 85,
            "magical": 1500,
            "ability": 0,
        },
        "triton": {"min": 3556, "max": 4556, "dmg": 80, "magical": 0, "ability": 100},
        # New Legacy Pets
        "juvenile manticore": {
            "min": 4356,
            "max": 4943,
            "dmg": 90,
            "magical": 0,
            "ability": 0,
        },
        "emberwing": {
            "min": 7133,
            "max": 7118,
            "dmg": 100,
            "magical": 1500,
            "ability": 200,
        },
        "arantress": {
            "min": 5158,
            "max": 5143,
            "dmg": 75,
            "magical": 1600,
            "ability": 0,
        },
        "arctos": {"min": 4358, "max": 4343, "dmg": 75, "magical": 0, "ability": 200},
        "blazetail": {
            "min": 4172,
            "max": 4157,
            "dmg": 80,
            "magical": 0,
            "ability": 200,
        },
        "cinderclaw": {
            "min": 4433,
            "max": 4418,
            "dmg": 75,
            "magical": 0,
            "ability": 200,
        },
        "draalwyrm": {
            "min": 4827,
            "max": 5653,
            "dmg": 80,
            "magical": 0,
            "ability": 100,
        },
        "frostpaw": {"min": 3323, "max": 3332, "dmg": 65, "magical": 0, "ability": 200},
        "ossidrial": {
            "min": 7028,
            "max": 7028,
            "dmg": 85,
            "magical": 1600,
            "ability": 200,
        },
        "pachuxo": {"min": 4208, "max": 4193, "dmg": 75, "magical": 0, "ability": 200},
        "snarltooth": {
            "min": 4373,
            "max": 4358,
            "dmg": 75,
            "magical": 0,
            "ability": 200,
        },
        "thunderhoof": {
            "min": 3682,
            "max": 3667,
            "dmg": 65,
            "magical": 0,
            "ability": 100,
        },
    }

    def __init__(self):
        self.GUMP_WIDTH = 270
        self.GUMP_HEIGHT = 340

        self.gump = Gump(self.GUMP_WIDTH, self.GUMP_HEIGHT, self._onClose, False, gumpId=0xBEE701)
        self._running = True
        self._isTameableIcon = None
        self.state = self._emptyState()
        self.isDrawed = False
        self._historyChartY = None
        self._historyChartX = None
        self._historyChartWidth = None
        self._historyChartHeight = None
        self._resistChartY = None
        self._resistChartX = None
        self._resistChartWidth = None
        self._ratingThresholdTextBox = None
        self.selectedPetKey = "cu sidhe"
        self.petTypeRadios = []

    def _emptyState(self):
        if self._isTameableIcon:
            self._isTameableIcon.Dispose()

        return {
            "petKey": None,
            "stats": [],
            "resists": [],
            "pretame": False,
            "pctValue": 0,
            "pctRating": "0%",
            "intensityValue": 0,
            "oldSlots": "?",
            "newSlots": "?",
            "name": None,
            "undefined": None,
            "isWild": None,
            "cuColor": None,
            "cuRarity": None,
            "cuTemplate": None,
            "cuWebRating": None,
            "isEliteResists": None,
        }

    def _showGump(self):
        self.GUMP_WIDTH = 455
        self.GUMP_HEIGHT = 525
        self.gump = Gump(self.GUMP_WIDTH, self.GUMP_HEIGHT, self._onClose, False, gumpId=0xBEE701)
        self.petTypeRadios = []
        self.metricHighlights = {}
        self.currentHighlights = {}

        self.gump.addTitle("PET INTENSITY CALCULATOR")
        self.gump.addHelpButton(338, 7, self.gump.onClick(lambda: self._help()))

        statPanel = self.gump.addPanel(14, 42, 207, 96, "Stats")
        resistPanel = self.gump.addPanel(234, 42, 207, 96, "Resists")

        self.statLabels = {}
        self._addMetricCells(
            statPanel,
            [["Hits", "Stam", "Mana"], ["Str", "Dex", "Int"]],
            self.statLabels,
        )

        self.resistLabels = {}
        self._addMetricCells(
            resistPanel,
            [["Phys", "Fire", "Cold"], ["Pois", "Ener"]],
            self.resistLabels,
            {
                "Phys": "#d8c6a0",
                "Fire": "#d35c4c",
                "Cold": "#63b9d7",
                "Pois": "#74c95c",
                "Ener": "#b07ad8",
            },
        )

        intensityPanel = self.gump.addPanel(
            14, 152, self.GUMP_WIDTH - 28, 160, "Intensity Distribution"
        )
        self.totalPetLabel = self.gump.addLabel("", 0, 0)
        chart = self.gump.addChartGrid(
            intensityPanel["x"] + 4,
            intensityPanel["y"] + 8,
            intensityPanel["width"] - 8,
            intensityPanel["height"] - 12,
            ["25%", "20%", "15%", "10%", "5%", ""],
            ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90"],
        )
        self._historyChartX = chart["x"]
        self._historyChartWidth = chart["width"]
        self._historyChartY = chart["y"]
        self._historyChartHeight = chart["height"]
        self._drawHistoryIntensityChart()

        resistHistoryPanel = self.gump.addPanel(
            14, 326, self.GUMP_WIDTH - 28, 62, "Elite Resist History"
        )
        self._resistChartX = resistHistoryPanel["x"] + 8
        self._resistChartWidth = resistHistoryPanel["width"] - 16
        self._resistChartY = resistHistoryPanel["y"] + 14
        self._drawHistoryResistChart()

        selectPanel = self.gump.addPanel(14, 402, 198, 88, "Select Pet Type")
        for i, (label, key) in enumerate([("Cu Sidhe", "cu sidhe"), ("Lesser Hiryu", "lesser hiryu")]):
            rowY = selectPanel["y"] + 5 + i * 28
            self.gump.addRow(
                selectPanel["x"] + 2,
                rowY - 3,
                selectPanel["width"] - 4,
                24,
                key == self.selectedPetKey,
            )
            radio = self.gump.addRadio(
                label,
                selectPanel["x"] + 4,
                rowY,
                10,
                key == self.selectedPetKey,
                self.gump.onClick(lambda key=key: self._onPetTypeClicked(key)),
            )
            self.petTypeRadios.append({"key": key, "radio": radio})

        detailsPanel = self.gump.addPanel(226, 402, self.GUMP_WIDTH - 240, 88, "Current Pet")
        self.nameLabel = self.gump.addLabel("No pet analyzed", detailsPanel["x"] + 8, detailsPanel["y"] + 14)
        self.currentHighlights["slots"] = self._addRatingHighlight(detailsPanel["x"] + 4, detailsPanel["y"] + 32, detailsPanel["width"] - 8, 16)
        self.currentHighlights["rating"] = self._addRatingHighlight(detailsPanel["x"] + 4, detailsPanel["y"] + 50, detailsPanel["width"] - 8, 16)
        self.slotLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 32)
        self.ratingLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 50)
        self.templateLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 68)
        self.colorLabel = self.gump.addLabel("", detailsPanel["x"] + 104, detailsPanel["y"] + 70)
        self.webLabel = self.gump.addLabel("", 0, 0)

        self.totalPetLabel.SetX(self.GUMP_WIDTH - 138)
        self.totalPetLabel.SetY(370)

        self.gump.create()

    def _addMetricCells(self, panel, rows, labels, colors=None):
        colors = colors or {}
        cellHeight = 29
        cellWidth = int(panel["width"] / 3)
        for rowIndex, row in enumerate(rows):
            y = panel["y"] + 14 + rowIndex * cellHeight
            self.gump.addColorBox(panel["x"], y, 1, panel["width"], Gump.theme["panelHeaderLine"], 0.22)
            if rowIndex > 0:
                self.gump.addColorBox(panel["x"], y - 1, 1, panel["width"], "#000000", 0.35)
            for colIndex, name in enumerate(row):
                x = panel["x"] + colIndex * cellWidth
                if colIndex > 0:
                    self.gump.addColorBox(x, y, cellHeight, 1, Gump.theme["panelHeaderLine"], 0.25)
                self.metricHighlights[name] = self._addRatingHighlight(x + 2, y + 2, cellWidth - 4, cellHeight - 4)
                labelColor = colors.get(name, "#efe4cd")
                labels[name] = self.gump.addTtfLabel(
                    f"{name}: --",
                    x + 8,
                    y + 4,
                    cellWidth - 10,
                    20,
                    12,
                    labelColor,
                    "left",
                    None,
                )

    def _addRatingHighlight(self, x, y, width, height):
        highlights = {}
        for rating, color in self.RATING_COLORS.items():
            box = self.gump.addColorBox(x, y, height, width, color, 0.34, withTexture=False)
            box.IsVisible = False
            highlights[rating] = box
        return highlights

    def _setRatingHighlight(self, highlights, rating):
        for key, box in highlights.items():
            box.IsVisible = key == rating

    def _ratingColorKey(self, rating):
        if not rating:
            return None
        return rating.lower()

    def _onPetTypeClicked(self, key):
        self.selectedPetKey = key
        for item in self.petTypeRadios:
            item["radio"].IsChecked = item["key"] == key

    def _updateStatsSection(self):
        if not self.state["stats"]:
            for name, lbl in self.statLabels.items():
                lbl.Text = f"{name}: --"
                self._setRatingHighlight(self.metricHighlights.get(name, {}), None)
            return

        names = ["Hits", "Stam", "Mana", "Str", "Dex", "Int"]
        for i, val in enumerate(self.state["stats"]):
            name = names[i]
            self.statLabels[name].Text = f"{name}: {int(val)}"
            self._setRatingHighlight(
                self.metricHighlights.get(name, {}),
                self._ratingColorKey(self._rateMetric(name, val)),
            )

    def _updateResistSection(self):
        if not self.state["resists"]:
            for name, lbl in self.resistLabels.items():
                lbl.Text = f"{name}: --"
                self._setRatingHighlight(self.metricHighlights.get(name, {}), None)
            return

        names = ["Phys", "Fire", "Cold", "Pois", "Ener"]
        for i, val in enumerate(self.state["resists"]):
            name = names[i]
            self.resistLabels[name].Text = f"{name}: {int(val)}"
            self._setRatingHighlight(
                self.metricHighlights.get(name, {}),
                self._ratingColorKey(self._rateMetric(name, val)),
            )

    def _updateGump(self):
        if not self.state["petKey"] and not self.state["undefined"]:
            return

        if self.state["undefined"]:
            self.nameLabel.Text = f"Unsupported: {self.state['undefined']}"
            self.slotLabel.Text = ""
            self.ratingLabel.Text = ""
            self.templateLabel.Text = ""
            return

        self.nameLabel.Text = f"Name:    {self.state['name'].strip()}"
        self.slotLabel.Text = (
            f"Slot:    {self.state['oldSlots']} → {self.state['newSlots']}"
        )
        self.ratingLabel.Text = f"Rating:   {self.state['pctRating']}"
        self._setRatingHighlight(
            self.currentHighlights["slots"],
            self._ratingColorKey(self._rateSlots()),
        )
        self._setRatingHighlight(
            self.currentHighlights["rating"],
            self._ratingColorKey(self._rateIntensity()),
        )
        if self.state["cuColor"]:
            self.colorLabel.Text = (
                f"Color:   {self.state['cuColor']} ({self.state['cuRarity']})"
            )
        else:
            self.colorLabel.Text = ""
        if self.state["cuTemplate"]:
            self.templateLabel.Text = f"Elite:    {self.state['cuTemplate']}"
        else:
            self.templateLabel.Text = f"Elite:    None"
        self._updateStatsSection()
        self._updateResistSection()

    def _normalizedStatValue(self, metric, value):
        if metric not in ["Hits", "Str"]:
            return value
        if self.state["isWild"]:
            return value
        return value * Decimal("2")

    def _rateRange(self, value, minimum, poorMax, averageMax, goodMax, perfectMin=None):
        value = Decimal(value)
        if value < Decimal(str(minimum)):
            return "below"
        if perfectMin is not None and value >= Decimal(str(perfectMin)):
            return "perfect"
        if value <= Decimal(str(poorMax)):
            return "poor"
        if value <= Decimal(str(averageMax)):
            return "average"
        if value <= Decimal(str(goodMax)):
            return "good"
        return "perfect"

    def _rateExactPerfectLowGood(self, value, minimum, perfect, goodMin, averageMin, poorAbove):
        value = Decimal(value)
        if value < Decimal(str(perfect)):
            return "below"
        if value == Decimal(str(perfect)):
            return "perfect"
        if Decimal(str(goodMin)) <= value < Decimal(str(averageMin)):
            return "good"
        if Decimal(str(averageMin)) <= value <= Decimal(str(poorAbove)):
            return "average"
        return "poor"

    def _rateMetric(self, metric, value):
        petKey = self.state["petKey"]
        if not petKey:
            return None

        if metric == "Hits":
            value = self._normalizedStatValue(metric, value)
            if petKey == "cu sidhe":
                return self._rateRange(value, 1010, 1099, 1149, 1199, 1200)
            if petKey == "lesser hiryu":
                return self._rateRange(value, 400, 499, 549, 579, 580)
        if metric == "Str":
            value = self._normalizedStatValue(metric, value)
            if petKey == "cu sidhe":
                return self._rateRange(value, 1200, 1199, 1209, 1219, 1220)
            if petKey == "lesser hiryu":
                return self._rateRange(value, 300, 359, 389, 404, 405)

        if petKey == "cu sidhe":
            rules = {
                "Phys": lambda v: self._rateRange(v, 50, 54, 59, 64, 65),
                "Fire": lambda v: self._rateRange(v, 25, 34, 39, 44, 45),
                "Cold": lambda v: self._rateExactPerfectLowGood(v, 70, 70, 71, 73, 75),
                "Pois": lambda v: self._rateRange(v, 30, 39, 44, 49, 50),
                "Ener": lambda v: self._rateExactPerfectLowGood(v, 70, 70, 71, 73, 75),
            }
            return rules.get(metric, lambda _: None)(value)

        if petKey == "lesser hiryu":
            rules = {
                "Phys": lambda v: self._rateRange(v, 45, 54, 59, 64, 65),
                "Fire": lambda v: self._rateRange(v, 60, 69, 74, 79, 80),
                "Cold": lambda v: self._rateRange(v, 5, 9, 12, 14, 15),
                "Pois": lambda v: self._rateRange(v, 30, 34, 37, 39, 40),
                "Ener": lambda v: self._rateRange(v, 30, 34, 37, 39, 40),
            }
            return rules.get(metric, lambda _: None)(value)

        return None

    def _rateSlots(self):
        petKey = self.state["petKey"]
        try:
            slots = int(self.state["oldSlots"])
        except Exception:
            return None
        if petKey == "cu sidhe":
            if slots < 3:
                return "below"
            if slots == 3:
                return "perfect"
            if slots == 4:
                return "poor"
            return "below"
        if petKey == "lesser hiryu":
            if slots < 1:
                return "below"
            if slots == 1:
                return "perfect"
            if slots == 2:
                return "average"
            return "below"
        return None

    def _rateIntensity(self):
        petKey = self.state["petKey"]
        if petKey == "cu sidhe":
            value = Decimal(str(self.state["pctValue"]))
            return self._rateRange(value, "54.07", "59.99", "64.99", "69.99", "70")
        if petKey == "lesser hiryu":
            value = Decimal(str(self.state["intensityValue"]))
            return self._rateRange(value, 2070, 2399, 2599, 2749, 2750)
        return None

    def _help(self):
        API.SysMsg("Press SHIFT+A to analyze a pet and save history")
        API.SysMsg("Press SHIFT+S to analyze a pet and NOT save history")

    def _evaluatePet(self, isSavingHistory):
        self.state = self._emptyState()

        petSerial = API.RequestTarget()
        if not petSerial:
            return

        pet = API.FindMobile(petSerial)
        if not pet:
            return

        # API.PreTarget(pet.Serial)
        API.UseSkill("Animal Lore")
        API.WaitForTarget()
        API.Target(pet.Serial)
        while not API.GetGump(self.loreGumpId):
            API.Pause(0.1)
        gump = API.GetGump(self.loreGumpId)
        if not gump:
            return

        isWild = API.GumpContains("Wild")
        lines = gump.PacketGumpText.split("\n")
        nmLower = pet.Name.lower()
        API.CloseGump(self.loreGumpId)

        supportedKeys = ["cu sidhe", "lesser hiryu"]
        key = next((k for k in supportedKeys if k in nmLower), None)
        if not key:
            self.state["undefined"] = pet.Name
            return

        self.state["petKey"] = key
        self.state["name"] = pet.Name
        self.state["isWild"] = isWild

        self.state["stats"] = [
            self._matchStat(lines[1]),  # Hits
            self._matchStat(lines[2]),  # Stamina
            self._matchStat(lines[3]),  # Mana
            self._matchStat(lines[4]),  # Strength
            self._matchStat(lines[5]),  # Dexterity
            self._matchStat(lines[6]),  # Intelligence
        ]
        self.state["resists"] = [
            self._matchResist(lines[11]),  # Physical
            self._matchResist(lines[12]),  # Fire
            self._matchResist(lines[13]),  # Cold
            self._matchResist(lines[14]),  # Poison
            self._matchResist(lines[15]),  # Energy
        ]

        slotLine = self._safe(lines, 43)
        m = re.search(r"(\d+)\s*=>\s*(\d+)", slotLine)
        self.state["oldSlots"] = m.group(1) if m else "?"
        self.state["newSlots"] = m.group(2) if m else "?"

        try:
            self._recalculate()
            if "cu sidhe" in nmLower:
                self._analyzeCuSidhe(pet)

            if isSavingHistory:
                self._saveHistory()
                self._drawHistoryIntensityChart()
                self._drawHistoryResistChart()
        except Exception as e:
            API.SysMsg(str(e))

    def _matchStat(self, htmlStr):
        match = re.match(self.statRe, htmlStr)
        if match:
            stat = match.group(1).split("/")[0].strip()
            return Decimal(stat)
        return Decimal("0")

    def _matchResist(self, htmlStr):
        match = re.match(self.resistRe, htmlStr)
        if match:
            stat = match.group(1).split("%")[0].strip()
            return Decimal(stat)
        return Decimal("0")

    def _safe(self, lines, idx):
        return lines[idx] if idx >= 0 and idx < len(lines) else ""

    def _recalculate(self):
        if not self.state["petKey"]:
            return
        cfg = self.petConfigs[self.state["petKey"]]
        s = self.state["stats"][:]
        r = self.state["resists"][:]

        if cfg.get("reduce") and self.state["isWild"]:
            s[0] = Decimal((s[0]) / 2)
            s[1] = Decimal((s[1]) / 2)
            s[3] = Decimal((s[3]) / 2)
            s[4] = Decimal((s[4]) / 2)

        wStats = [
            Decimal("3"),
            Decimal("0.5"),
            Decimal("0.5"),
            Decimal("3"),
            Decimal("0.1"),
            Decimal("0.5"),
        ]
        wResists = [Decimal("3")] * 5

        total = sum(s[i] * wStats[i] for i in range(len(s))) + sum(
            r[j] * wResists[j] for j in range(len(r))
        )
        total += (
            Decimal(cfg.get("dmg", 0))
            + Decimal(cfg.get("magical", 0))
            + Decimal(cfg.get("ability", 0))
        )
        self.state["intensityValue"] = float(total)

        den = Decimal(cfg["max"]) - Decimal(cfg["min"])
        pctValue = (
            ((total - Decimal(cfg["min"])) / den * Decimal(100))
            if den > 0
            else Decimal(0)
        )
        pctValue = max(Decimal(0), min(Decimal(100), pctValue))

        self.state["pctValue"] = float(pctValue)
        self.state["pctRating"] = f"{pctValue:.2f}%"

    def _drawHistoryResistChart(self):
        try:
            chartX = self._resistChartX or 10
            chartY = self._resistChartY
            chartWidth = self._resistChartWidth or self.GUMP_WIDTH - 30
            chartHeight = 20

            # Remove old bars
            if hasattr(self, "resistChartElements"):
                for e in self.resistChartElements:
                    try:
                        e.Destroy()
                    except Exception:
                        pass
            self.resistChartElements = []

            # Load data
            if not os.path.exists(self.SAVE_FILE):
                API.SysMsg("[PetIntensity] No history file found for resist chart.")
                elements = self.gump.createStackedBarChart(
                    chartX, chartY, chartHeight, chartWidth, 0, ""
                )
                for element in elements:
                    self.resistChartElements.append(element)
                return
            with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                return

            total = 0
            elite_count = 0
            for entry in data:
                if "isEliteResists" in entry:
                    val = entry["isEliteResists"]
                    if isinstance(val, bool):
                        total += 1
                        if val:
                            elite_count += 1

            if total == 0:
                API.SysMsg("[PetIntensity] No elite data in history.")
                return

            elitePct = (elite_count / total) * 100
            elements = self.gump.createStackedBarChart(
                chartX, chartY, chartHeight, chartWidth, elitePct, ""
            )
            for element in elements:
                self.resistChartElements.append(element)
        except Exception as e:
            API.SysMsg(f"[PetIntensity] Resist chart error: {e}")

    def _drawHistoryIntensityChart(self):
        try:
            if not os.path.exists(self.SAVE_FILE):
                return
            with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                return

            intensities = [float(e.get("pctValue", 0)) for e in data]
            physList = [
                e["resists"][0] for e in data if "resists" in e and e["resists"]
            ]

            bins = [0] * 10
            physBins = [[] for _ in range(10)]
            for i, val in enumerate(intensities):
                idx = min(9, int(val // 10))
                bins[idx] += 1
                if i < len(physList):
                    physBins[idx].append(physList[i])

            maxCount = max(bins) if any(bins) else 1
            chart_x = self._historyChartX or 10
            chart_y = self._historyChartY
            chart_width = self._historyChartWidth or 350
            chart_height = self._historyChartHeight or 100
            bar_width = int(chart_width / len(bins)) - 2

            if hasattr(self, "chartBars"):
                for b in self.chartBars:
                    try:
                        b.Destroy()
                    except:
                        pass
            self.chartBars = []
            for i, count in enumerate(bins):
                if count <= 0:
                    count = 0.01
                height = max(1, int((count / maxCount) * chart_height))
                x = chart_x + i * (bar_width + 2)
                y = chart_y + (chart_height - height)
                bar = self.gump.addColorBox(x, y, height, bar_width, "#b8b8b8")
                self.chartBars.append(bar)

            self.totalPetLabel.Text = f"Total pets: {len(intensities)}"
        except Exception as e:
            API.SysMsg(f"[PetIntensity] Chart error: {e}")

    def tick(self):
        if self.state["petKey"]:
            self._updateGump()

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        for sub in self.gump.subGumps:
            sub.destroy()
        self.gump.destroy()
        API.Stop()

    def main(self):
        self._showGump()
        API.OnHotKey("SHIFT+A", lambda: self._evaluatePet(True))
        API.OnHotKey("SHIFT+S", lambda: self._evaluatePet(False))

    def _isRunning(self):
        return self._running

    def _analyzeCuSidhe(self, pet):
        petHue = pet.Hue
        colorInfo = self.cuSidheColors.get(
            petHue, ("Unknown Color", "Rarity not listed")
        )
        self.state["cuColor"], self.state["cuRarity"] = colorInfo
        resists = {
            "Physical": self.state["resists"][0],
            "Fire": self.state["resists"][1],
            "Cold": self.state["resists"][2],
            "Poison": self.state["resists"][3],
            "Energy": self.state["resists"][4],
        }
        matched = None
        for i, template in enumerate(self.resistTemplates):
            trained = self._getPossibleTrainedResists(resists.copy(), template)
            if self._isWithinTemplateRange(trained, template):
                matched = f"Template #{i+1} ±5"
                break
        self.state["cuTemplate"] = matched
        self.state["isEliteResists"] = bool(matched)
        if self._isTameableIcon:
            self._isTameableIcon.Dispose()
        icon = "isTameable"
        iconY = 10
        if not self.state["isEliteResists"] or self.state["pctValue"] <= 70:
            icon = "isNotTameable"
            iconY = 30
        self._isTameableIcon = self.gump.addButton("", round(self.GUMP_WIDTH / 2 + 10), iconY, icon)

    def _isWithinTemplateRange(self, trained, target):
        for resist in target:
            if abs(trained[resist] - target[resist]) > 5:
                return False
        return True

    def _getPossibleTrainedResists(self, current, template):
        maxTotal = 365
        totalCurrent = sum(current.values())
        budget = maxTotal - totalCurrent
        trained = current.copy()
        for resist in trained:
            target = min(80, template[resist])
            delta = max(0, target - trained[resist])
            if delta > budget:
                delta = budget
            trained[resist] += delta
            budget -= delta
        return trained

    def _saveHistory(self):
        try:
            data = []
            if os.path.exists(self.SAVE_FILE):
                with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

            def convert(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                if isinstance(obj, list):
                    return [convert(x) for x in obj]
                if isinstance(obj, dict):
                    return {k: convert(v) for k, v in obj.items()}
                return obj

            cleaned_state = convert(self.state)
            now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            entry = {"timestamp": now_str, **cleaned_state}

            data.append(entry)
            with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            API.SysMsg(f"[PetIntensity] History save error: {e}")


petIntensity = PetIntensity()
petIntensity.main()
while petIntensity._isRunning():
    petIntensity.gump.tick()
    petIntensity.gump.tickSubGumps()
    petIntensity.tick()
    API.Pause(0.1)
