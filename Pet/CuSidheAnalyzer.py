import API
import re
import urllib.request
from urllib.parse import urlencode
import importlib
from decimal import Decimal
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util
import Item

importlib.reload(Util)
importlib.reload(Item)

class CuSidheAnalyzer:
    resistTolerance = 5
    loreGumpId = 0x1db
    statRe = re.compile(r'<div align=right>(\d+(?:\.\d+)?)(?:/\d+)?%?</div>', re.IGNORECASE)
    resistRe = re.compile(r'(?:<BASEFONT[^>]*>)?<div align=right>(\d+(?:\.\d+)?)(?:/\d+)?%?</div>', re.IGNORECASE)

    cuSidheColors = {
        0: ("Original/Plain Color", "Extremely Common - 84%"),
        2426: ("Agapite / Rose", "Uncommon - 1 in 47 (2.1%)"),
        2218: ("Bronze", "Uncommon - 1 in 47 (2.1%)"),
        1447: ("Copper", "Uncommon - 1 in 47 (2.1%)"),
        2424: ("Dull Copper", "Uncommon - 1 in 47 (2.1%)"),
        2305: ("Grey", "Uncommon - 1 in 47 (2.1%)"),
        1319: ("Echo Blue", "Uncommon - 1 in 47 (2.1%)"),
        2220: ("Valorite Blue", "Uncommon - 1 in 47 (2.1%)"),
        1301: ("Sky Blue", "Rare - 1 in 476 (0.2%)"),
        1154: ("Ice Blue", "Rare - 1 in 476 (0.2%)"),
        1201: ("Pink", "Rare - 1 in 476 (0.2%)"),
        1652: ("Red", "Rare - 1 in 476 (0.2%)"),
        1109: ("Black", "Rare - 1 in 476 (0.2%)"),
        1153: ("Pure White", "Rare - 1 in 476 (0.2%)"),
        1161: ("Blaze", "Extremely Rare - 1 in 23,301 (0.004%)"),
    }

    resistTemplates = [
        {"Physical": 80, "Fire": 75, "Cold": 70, "Poison": 70, "Energy": 70},
        {"Physical": 80, "Fire": 80, "Cold": 65, "Poison": 70, "Energy": 70},
        {"Physical": 80, "Fire": 80, "Cold": 70, "Poison": 65, "Energy": 70},
        {"Physical": 80, "Fire": 80, "Cold": 65, "Poison": 65, "Energy": 75},
    ]

    def __init__(self):
        self.petSerial = None
        self.pet = None
        self.isWild = False
        self.stats = {}
        self.currentResists = {}

    def run(self):
        API.SysMsg("Target the Cu Sidhe")
        self.petSerial = API.RequestTarget()
        self.pet = API.FindMobile(self.petSerial)

        Util.Util.openGumpSkill("Animal Lore", self.petSerial, self.loreGumpId)
        gump = API.GetGump(self.loreGumpId)
        if not gump:
            API.SysMsg("Animal Lore gump not found.")
            return

        self.isWild = API.GumpContains("Wild")

        petHue = self.pet.Hue
        colorInfo = self.cuSidheColors.get(petHue, ("Unknown Color", "Rarity not listed"))
        API.SysMsg(f"Color: {colorInfo[0]} - Probability: {colorInfo[1]}")

        values = gump.PacketGumpText.split("\n")
        self.stats = {
            "Hits": self._matchStat(values[1]),
            "Stamina": self._matchStat(values[2]),
            "Mana": self._matchStat(values[3]),
            "Strength": self._matchStat(values[4]),
            "Dexterity": self._matchStat(values[5]),
            "Intelligence": self._matchStat(values[6]),
            "Physical Resist": self._matchResist(values[11]),
            "Fire Resist": self._matchResist(values[12]),
            "Cold Resist": self._matchResist(values[13]),
            "Poison Resist": self._matchResist(values[14]),
            "Energy Resist": self._matchResist(values[15]),
        }
        
        for val in range(5, 0, -1):
            if API.GumpContains(f"Pet Slots: {val}"):
                self.stats["Pet Slots"] = str(val)
                break
        else:
            self.stats["Pet Slots"] = "---"

        self.currentResists = {
            "Physical": self._getNum(self.stats["Physical Resist"]),
            "Fire": self._getNum(self.stats["Fire Resist"]),
            "Cold": self._getNum(self.stats["Cold Resist"]),
            "Poison": self._getNum(self.stats["Poison Resist"]),
            "Energy": self._getNum(self.stats["Energy Resist"]),
        }

        matched = False
        for i, template in enumerate(self.resistTemplates):
            trained = self._getPossibleTrainedResists(
                self.currentResists.copy(), template
            )
            if self._isWithinTemplateRange(trained, template):
                API.SysMsg(
                    f"Matches elite resist template #{i+1} (±{self.resistTolerance})"
                )
                API.SysMsg(str(trained))
                matched = True
        if not matched:
            API.SysMsg("No elite resist template matched.")

        params = {
            "creature": "Cu Sidhe",
            "hits": self._halfValue(self.stats["Hits"]),
            "stamina": self._halfValue(self.stats["Stamina"]),
            "mana": self._getNum(self.stats["Mana"]),
            "str": self._halfValue(self.stats["Strength"]),
            "dex": self._halfValue(self.stats["Dexterity"]),
            "int": self._getNum(self.stats["Intelligence"]),
            "rateminimum": 1,
            "physical": self._getNum(self.stats["Physical Resist"]),
            "fire": self._getNum(self.stats["Fire Resist"]),
            "cold": self._getNum(self.stats["Cold Resist"]),
            "poison": self._getNum(self.stats["Poison Resist"]),
            "energy": self._getNum(self.stats["Energy Resist"]),
            "target_physical": "--",
            "target_fire": "--",
            "target_cold": "--",
            "target_poison": "--",
            "target_energy": "--",
            "wrestling": 0,
            "resistingspells": 0,
            "evalintel": 0,
            "tactics": 0,
            "magery": 0,
            "poisoning": 0,
            "mic": "fresh",
        }

        self._fetchIntensityRating(params)

    def _matchStat(self, htmlStr):
        match = re.match(self.statRe, htmlStr)
        if match:
            stat = match.group(1).split("/")[0].strip()
            return Decimal(stat)
        
    def _matchResist(self, htmlStr):
        match = re.match(self.resistRe, htmlStr)
        if match:
            stat = match.group(1).split("%")[0].strip()
            return Decimal(stat)

    def _getNum(self, val):
        return Decimal(val)

    def _halfValue(self, val):
        return Decimal(self._getNum(val) / 2) if self.isWild else self._getNum(val)

    def _isWithinTemplateRange(self, trained, target):
        for resist in target:
            if abs(trained[resist] - target[resist]) > self.resistTolerance:
                return False
        return True

    def _getPossibleTrainedResists(self, current, template):
        maxTotal = 365
        totalCurrent = sum(current.values())
        budget = maxTotal - totalCurrent
        trained = current.copy()
        for resist in trained:
            minNeeded = template[resist] - self.resistTolerance
            maxAllowed = min(80, template[resist] + self.resistTolerance)
            target = min(maxAllowed, max(trained[resist], minNeeded))
            target = max(target, trained[resist])
            delta = target - trained[resist]
            if delta > budget:
                delta = budget
            trained[resist] += delta
            budget -= delta
        return trained

    def _fetchIntensityRating(self, params):
        url = "https://www.uo-cah.com/pet-intensity-calculator?" + urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                html = response.read().decode("utf-8")
                match = re.search(r"Intensity Rating: <strong>([\d.]+%)</strong>", html)
                if match:
                    API.SysMsg("Intensity Rating: " + match.group(1))
                else:
                    API.SysMsg("Intensity Rating not found.")
        except Exception as e:
            API.SysMsg("HTTP error: " + str(e))


CuSidheAnalyzer().run()
