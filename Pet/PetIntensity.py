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

    loreGumpId = 0x1DB
    statRe = re.compile(r'<div align=right>(\d+(?:\.\d+)?)(?:/\d+)?%?</div>', re.IGNORECASE)
    resistRe = re.compile(r'(?:<BASEFONT[^>]*>)?<div align=right>(\d+(?:\.\d+)?)(?:/\d+)?%?</div>', re.IGNORECASE)

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
        "nightmare": { "min": 3951, "max": 4254, "dmg": 75, "magical": 1500, "ability": 100, },
        "drake": {"min": 2820, "max": 3144, "dmg": 60, "magical": 0, "ability": 100},
        "greater dragon": { "min": 6139, "max": 9439, "dmg": 110, "magical": 1500, "ability": 200, "reduce": True, },
        "dragon": { "min": 6599, "max": 6936, "dmg": 75, "magical": 1500, "ability": 100, },
        "giant beetle": { "min": 1680, "max": 1830, "dmg": 70, "magical": 0, "ability": 0, },
        "fire beetle": { "min": 1890, "max": 1905, "dmg": 70, "magical": 0, "ability": 0, },
        "fire steed": { "min": 2870, "max": 3170, "dmg": 80, "magical": 0, "ability": 100, },
        "clydesdale": {"min": 2102, "max": 2818, "dmg": 70, "magical": 0, "ability": 0},
        "cu sidhe": { "min": 4624, "max": 5261, "dmg": 95, "magical": 0, "ability": 200, "reduce": True, },
        "high plains boura": { "min": 3701, "max": 4255, "dmg": 80, "magical": 0, "ability": 100, },
        "gaman": {"min": 1495, "max": 2001, "dmg": 40, "magical": 0, "ability": 0},
        "hell hound": { "min": 2581, "max": 3207, "dmg": 60, "magical": 1500, "ability": 100, },
        "hiryu": {"min": 4340, "max": 5272, "dmg": 100, "magical": 0, "ability": 200},
        "ki-rin": {"min": 3774, "max": 4117, "dmg": 75, "magical": 1500, "ability": 0},
        "unicorn": {"min": 3834, "max": 4222, "dmg": 75, "magical": 1500, "ability": 0},
        "lesser hiryu": { "min": 2070, "max": 2705, "dmg": 80, "magical": 0, "ability": 200, },
        "rune beetle": { "min": 5111, "max": 5760, "dmg": 75, "magical": 1600, "ability": 200, },
        "shadowmane": { "min": 4248, "max": 4248, "dmg": 75, "magical": 1500, "ability": 0, },
        "white wyrm": { "min": 5097, "max": 5760, "dmg": 85, "magical": 1500, "ability": 0, },
        "triton": {"min": 3556, "max": 4556, "dmg": 80, "magical": 0, "ability": 100},
        # New Legacy Pets
        "juvenile manticore": { "min": 4356, "max": 4943, "dmg": 90, "magical": 0, "ability": 0, },
        "emberwing": { "min": 7133, "max": 7118, "dmg": 100, "magical": 1500, "ability": 200, },
        "arantress": { "min": 5158, "max": 5143, "dmg": 75, "magical": 1600, "ability": 0, },
        "arctos": {"min": 4358, "max": 4343, "dmg": 75, "magical": 0, "ability": 200},
        "blazetail": { "min": 4172, "max": 4157, "dmg": 80, "magical": 0, "ability": 200, },
        "cinderclaw": { "min": 4433, "max": 4418, "dmg": 75, "magical": 0, "ability": 200, },
        "draalwyrm": { "min": 4827, "max": 5653, "dmg": 80, "magical": 0, "ability": 100, },
        "frostpaw": {"min": 3323, "max": 3332, "dmg": 65, "magical": 0, "ability": 200},
        "ossidrial": { "min": 7028, "max": 7028, "dmg": 85, "magical": 1600, "ability": 200, },
        "pachuxo": {"min": 4208, "max": 4193, "dmg": 75, "magical": 0, "ability": 200},
        "snarltooth": { "min": 4373, "max": 4358, "dmg": 75, "magical": 0, "ability": 200, },
        "thunderhoof": { "min": 3682, "max": 3667, "dmg": 65, "magical": 0, "ability": 100, },
    }

    def __init__(self):
        self.GUMP_WIDTH = 250
        self.GUMP_HEIGHT = 300

        self.gump = Gump(self.GUMP_WIDTH, self.GUMP_HEIGHT, self._onClose, False)
        self._running = True
        self.state = {
            "petKey": None,
            "stats": [],
            "resists": [],
            "pretame": False,
            "pctValue": 0,
            "pctRating": "0%",
            "oldSlots": "?",
            "newSlots": "?",
            "name": None,
            "undefined": None,
            "isWild": None,
            # Cu Sidhe extras:
            "cuColor": None,
            "cuRarity": None,
            "cuTemplate": None,
            "cuWebRating": None,
        }
        self.isDrawed = False

    @staticmethod
    def _num(s: str) -> int:
        m = re.search(r"(\d+)", s or "")
        return int(m.group(1)) if m else 0

    @staticmethod
    def _pct(s: str) -> int:
        m = re.search(r"(\d+)%", s or "")
        return int(m.group(1)) if m else 0

    @staticmethod
    def _safe(lines, idx):
        return lines[idx] if idx >= 0 and idx < len(lines) else ""

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

    def _resetState(self):
        self.state = {
            "petKey": None,
            "stats": [],
            "resists": [],
            "pretame": False,
            "pctValue": 0,
            "pctRating": "0%",
            "oldSlots": "?",
            "newSlots": "?",
            "name": None,
            "undefined": None,
            "isWild": None,
            "cuColor": None,
            "cuRarity": None,
            "cuTemplate": None,
            "cuWebRating": None,
        }

    def _evaluatePet(self):
        self._resetState()

        petSerial = API.RequestTarget()
        if not petSerial:
            return

        pet = API.FindMobile(petSerial)
        if not pet:
            return

        API.PreTarget(pet.Serial)
        API.UseSkill("Animal Lore")
        while not API.GetGump(self.loreGumpId):
            API.Pause(0.1)
        gump = API.GetGump(self.loreGumpId)
        if not gump:
            return

        isWild = API.GumpContains("Wild")
        lines = gump.PacketGumpText.split("\n")
        nmLower = pet.Name.lower()
        API.CloseGump(self.loreGumpId)
        key = next((k for k in self.petConfigs.keys() if k in nmLower), None)
        if not key:
            self.state["undefined"] = pet.Name
            return

        self.state["petKey"] = key
        self.state["name"] = pet.Name
        self.state["isWild"] = isWild

        self.state["stats"] = [
            self._matchStat(lines[1]),   # Hits
            self._matchStat(lines[2]),   # Stamina
            self._matchStat(lines[3]),   # Mana
            self._matchStat(lines[4]),   # Strength
            self._matchStat(lines[5]),   # Dexterity
            self._matchStat(lines[6]),   # Intelligence
        ]
        self.state["resists"] = [
            self._matchResist(lines[11]),  # Physical
            self._matchResist(lines[12]),  # Fire
            self._matchResist(lines[13]),  # Cold
            self._matchResist(lines[14]),  # Poison
            self._matchResist(lines[15]),  # Energy
        ]

        slotLine = PetIntensity._safe(lines, 43)
        m = re.search(r"(\d+)\s*=>\s*(\d+)", slotLine)
        self.state["oldSlots"] = m.group(1) if m else "?"
        self.state["newSlots"] = m.group(2) if m else "?"

        self._recalculate()

        if "cu sidhe" in nmLower:
            self._analyzeCuSidhe(pet, lines)
        self._saveHistory()
        self._drawHistoryChart()

    # -------------------------------
    # Cu Sidhe special analyzer
    # -------------------------------
    def _analyzeCuSidhe(self, pet, lines):
        petHue = pet.Hue
        colorInfo = self.cuSidheColors.get(
            petHue, ("Unknown Color", "Rarity not listed")
        )
        self.state["cuColor"], self.state["cuRarity"] = colorInfo

        # Resists for template check
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
        API.SysMsg(str(self.state["cuTemplate"]))

        # Web fetch (optional)
        params = {
            "creature": "Cu Sidhe",
            "hits": self.state["stats"][0],
            "stamina": self.state["stats"][1],
            "mana": self.state["stats"][2],
            "str": self.state["stats"][3],
            "dex": self.state["stats"][4],
            "int": self.state["stats"][5],
            "physical": resists["Physical"],
            "fire": resists["Fire"],
            "cold": resists["Cold"],
            "poison": resists["Poison"],
            "energy": resists["Energy"],
        }
        url = "https://www.uo-cah.com/pet-intensity-calculator?" + urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                html = response.read().decode("utf-8")
                match = re.search(r"Intensity Rating: <strong>([\d.]+%)</strong>", html)
                if match:
                    self.state["cuWebRating"] = match.group(1)
                    API.SysMsg(str(self.state["cuWebRating"]))
        except Exception as e:
            API.SysMsg("Cu Sidhe web fetch error: " + str(e))

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

    # -------------------------------
    # Recalculate & gump
    # -------------------------------
    def _recalculate(self):
        if not self.state["petKey"]:
            return
        cfg = self.petConfigs[self.state["petKey"]]

        s = self.state["stats"][:]
        r = self.state["resists"][:]

        if cfg.get("reduce") and self.state["isWild"]:
            s[0] = Decimal((s[0]) / 2)   # Hits
            s[1] = Decimal((s[1]) / 2)   # Stamina
            s[3] = Decimal((s[3]) / 2)   # Strength
            s[4] = Decimal((s[4]) / 2)   # Dexterity

        wStats = [Decimal("3"), Decimal("0.5"), Decimal("0.5"), Decimal("3"), Decimal("0.1"), Decimal("0.5")]
        wResists = [Decimal("3"), Decimal("3"), Decimal("3"), Decimal("3"), Decimal("3")]

        total = sum(s[i] * wStats[i] for i in range(len(s)))
        total += sum(r[j] * wResists[j] for j in range(len(r)))
        total += Decimal(cfg.get("dmg", 0)) + Decimal(cfg.get("magical", 0)) + Decimal(cfg.get("ability", 0))

        den = Decimal(cfg["max"]) - Decimal(cfg["min"])
        pctValue = ((total - Decimal(cfg["min"])) / den * Decimal(100)) if den > 0 else Decimal(0)
        pctValue = max(Decimal(0), min(Decimal(100), pctValue))

        self.state["pctValue"] = float(pctValue)  # keep as float for easy formatting
        self.state["pctRating"] = f"{pctValue:.2f}%"

    def _showGump(self):
        self.gump.addLabel("Pet Intensity Calculator", round(self.GUMP_WIDTH / 2 - 100), 1)
        self.gump.addButton(
            "", round(self.GUMP_WIDTH / 2 + 65), 1, "eye", self.gump.onClick(lambda: self._help()), True
        )

        self.undefinedLabel = self.gump.addLabel("", 1, 40)
        self.nameLabel = self.gump.addLabel("", 1, 55)
        self.ratingLabel = self.gump.addLabel("", 1, 70)

        # Cu Sidhe extras
        self.colorLabel = self.gump.addLabel("", 1, 90)
        self.templateLabel = self.gump.addLabel("", 1, 105)
        self.webLabel = self.gump.addLabel("", 1, 120)

        self.gump.create()
        self._drawHistoryChart()

    def _help(self):
        API.SysMsg("Press SHIFT+A to analyze a pet")

    def _updateGump(self):
        self.nameLabel.Text = (
            f"{self.state['name']} {self.state['oldSlots']}→{self.state['newSlots']}"
        )
        hue = (
            33
            if self.state["pctValue"] < 50
            else 52 if self.state["pctValue"] < 80 else 67
        )
        self.ratingLabel.Text = f"Rating: {self.state['pctRating']}"
        self.ratingLabel.Hue = hue

        # Cu Sidhe extras
        if self.state["cuColor"]:
            self.colorLabel.Text = (
                f"Color: {self.state['cuColor']} ({self.state['cuRarity']})"
            )
        if self.state["cuTemplate"]:
            self.templateLabel.Text = f"Elite: {self.state['cuTemplate']}"
        if self.state["cuWebRating"]:
            self.webLabel.Text = f"Web: {self.state['cuWebRating']}"

    def tick(self):
        if self.state["petKey"] or self.state["undefined"]:
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
        API.OnHotKey("SHIFT+A", self._evaluatePet)

    def _isRunning(self):
        return self._running

    def _saveHistory(self):
        import json, os
        from datetime import datetime
        from decimal import Decimal

        try:
            data = []
            if os.path.exists(self.SAVE_FILE):
                with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

            # Convert any Decimal in self.state to float recursively
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

            entry = {
                "timestamp": now_str,
                **cleaned_state,
            }

            data.append(entry)
            with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            API.SysMsg(f"[PetIntensity] History save error: {e}")

    def _drawHistoryChart(self):
        """
        Vertical bar chart:
        X-axis = intensity bins (0–100%)
        Y-axis = number of analyzed pets in each intensity range.
        """
        try:
            if not os.path.exists(self.SAVE_FILE):
                API.SysMsg("[PetIntensity] No history data yet.")
                return

            with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                API.SysMsg("[PetIntensity] History file empty.")
                return

            # Extract intensities
            intensities = [float(e.get("pctValue", 0)) for e in data if "pctValue" in e]
            if not intensities:
                API.SysMsg("[PetIntensity] No valid intensity data.")
                return

            # Group into 10 bins: 0–10, 10–20, ... 90–100
            bins = [0] * 10
            for val in intensities:
                idx = min(9, int(val // 10))
                bins[idx] += 1

            maxCount = max(bins) if any(bins) else 1

            # Chart geometry
            chart_x = 10
            chart_y = 140
            chart_width = 180
            chart_height = 100
            bar_width = int(chart_width / len(bins)) - 2

            # Remove old bars
            if hasattr(self, "chartBars"):
                for bar in self.chartBars:
                    try:
                        bar.Destroy()
                    except Exception:
                        pass
            self.chartBars = []

            # Grid lines (Y = number of pets)
            if not self.isDrawed:
                self.gump.addLabel("Intensity Distribution", chart_x, chart_y - 15)
                self.totalPetLabel = self.gump.addLabel(f"Total pets: {len(intensities)}", chart_x, chart_y + chart_height + 20)
                for frac in [0, 0.5, 1.0]:
                    y = chart_y + chart_height - int(frac * chart_height)
                    self.gump.addColorBox(chart_x, y, 1, chart_width, "#919191")
                    self.gump.addLabel(f"{int(frac * maxCount)}", chart_x + chart_width + 5, y - 5)
                self.isDrawed = True

            # Draw bars
            for i, count in enumerate(bins):
                if count <= 0:
                    continue

                height = max(1, int((count / maxCount) * chart_height))
                x = chart_x + i * (bar_width + 2)
                y = chart_y + (chart_height - height)

                # Draw vertical bar
                bar = self.gump.addColorBox(int(x), int(y), int(height), int(bar_width), "#919191")
                self.chartBars.append(bar)

                # Label intensity bin below bar
                self.gump.addLabel(f"{int(i * 10)}", x, chart_y + chart_height + 5)

            # Title / Footer
            self.totalPetLabel.Text = f"Total pets: {len(intensities)}"

        except Exception as e:
            API.SysMsg(f"[PetIntensity] Chart draw error: {e}")


petIntensity = PetIntensity()
petIntensity.main()
while petIntensity._isRunning():
    petIntensity.gump.tick()
    petIntensity.gump.tickSubGumps()
    petIntensity.tick()
    API.Pause(0.1)