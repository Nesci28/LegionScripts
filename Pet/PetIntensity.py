try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass

# API is injected by TazUO at runtime; the import above is IDE-only.
import re
import importlib
import traceback
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



class PetIntensityProfile:
    key = ""
    displayName = ""
    historySlug = ""
    canSaveHistory = False
    modeLabel = "Pet"

    def __init__(self, owner):
        self.owner = owner

    def calculate(self, state, cfg):
        s = state["stats"][:]
        r = state["resists"][:]

        if cfg.get("reduce") and state["isWild"]:
            s[0] = s[0] / 2
            s[1] = s[1] / 2
            s[3] = s[3] / 2
            s[4] = s[4] / 2

        wStats = [
            Decimal("3"),
            Decimal("0.5"),
            Decimal("0.5"),
            Decimal("3"),
            Decimal("0.1"),
            Decimal("0.5"),
        ]
        wResists = [Decimal("3")] * 5

        total = sum(s[i] * wStats[i] for i in range(6))
        total += sum(r[i] * wResists[i] for i in range(5))
        total += (
            Decimal(cfg.get("dmg", 0))
            + Decimal(cfg.get("magical", 0))
            + Decimal(cfg.get("ability", 0))
        )

        state["intensityValue"] = float(total)
        den = Decimal(cfg["max"]) - Decimal(cfg["min"])
        pctValue = (
            ((total - Decimal(cfg["min"])) / den * Decimal(100))
            if den > 0
            else Decimal(0)
        )
        pctValue = max(Decimal(0), min(Decimal(100), pctValue))
        if self.canSaveHistory:
            state["pctValue"] = float(pctValue)
            state["pctRating"] = f"{pctValue:.2f}%"
            state["trainedIntensityComplete"] = True
        else:
            state["pctValue"] = 0
            state["pctRating"] = "N/A"
            state["trainedIntensityComplete"] = False

    def analyzeDetails(self, state, pet):
        return

    def historyFile(self):
        return f"{Util.getPlayerName()}_pet_intensity_{self.historySlug}_history.json"

    def readHistory(self):
        try:
            path = self.historyFile()
            if not os.path.exists(path):
                return []
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            API.SysMsg(f"[PetIntensity] History read error: {e}")
            return []

    def historyCount(self):
        return len(self.readHistory())

    def saveHistory(self, state):
        if not self.canSaveHistory:
            return
        try:
            data = self.readHistory()

            def convert(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                if isinstance(obj, list):
                    return [convert(x) for x in obj]
                if isinstance(obj, dict):
                    return {k: convert(v) for k, v in obj.items()}
                return obj

            cleaned_state = convert(state)
            now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            entry = {"timestamp": now_str, "profile": self.__class__.__name__, **cleaned_state}
            data.append(entry)
            with open(self.historyFile(), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            API.SysMsg(f"[PetIntensity] History save error: {e}")


class WildCuSidhe(PetIntensityProfile):
    key = "cu sidhe"
    displayName = "Cu Sidhe"
    historySlug = "wild_cu_sidhe"
    canSaveHistory = True
    modeLabel = "Wild"

    def analyzeDetails(self, state, pet):
        petHue = pet.Hue
        colorInfo = self.owner.cuSidheColors.get(
            petHue, ("Unknown Color", "Rarity not listed")
        )
        state["cuColor"], state["cuRarity"] = colorInfo
        resists = {
            "Physical": state["resists"][0],
            "Fire": state["resists"][1],
            "Cold": state["resists"][2],
            "Poison": state["resists"][3],
            "Energy": state["resists"][4],
        }
        matched = None
        for i, template in enumerate(self.owner.resistTemplates):
            trained = self.owner._getPossibleTrainedResists(resists.copy(), template)
            if self.owner._isWithinTemplateRange(trained, template):
                matched = f"Template #{i + 1} +/-5"
                break
        state["cuTemplate"] = matched
        state["isEliteResists"] = bool(matched)
        self.owner._setTameableIcon(state["isEliteResists"] and state["pctValue"] > 70)


class TamedCuSidhe(WildCuSidhe):
    historySlug = "tamed_cu_sidhe"
    canSaveHistory = False
    modeLabel = "Tamed"


class WildLesserHiryu(PetIntensityProfile):
    key = "lesser hiryu"
    displayName = "Lesser Hiryu"
    historySlug = "wild_lesser_hiryu"
    canSaveHistory = True
    modeLabel = "Wild"


class TamedLesserHiryu(WildLesserHiryu):
    historySlug = "tamed_lesser_hiryu"
    canSaveHistory = False
    modeLabel = "Tamed"


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
    mobileGraphicPetKeys = {
        0x0115: "cu sidhe",
        0x00F3: "lesser hiryu",
    }
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
            "reduce": True,
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
        self.petClasses = self._createPetClasses()
        self.currentPetClass = self._petClassFor(self.selectedPetKey, True)
        self.petTypeRadios = []

    def _createPetClasses(self):
        return {
            "cu sidhe": {
                True: WildCuSidhe(self),
                False: TamedCuSidhe(self),
            },
            "lesser hiryu": {
                True: WildLesserHiryu(self),
                False: TamedLesserHiryu(self),
            },
        }

    def _petClassFor(self, key, isWild=True):
        return self.petClasses.get(key, {}).get(bool(isWild))

    def _historyPetClass(self):
        return self._petClassFor(self.selectedPetKey, True)

    def _setTameableIcon(self, isTameable):
        if self._isTameableIcon:
            self._isTameableIcon.Dispose()
        icon = "isTameable"
        iconY = 10
        if not isTameable:
            icon = "isNotTameable"
            iconY = 30
        self._isTameableIcon = self.gump.addButton("", round(self.GUMP_WIDTH / 2 + 10), iconY, icon)

    def _emptyState(self):
        return {
            "petKey": None,
            "profile": None,
            "name": "",
            "stats": [],
            "resists": [],
            "isWild": False,
            "pretame": False,
            "pctValue": 0,
            "pctRating": "0%",
            "intensityValue": 0,
            "trainedIntensityComplete": False,
            "oldSlots": 0,
            "newSlots": 0,
            "cuColor": "",
            "cuRarity": "",
            "cuTemplate": "",
            "isEliteResists": False,
            "undefined": None,
        }

    def _showGump(self):
        self.GUMP_WIDTH = 475
        self.GUMP_HEIGHT = 735
        self.gump = Gump(self.GUMP_WIDTH, self.GUMP_HEIGHT, self._onClose, False, gumpId=0xBEE701)
        self.petTypeRadios = []
        self.metricHighlights = {}
        self.currentHighlights = {}

        self.gump.addTitle("PET INTENSITY CALCULATOR")
        self.gump.addHelpButton(self.GUMP_WIDTH - 120, 7, self.gump.onClick(lambda: self._help()))

        statPanel = self.gump.addPanel(14, 42, 217, 112, "Stats")
        resistPanel = self.gump.addPanel(244, 42, 217, 112, "Resists")

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
            14, 168, self.GUMP_WIDTH - 28, 166, "Intensity Distribution"
        )
        self.totalPetLabel = self.gump.addLabel("", 0, 0)
        chart = self.gump.addChartGrid(
            intensityPanel["x"] + 10,
            intensityPanel["y"] + 12,
            intensityPanel["width"] - 22,
            intensityPanel["height"] - 26,
            ["25%", "20%", "15%", "10%", "5%", ""],
            ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90"],
        )
        self._historyChartX = chart["x"]
        self._historyChartWidth = chart["width"]
        self._historyChartY = chart["y"]
        self._historyChartHeight = chart["height"]
        self._drawHistoryIntensityChart()

        resistHistoryPanel = self.gump.addPanel(
            14, 350, self.GUMP_WIDTH - 28, 78, "Elite Resist History"
        )
        self._resistChartX = resistHistoryPanel["x"] + 16
        self._resistChartWidth = resistHistoryPanel["width"] - 32
        self._resistChartY = resistHistoryPanel["y"] + 42
        self._drawHistoryResistChart()

        selectPanel = self.gump.addPanel(14, 444, 208, 132, "Select Pet Type")
        for i, (label, key) in enumerate([("Cu Sidhe", "cu sidhe"), ("Lesser Hiryu", "lesser hiryu")]):
            rowY = selectPanel["y"] + 20 + i * 32
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

        detailsPanel = self.gump.addPanel(236, 444, self.GUMP_WIDTH - 250, 132, "Current Pet")
        self.nameLabel = self.gump.addLabel("No pet analyzed", detailsPanel["x"] + 8, detailsPanel["y"] + 4)
        self.currentHighlights["slots"] = self._addRatingHighlight(detailsPanel["x"] + 4, detailsPanel["y"] + 22, detailsPanel["width"] - 8, 16)
        self.currentHighlights["rating"] = self._addRatingHighlight(detailsPanel["x"] + 4, detailsPanel["y"] + 40, detailsPanel["width"] - 8, 16)
        self.slotLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 22)
        self.ratingLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 40)
        self.intensityLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 58)
        self.templateLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 76)
        self.colorLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 94)
        self.rarityLabel = self.gump.addLabel("", detailsPanel["x"] + 8, detailsPanel["y"] + 112)

        decisionPanel = self.gump.addPanel(14, 588, self.GUMP_WIDTH - 28, 96, "Final Decision")
        self.currentHighlights["decision"] = self._addRatingHighlight(decisionPanel["x"] + 4, decisionPanel["y"] + 34, decisionPanel["width"] - 8, 24)
        self.finalDecisionLabel = self.gump.addTtfLabel(
            "Scan a pet to evaluate taming value.",
            decisionPanel["x"] + 16,
            decisionPanel["y"] + 40,
            decisionPanel["width"] - 32,
            26,
            13,
            "#efe4cd",
            "center",
            None,
        )
        self.finalDecisionDetailLabel = self.gump.addTtfLabel(
            "",
            decisionPanel["x"] + 16,
            decisionPanel["y"] + 70,
            decisionPanel["width"] - 32,
            18,
            11,
            "#d8c6a0",
            "center",
            None,
        )
        self.webLabel = self.gump.addLabel("", 0, 0)

        self.totalPetLabel.SetX(self.GUMP_WIDTH - 150)
        self.totalPetLabel.SetY(408)

        self.gump.create()

    def _addMetricCells(self, panel, rows, labels, colors=None):
        colors = colors or {}
        cellWidth = 62
        cellHeight = 22
        cellGap = 5
        rowGap = 12
        totalHeight = len(rows) * cellHeight + (len(rows) - 1) * rowGap
        startY = panel["y"] + 26 + max(0, (panel["height"] - 38 - totalHeight) // 2)

        for rowIndex, row in enumerate(rows):
            rowWidth = len(row) * cellWidth + (len(row) - 1) * cellGap
            x = panel["x"] + (panel["width"] - rowWidth) // 2
            y = startY + rowIndex * (cellHeight + rowGap)
            for name in row:
                self.metricHighlights[name] = self._addRatingHighlight(x, y, cellWidth, cellHeight)
                labelColor = colors.get(name, "#efe4cd")
                labels[name] = self.gump.addTtfLabel(
                    f"{name}: --",
                    x + 2,
                    y,
                    cellWidth - 4,
                    cellHeight,
                    12,
                    labelColor,
                    "center",
                    None,
                )
                x += cellWidth + cellGap

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
        self.currentPetClass = self._petClassFor(key, True)
        self._drawHistoryIntensityChart()
        self._drawHistoryResistChart()
        self._updateGump()

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
        self._updateStatsSection()
        self._updateResistSection()

        if not self.state["petKey"] and not self.state["undefined"]:
            self.nameLabel.Text = "No pet analyzed"
            self.slotLabel.Text = "Slot: -"
            self.ratingLabel.Text = "Rating: -"
            self.intensityLabel.Text = "Intensity: -"
            self.templateLabel.Text = "Elite: -"
            self.colorLabel.Text = "Color: -"
            self.rarityLabel.Text = "Rarity: -"
            self.totalPetLabel.Text = f"Total pets: {self._historyCount()}"
            self.finalDecisionLabel.Text = "Scan a pet to evaluate taming value."
            self.finalDecisionDetailLabel.Text = ""
            self._setRatingHighlight(self.currentHighlights.get("slots", {}), None)
            self._setRatingHighlight(self.currentHighlights.get("rating", {}), None)
            self._setRatingHighlight(self.currentHighlights.get("decision", {}), None)
            return

        if self.state["undefined"]:
            self.nameLabel.Text = f"Unsupported: {self.state['undefined']}"
            self.slotLabel.Text = "Slot: -"
            self.ratingLabel.Text = "Rating: -"
            self.intensityLabel.Text = "Intensity: -"
            self.templateLabel.Text = "Elite: -"
            self.colorLabel.Text = "Color: -"
            self.rarityLabel.Text = "Rarity: -"
            self.totalPetLabel.Text = f"Total pets: {self._historyCount()}"
            self.finalDecisionLabel.Text = "Not worth taming for this tool."
            self.finalDecisionDetailLabel.Text = "This pet type is not supported by the calculator."
            self._setRatingHighlight(self.currentHighlights.get("slots", {}), None)
            self._setRatingHighlight(self.currentHighlights.get("rating", {}), None)
            self._setRatingHighlight(self.currentHighlights.get("decision", {}), "below")
            return

        mode = "Wild" if self.state["isWild"] else "Tamed"
        self.nameLabel.Text = f"{mode}: {self.state['name']}"
        if self.state["isWild"]:
            self.slotLabel.Text = f"Slot: {self.state['oldSlots']} -> {self.state['newSlots']}"
        else:
            self.slotLabel.Text = "Slot: N/A"
        self.ratingLabel.Text = f"Rating: {self.state['pctRating']}"
        self.intensityLabel.Text = f"Intensity: {self.state['intensityValue']:.1f}"
        if self.state["petKey"] == "cu sidhe":
            if self.state["isWild"]:
                self.templateLabel.Text = f"Elite: {self.state['cuTemplate'] or 'No elite template'}"
                self.colorLabel.Text = f"Color: {self.state['cuColor']}"
                self.rarityLabel.Text = f"Rarity: {self.state['cuRarity']}"
            else:
                self.templateLabel.Text = f"Color: {self.state['cuColor']}"
                self.colorLabel.Text = f"Rarity: {self.state['cuRarity']}"
                self.rarityLabel.Text = ""
        else:
            self.templateLabel.Text = "Elite: N/A"
            self.colorLabel.Text = "Color: N/A"
            self.rarityLabel.Text = "Rarity: N/A"

        self.totalPetLabel.Text = f"Total pets: {self._historyCount()}"
        isWorth = self._isWorthTaming()
        if not self.state["isWild"]:
            self.finalDecisionLabel.Text = "Tamed pet info"
        else:
            self.finalDecisionLabel.Text = "Worth taming" if isWorth else "Not worth taming"
        self.finalDecisionDetailLabel.Text = self._decisionReason(isWorth)
        self._setRatingHighlight(
            self.currentHighlights.get("rating", {}),
            self._ratingColorKey(self._rateIntensity()),
        )
        self._setRatingHighlight(
            self.currentHighlights.get("slots", {}),
            self._ratingColorKey(self._rateSlots()) if self.state["isWild"] else None,
        )
        self._setRatingHighlight(
            self.currentHighlights.get("decision", {}),
            ("perfect" if isWorth else "below") if self.state["isWild"] else None,
        )

    def _isWorthTaming(self):
        if not self.state["petKey"] or not self.state["isWild"]:
            return False
        if Decimal(str(self.state["pctValue"])) < Decimal("70"):
            return False
        if self.state["petKey"] == "cu sidhe" and not self.state["isEliteResists"]:
            return False
        return True

    def _decisionReason(self, isWorth):
        petKey = self.state["petKey"]
        if not self.state["isWild"]:
            return "Tamed calculator needs trained skills, regens, damage, and abilities."
        if isWorth:
            if petKey == "cu sidhe":
                return "70%+ intensity with elite resist template."
            return "70%+ intensity for pet type."
        if petKey == "cu sidhe" and not self.state["isEliteResists"]:
            return "Cu Sidhe is missing an elite resist template."
        return "Intensity is below the 70% taming target."

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
        petSerial = API.RequestTarget()
        if not petSerial:
            return
        self._evaluatePetBySerial(petSerial, isSavingHistory)

    def _evaluatePetBySerial(self, petSerial, isSavingHistory):
        self.state = self._emptyState()

        pet = API.FindMobile(petSerial)
        if not pet:
            return

        API.PreTarget(pet.Serial)
        API.UseSkill("Animal Lore")
        API.WaitForTarget()
        API.Target(pet.Serial)
        while not API.GetGump(self.loreGumpId):
            API.Pause(0.1)
        gump = API.GetGump(self.loreGumpId)
        if not gump:
            return

        lines = gump.PacketGumpText.split("\n")
        isWild = any("wild" in line.lower() for line in lines)
        nmLower = pet.Name.lower()
        API.CloseGump(self.loreGumpId)

        supportedKeys = ["cu sidhe", "lesser hiryu"]
        key = next((k for k in supportedKeys if k in nmLower), None)
        if not key:
            key = self.mobileGraphicPetKeys.get(pet.Graphic)
        if not key:
            self.state["undefined"] = pet.Name
            return

        self.selectedPetKey = key
        for item in self.petTypeRadios:
            item["radio"].IsChecked = item["key"] == key

        self.currentPetClass = self._petClassFor(key, isWild)
        if not self.currentPetClass:
            self.state["undefined"] = pet.Name
            return

        self.state["petKey"] = key
        self.state["profile"] = self.currentPetClass.__class__.__name__
        self.state["name"] = pet.Name
        self.state["isWild"] = isWild

        statStart = 1
        resistStart = 11
        if self._safe(lines, 1).strip().endswith("%</div>") and "/" in self._safe(lines, 2):
            statStart = 2

        self.state["stats"] = [
            self._matchStat(self._safe(lines, statStart)),
            self._matchStat(self._safe(lines, statStart + 1)),
            self._matchStat(self._safe(lines, statStart + 2)),
            self._matchStat(self._safe(lines, statStart + 3)),
            self._matchStat(self._safe(lines, statStart + 4)),
            self._matchStat(self._safe(lines, statStart + 5)),
        ]
        self.state["resists"] = [
            self._matchResist(self._safe(lines, resistStart)),
            self._matchResist(self._safe(lines, resistStart + 1)),
            self._matchResist(self._safe(lines, resistStart + 2)),
            self._matchResist(self._safe(lines, resistStart + 3)),
            self._matchResist(self._safe(lines, resistStart + 4)),
        ]
        self.state["oldSlots"] = self._safe(lines, 21)
        self.state["newSlots"] = self._safe(lines, 22)

        self._recalculate()
        self.currentPetClass.analyzeDetails(self.state, pet)

        if isSavingHistory and self.currentPetClass.canSaveHistory:
            self._saveHistory()
        elif isSavingHistory and not self.currentPetClass.canSaveHistory:
            API.SysMsg("[PetIntensity] Tamed pet analyzed for information only; history was not saved.")

        self._drawHistoryIntensityChart()
        self._drawHistoryResistChart()
        self._updateGump()

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


    def _stripHtml(self, htmlStr):
        return re.sub(r"<[^>]+>", " ", htmlStr or "").replace("&nbsp;", " ").strip()

    def _valueAfterLabel(self, lines, label):
        for i, line in enumerate(lines):
            if label.lower() not in self._stripHtml(line).lower():
                continue
            for candidate in lines[i + 1:i + 4]:
                text = self._stripHtml(candidate)
                match = re.search(r"(\d+(?:\.\d+)?)(?:\s*/\s*\d+(?:\.\d+)?)?%?", text)
                if match:
                    return Decimal(match.group(1))
        return None

    def _recalculate(self):
        if not self.state["petKey"] or not self.currentPetClass:
            return
        cfg = self.petConfigs[self.state["petKey"]]
        self.currentPetClass.calculate(self.state, cfg)

    def _drawHistoryResistChart(self):
        try:
            chartX = self._resistChartX or 10
            chartY = self._resistChartY or 10
            chartWidth = self._resistChartWidth or self.GUMP_WIDTH - 30
            chartHeight = 18

            if hasattr(self, "resistChartElements"):
                for element in self.resistChartElements:
                    try:
                        element.Destroy()
                    except Exception:
                        try:
                            element.Dispose()
                        except Exception:
                            pass
            self.resistChartElements = []

            profile = self._historyPetClass()
            data = profile.readHistory() if profile else []
            total = 0
            elite_count = 0
            for entry in data:
                if "isEliteResists" in entry:
                    total += 1
                    if bool(entry["isEliteResists"]):
                        elite_count += 1

            elitePct = (elite_count / total) * 100 if total else 0
            elements = self.gump.createStackedBarChart(
                chartX, chartY, chartHeight, chartWidth, elitePct, ""
            )
            for element in elements:
                self.resistChartElements.append(element)
        except Exception as e:
            API.SysMsg(f"[PetIntensity] Resist chart error: {e}")

    def _historyCount(self):
        profile = self._historyPetClass()
        return profile.historyCount() if profile else 0

    def _drawHistoryIntensityChart(self):
        try:
            profile = self._historyPetClass()
            data = profile.readHistory() if profile else []
            intensities = [float(e.get("pctValue", 0)) for e in data]

            bins = [0] * 10
            for val in intensities:
                idx = min(9, int(val // 10))
                bins[idx] += 1

            if hasattr(self, "chartBars"):
                for b in self.chartBars:
                    try:
                        b.Destroy()
                    except Exception:
                        try:
                            b.Dispose()
                        except Exception:
                            pass
            self.chartBars = []

            chart_x = self._historyChartX or 10
            chart_y = self._historyChartY or 10
            chart_width = self._historyChartWidth or self.GUMP_WIDTH - 30
            chart_height = self._historyChartHeight or 120
            maxCount = max(bins) if any(bins) else 1
            bar_w = max(3, int(chart_width / 10) - 4)

            for i, count in enumerate(bins):
                bar_h = int((count / maxCount) * chart_height) if count else 0
                x = chart_x + i * int(chart_width / 10) + 2
                y = chart_y + chart_height - bar_h
                color = "#277bd8" if i >= 7 else "#36a852" if i >= 5 else "#d17a22"
                bar = self.gump.addColorBox(x, y, bar_h, bar_w, color, 0.8)
                self.chartBars.append(bar)

            self.totalPetLabel.Text = f"Total pets: {self._historyCount()}"
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
        profile = self._petClassFor("cu sidhe", self.state.get("isWild", True))
        if profile:
            profile.analyzeDetails(self.state, pet)

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
        if self.currentPetClass:
            self.currentPetClass.saveHistory(self.state)


try:
    petIntensity = PetIntensity()
    petIntensity.main()
    while petIntensity._isRunning():
        petIntensity.gump.tick()
        petIntensity.gump.tickSubGumps()
        petIntensity.tick()
        API.Pause(0.1)
except BaseException as e:
    API.SysMsg(f"PetIntensity e: {e}", 33)
    API.SysMsg(traceback.format_exc())
    raise
