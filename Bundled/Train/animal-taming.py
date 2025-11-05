#=========== Consolidated Imports ============#
from decimal import Decimal
import API
import System
import hashlib
import importlib
import json
import os
import re
import sys
import time
import math


#=========== Start of _Utils\math.py ============#

class Math:
    centerX = 1323
    mapWidth = 5120
    centerY = 1624
    mapHeight = 4096
    
    @staticmethod
    def truncateDecimal(n1, d=1):
        n = str(n1)
        return n if "." not in n else n[: n.find(".") + d + 1]
    
    @staticmethod
    def distanceBetween(m1, m2):
        if not m1 or not m2:
            return 999
        return max(abs(m1.X - m2.X), abs(m1.Y - m2.Y))

    @staticmethod
    def convertToHex(obj):
        if isinstance(obj, dict):
            return {k: Math.convertToHex(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Math.convertToHex(elem) for elem in obj]
        elif isinstance(obj, str) and re.fullmatch(r"0x[0-9a-fA-F]+", obj):
            return int(obj, 16)
        return obj
    
    @staticmethod
    def tilesToLatLon(x, y):
        degLon = (x - Math.centerX) * 360.0 / Math.mapWidth
        degLat = (y - Math.centerY) * 360.0 / Math.mapHeight

        if degLon > 180:
            degLon = 360 - degLon
            lonDir = "W"
        else:
            lonDir = "E"

        if degLat > 180:
            degLat = 360 - degLat
            latDir = "N"
        else:
            latDir = "S"

        lat = (int(degLat), (degLat - int(degLat)) * 60, latDir)
        lon = (int(degLon), (degLon - int(degLon)) * 60, lonDir)
        return lat, lon

    @staticmethod
    def latLonToTiles(degLat, minLat, latDir, degLon, minLon, lonDir):
        totalLat = degLat + minLat / 60
        if latDir == "N":
            totalLat = 360 - totalLat

        totalLon = degLon + minLon / 60
        if lonDir == "W":
            totalLon = 360 - totalLon

        y = totalLat * Math.mapHeight / 360 + Math.centerY
        x = totalLon * Math.mapWidth / 360 + Math.centerX
        return int(x % Math.mapWidth), int(y % Math.mapHeight)
#=========== End of _Utils\math.py ============#

#=========== Start of LegionPath.py ============#

class LegionPath:
    @staticmethod
    def createPath(path):
        path = f"{LegionPath.getLegionPath()}/{path}"
        return path

    @staticmethod
    def getLegionPath():
        base = sys.prefix
        if base.lower().endswith("ironpython.dll"):
            base = os.path.dirname(base)

        legion_path = os.path.join(base, "LegionScripts")
        return legion_path

    @staticmethod
    def addSubdirs():
        legion_path = LegionPath.getLegionPath()

        if not os.path.isdir(legion_path):
            return

        for name in os.listdir(legion_path):
            subdir = os.path.join(legion_path, name)
            if os.path.isdir(subdir) and name.startswith("_"):
                if subdir not in sys.path:
                    sys.path.append(subdir)
#=========== End of LegionPath.py ============#

#=========== Start of _Classes\Animal.py ============#
class Animal:
    def __init__(self, name, mobileID, color, minTamingSkill, maxTamingSkill, packType):
        self.name = name
        self.mobileID = mobileID
        self.color = color
        self.minTamingSkill = minTamingSkill
        self.maxTamingSkill = maxTamingSkill
        self.packType = packType

    @staticmethod
    def rename(animal, name):
        API.Rename(animal.Serial, name)
        API.Pause(0.1)

    @staticmethod
    def release(animal):
        API.ContextMenu(animal.Serial, 138)
        while not API.HasGump(601):
            API.Pause(0.1)
        API.ReplyGump(2, 601)

    @staticmethod
    def kill(magic, animal, spellToKill):
        API.PreTarget(animal.Serial, "Harmful")
        magic.cast(spellToKill)
#=========== End of _Classes\Animal.py ============#

#=========== Start of _Utils\Math.py ============#

class Math:
    centerX = 1323
    mapWidth = 5120
    centerY = 1624
    mapHeight = 4096
    
    @staticmethod
    def truncateDecimal(n1, d=1):
        n = str(n1)
        return n if "." not in n else n[: n.find(".") + d + 1]
    
    @staticmethod
    def distanceBetween(m1, m2):
        if not m1 or not m2:
            return 999
        return max(abs(m1.X - m2.X), abs(m1.Y - m2.Y))

    @staticmethod
    def convertToHex(obj):
        if isinstance(obj, dict):
            return {k: Math.convertToHex(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Math.convertToHex(elem) for elem in obj]
        elif isinstance(obj, str) and re.fullmatch(r"0x[0-9a-fA-F]+", obj):
            return int(obj, 16)
        return obj
    
    @staticmethod
    def tilesToLatLon(x, y):
        degLon = (x - Math.centerX) * 360.0 / Math.mapWidth
        degLat = (y - Math.centerY) * 360.0 / Math.mapHeight

        if degLon > 180:
            degLon = 360 - degLon
            lonDir = "W"
        else:
            lonDir = "E"

        if degLat > 180:
            degLat = 360 - degLat
            latDir = "N"
        else:
            latDir = "S"

        lat = (int(degLat), (degLat - int(degLat)) * 60, latDir)
        lon = (int(degLon), (degLon - int(degLon)) * 60, lonDir)
        return lat, lon

    @staticmethod
    def latLonToTiles(degLat, minLat, latDir, degLon, minLon, lonDir):
        totalLat = degLat + minLat / 60
        if latDir == "N":
            totalLat = 360 - totalLat

        totalLon = degLon + minLon / 60
        if lonDir == "W":
            totalLon = 360 - totalLon

        y = totalLat * Math.mapHeight / 360 + Math.centerY
        x = totalLon * Math.mapWidth / 360 + Math.centerX
        return int(x % Math.mapWidth), int(y % Math.mapHeight)
#=========== End of _Utils\Math.py ============#

#=========== Start of _Utils\Util.py ============#





class Util:
    skillNames = [
        "Archery",
        "Chivalry",
        "Fencing",
        "Focus",
        "Mace Fighting",
        "Parrying",
        "Swordsmanship",
        "Tactics",
        "Wrestling",
        "Bushido",
        "Throwing",
        "Healing",
        "Veterinary",
        "Alchemy",
        "Evaluating Intelligence",
        "Inscription",
        "Magery",
        "Meditation",
        "Necromancy",
        "Resisting Spells",
        "Spellweaving",
        "Spirit Speak",
        "Mysticism",
        "Discordance",
        "Musicianship",
        "Peacemaking",
        "Provocation",
        "Begging",
        "Detecting Hidden",
        "Hiding",
        "Lockpicking",
        "Poisoning",
        "Remove Trap",
        "Snooping",
        "Stealing",
        "Stealth",
        "Ninjitsu",
        "Anatomy",
        "Animal Lore",
        "Animal Taming",
        "Camping",
        "Forensic Evaluation",
        "Herding",
        "Taste Identification",
        "Tracking",
        "Arms Lore",
        "Blacksmithy",
        "Bowcraft/Fletching",
        "Carpentry",
        "Cooking",
        "Item Identification",
        "Cartography",
        "Tailoring",
        "Tinkering",
        "Imbuing",
        "Fishing",
        "Mining",
        "Lumberjacking",
    ]

    layers = [
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

    @staticmethod
    def getWeaponName():
        twoHandedWeapon = API.FindLayer("TwoHanded")
        if twoHandedWeapon:
            props = API.ItemNameAndProps(twoHandedWeapon.Serial, True).split("\n")
            return props[0].strip()
        oneHandedWeapon = API.FindLayer("OneHanded")
        if oneHandedWeapon:
            props = API.ItemNameAndProps(oneHandedWeapon.Serial, True).split("\n")
            return props[0].strip()
            
    @staticmethod
    def getPlayerName():
        while not API.Player.Name:
            API.Pause(0.1)
        playerName = API.Player.Name.replace("Lady ", "").replace("Lord ", "")
        return playerName

    @staticmethod
    def getMasterContainer(corpseSerial):
        corpseItem = API.FindItem(corpseSerial)
        API.SysMsg(str(corpseItem))
        if corpseItem.Container:
            corpseItem = API.FindItem(corpseItem.Container)
            API.SysMsg(f"container: {str(corpseItem)}")
            return corpseItem
        return corpseItem

    @staticmethod
    def scanEnemies(range=15):
        enemies = API.NearestMobiles(
            [
                API.Notoriety.Enemy,
                API.Notoriety.Criminal,
                API.Notoriety.Gray,
                API.Notoriety.Murderer,
            ],
            range,
        )
        enemies = [m for m in enemies if not m.IsRenamable and m.HasLineOfSightFrom()]
        enemies = sorted(
            enemies, key=lambda m: Math.distanceBetween(API.Player, m)
        )
        return enemies

    @staticmethod
    def getStatValue(statName):
        rawStat = getattr(API.Player, statName)
        for layer in Util.layers:
            item = API.FindLayer(layer)
            if item:
                props = API.ItemNameAndProps(item.Serial).split("\n")
                for prop in props:
                    if f"{statName} Bonus".lower() in prop.lower():
                        bonus = prop.split("Bonus ")[1]
                        rawStat -= int(bonus)
        return rawStat

    @staticmethod
    def useObject(objectSerial):
        API.CancelTarget()
        object = API.FindItem(objectSerial)
        if not object:
            API.SysMsg(f"Object {str(objectSerial)} not found")
        API.UseObject(object.Serial)

    @staticmethod
    def useObjectWithTarget(objectSerial):
        API.CancelTarget()
        while not API.WaitForTarget("any", 3):
            Util.useObject(objectSerial)

    @staticmethod
    def closeGump(gumpId):
        while API.HasGump(gumpId):
            API.SysMsg("Closing GUMP")
            API.CloseGump(gumpId)
            API.Pause(0.5)
            API.SysMsg(f"API.HasGump(gumpId) 1: {str(API.HasGump(gumpId))}")

    @staticmethod
    def openGumpObject(objectSerial, gumpId):
        Util.closeGump(gumpId)
        while not API.HasGump(gumpId):
            Util.useObject(objectSerial)
            API.Pause(0.5)
        API.SysMsg(f"API.HasGump(gumpId) 2: {str(API.HasGump(gumpId))}")
        gump = API.GetGump(gumpId)
        return gump

    @staticmethod
    def openGumpSkill(skillName, targetSerial, gumpId):
        while not API.HasGump(gumpId):
            API.UseSkill(skillName)
            API.WaitForTarget("any", 1)
            API.Target(targetSerial)
            API.Pause(0.1)

    @staticmethod
    def getCharSkillInfo():
        totalPlus = 0
        totalMinus = 0
        for skillName in Util.skillNames:
            values = Util.getSkillInfo(skillName)
            skillValue = values["value"]
            lock = values["lock"]
            if lock == "Locked" or lock == "Up":
                totalPlus += skillValue
            else:
                totalMinus += skillValue
        return {"totalPlus": totalPlus, "totalMinus": totalMinus}

    @staticmethod
    def getSkillInfo(skillName):
        values = API.GetSkill(skillName)
        v = Decimal(Math.truncateDecimal(values.Value))
        c = Decimal(Math.truncateDecimal(values.Cap))
        l = str(values.Lock)
        return {"value": v, "cap": c, "lock": l}

    @staticmethod
    def isWearingWeapon():
        oneHanded = bool(API.FindLayer("OneHanded"))
        if oneHanded:
            return True
        twoHanded = bool(API.FindLayer("TwoHanded"))
        return twoHanded

    @staticmethod
    def getTotalSkillPoints():
        total = 0
        for skill in Util.skillNames:
            value = Util.getSkillInfo(skill)["value"]
            total += value
        return total

    @staticmethod
    def findItemWithProps(props):
        items = Util.itemsInContainer(API.Backpack)
        for item in items:
            itemProps = API.ItemNameAndProps(item.Serial).split("\n")
            if all(any(p in itemProp for itemProp in itemProps) for p in props):
                return item

    @staticmethod
    def isTargeting():
        return API.WaitForTarget("any", 0)

    @staticmethod
    def getTypeOfTarget():
        res = None
        if API.WaitForTarget("Neutral", 0):
            res = "Neutral"
        elif API.WaitForTarget("Harmful", 0):
            res = "Harmful"
        elif API.WaitForTarget("Beneficial", 0):
            res = "Beneficial"
        else:
            res = None
        return res

    @staticmethod
    def checkIfGearBroken():
        for layer in Util.layers:
            item = API.FindLayer(layer)
            if item:
                props = API.ItemNameAndProps(item.Serial).split("\n")
                for prop in props:
                    if "durability 0 /" in prop.lower():
                        return True
        return False

    @staticmethod
    def itemsInContainer(containerSerial):
        allItems = API.ItemsInContainer(containerSerial, True)
        if len(allItems) == 1 and allItems[0].Graphic == 8198:
            allItems = API.ItemsInContainer(allItems[0].Serial, True)
        return allItems

    @staticmethod
    def findTypeAll(containerId, itemId, hue=None):
        filteredItems = []
        items = Util.itemsInContainer(containerId)
        for item in items:
            if item.Graphic == itemId:
                if hue and item.Hue == hue:
                    filteredItems.append(item)
                if not hue:
                    filteredItems.append(item)
        return filteredItems

    @staticmethod
    def findCorpses(range=7):
        items = API.FindTypeAll(8198, 4294967295, range)
        return items

    @staticmethod
    def findTypeWorld(itemId, range=2):
        item = API.FindType(itemId, 4294967295, range)
        return item

    @staticmethod
    def findType(containerId, itemId):
        items = Util.itemsInContainer(containerId)
        for item in items:
            if item.Graphic == itemId:
                return item
        return None

    @staticmethod
    def findTypeWithSpecialHue(resourceId, container, minAmount, resourceHue):
        resource = API.FindType(
            resourceId, container, hue=resourceHue, minamount=minAmount
        )
        return resource

    @staticmethod
    def openContainer(container):
        if isinstance(container, System.UInt32):
            container = API.FindItem(container)
        isOpened = container.Opened
        if not isOpened:
            API.UseObject(container.Serial)
            API.Pause(1)

    @staticmethod
    def moveItemOffset(itemSerial, xOffset=0, yOffset=1, amount=0, maxRetries=5):
        for attempt in range(maxRetries):
            API.ClearJournal()
            API.MoveItemOffset(itemSerial, amount, xOffset, yOffset, OSI=True)
            API.Pause(1)

            if not API.InJournal("You must wait to perform another action."):
                return True

            API.SysMsg(f"Retrying move ({attempt + 1}/{maxRetries})...", 33)
            API.Pause(1)

        API.SysMsg("Move failed after retries.", 33)
        return False

    @staticmethod
    def moveItem(itemSerial, destinationSerial, amount=0, maxRetries=5):
        for attempt in range(maxRetries):
            API.ClearJournal()
            API.MoveItem(itemSerial, destinationSerial, amount)
            API.Pause(1)

            if not API.InJournal("You must wait to perform another action."):
                return True

            API.SysMsg(f"Retrying move ({attempt + 1}/{maxRetries})...", 33)
            API.Pause(1)

        API.SysMsg("Move failed after retries.", 33)
        return False

    @staticmethod
    def getContents(item):
        props = API.ItemNameAndProps(item.Serial, True).split("\n")
        for prop in props:
            if "Contents" in prop:
                match = re.search(
                    r"Content[s]?:\s*(\d+)/\d+\s+Items,\s*(\d+)(?:/\d+)?\s+Stones", prop
                )
                if match:
                    result = {
                        "items": int(match.group(1)),
                        "stones": int(match.group(2)),
                    }
                else:
                    result = {"items": None, "stones": None}
                return result
#=========== End of _Utils\Util.py ============#

#=========== Start of _Utils\Magic.py ============#





with open(LegionPath.createPath("_Jsons\\spell-def-magic.json")) as f:
    SPELLS = json.load(f)


class Magic:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Magic, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.recallMethod = self._getRecallMethod()
        self._lastCastTime = 0

    @staticmethod
    def _now():
        return time.time()

    @staticmethod
    def regenMana(manaRequired):
        if API.Player.Mana >= manaRequired:
            return
        lastAttempt = 0
        while API.Player.Mana < API.Player.ManaMax:
            if not API.BuffExists("Actively Meditating"):
                now = time.time()
                if now - lastAttempt >= 11:
                    API.UseSkill("Meditation")
                    lastAttempt = now
            API.Pause(0.1)

    @staticmethod
    def getFcDelay(castingTime):
        fc = getattr(API.Player, "FasterCasting", 0)
        return max(castingTime - (fc * 0.25), 0)

    @staticmethod
    def getFcrDelay():
        fcr = getattr(API.Player, "FasterCastRecovery", 0)
        return max(1.5 - (fcr * 0.25), 0)

    @staticmethod
    def getManaCost(baseCost):
        lmc = getattr(API.Player, "LowerManaCost", 0)
        return max(1, round(baseCost * (1 - lmc / 100.0)))

    def findSpellDef(self, spellName):
        for spell in SPELLS:
            if spell["name"].lower() == spellName.lower():
                return spell
        return None

    def hasSpell(self, spellName):
        API.ClearJournal()
        API.CastSpell(spellName)
        API.Pause(0.1)
        return not self._checkNoSpell()

    def cast(self, spellName, maxTries=3):
        API.SysMsg(spellName)
        spellDef = self.findSpellDef(spellName)
        if not spellDef:
            API.SysMsg(f"Invalid spell name: {spellName}", 33)
            return False

        manaNeeded = self.getManaCost(spellDef["manaCost"])

        for _ in range(maxTries):
            API.ClearJournal()
            if API.Player.Mana < manaNeeded:
                self.regenMana(manaNeeded)
            API.CastSpell(spellName)
            self._lastCastTime = self._now()
            castStart = self._now()
            retry = False
            while self._now() - castStart < spellDef["castTime"]:
                if spellDef["hasTarget"] and Util.isTargeting():
                    return True
                if self._checkNoSpell():
                    API.SysMsg(f"You do not have that spell: {spellName}", 33)
                    return False
                if self._checkFizzleJournal():
                    API.SysMsg(f"Spell fizzled: {spellName}", 33)
                    retry = True
                    break
                if self._checkManaFailureJournal():
                    API.SysMsg("Not enough mana, retrying", 33)
                    self.regenMana(manaNeeded)
                    retry = True
                    break
                if self._checkRecoveredJournal():
                    retry = True
                    break
                API.Pause(0.05)
            if spellDef["hasTarget"] and Util.isTargeting():
                return True
            if not retry:
                return True
            API.Pause(0.1)
        return True

    def healCure(self, greaterHealOffset=20, healOffset=10):
        player = API.Player
        skills = {s: API.GetSkill(s).Value for s in ["Magery", "Chivalry", "Spellweaving", "Spirit Speak"]}
        while API.BuffExists("Poisoned"):
            if skills["Magery"] >= 30 and self.cast("Cure"):
                pass
            elif skills["Chivalry"] >= 30 and self.cast("Remove Curse"):
                pass
            elif skills["Spellweaving"] >= 24 and self.cast("Essence of Wind"):
                pass
            else:
                break
            if API.WaitForTarget("any", 3):
                API.TargetSelf()
        while player.Hits < player.HitsMax - greaterHealOffset:
            if skills["Magery"] >= 50 and self.cast("Greater Heal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Magery"] >= 30 and self.cast("Heal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Chivalry"] >= 30 and self.cast("Close Wounds"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Spirit Speak"] >= 30:
                API.UseSkill("Spirit Speak")
                API.Pause(7)
                continue
            elif skills["Spellweaving"] >= 24 and not API.BuffExists("Gift of Renewal") and self.cast("Gift of Renewal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            else:
                bandage = API.FindType(0x0E21, API.Backpack)
                if bandage:
                    API.UseObject(bandage)
                    if API.WaitForTarget("any", 3):
                        API.TargetSelf()
                        API.Pause(7)
                break
        while player.Hits < player.HitsMax - healOffset:
            if skills["Magery"] >= 30 and self.cast("Heal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Chivalry"] >= 30 and self.cast("Close Wounds"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Spirit Speak"] >= 30:
                API.UseSkill("Spirit Speak")
                API.Pause(7)
            else:
                break

    def recallToLocation(self, index, runebookItem):
        API.UseObject(runebookItem)
        API.Pause(1)
        if not API.HasGump(89):
            API.SysMsg("Runebook's gump did not open", 33)
            return
        API.ClearJournal()
        method = self._getRecallMethod()
        if method == "magery":
            API.ReplyGump(index + 50, 89)
        elif method == "chivalry":
            API.ReplyGump(index + 74, 89)
        else:
            API.SysMsg("No recall method available", 33)
            return
        # Retry if fizzled
        start = self._now()
        while self._now() - start < 4:
            if self._checkFizzleJournal():
                self.recallToLocation(index, runebookItem)
                break
            if not API.HasGump(89):
                break
            API.Pause(0.1)

    def _checkRecoveredJournal(self):
        return API.InJournalAny(["You have not yet recovered from casting a spell."])

    def _checkAlreadyCastingJournal(self):
        return API.InJournalAny([
            "You are already casting a spell.",
            "You must wait before casting another spell.",
        ])

    def _checkNoSpell(self):
        return API.InJournalAny([
            "You do not have that spell!",
            "You have not learned that spell"
        ])

    def _checkFizzleJournal(self):
        return API.InJournalAny([
            "You lost your concentration.",
            "Your spell fizzles.",
            "You can't cast that spell right now.",
            "You fail to cast",
            "Something is blocking the location.",
        ])

    def _checkManaFailureJournal(self):
        return API.InJournalAny(["You don't have enough mana"])

    def _getRecallMethod(self):
        magery = API.GetSkill("Magery").Value
        chivalry = API.GetSkill("Chivalry").Value
        if magery >= 40:
            return "magery"
        elif chivalry >= 40:
            return "chivalry"
        return None

    def _waitForRecovery(self, timeout=2.0):
        start = self._now()
        while self._now() - start < timeout:
            if not self._checkRecoveredJournal():
                return True
            API.Pause(0.05)
        return False
#=========== End of _Utils\Magic.py ============#

#=========== Start of _Utils\Timer.py ============#

class Timer:
    timers = []
    
    @classmethod
    def create(cls, seconds, text, hue=21):
        cls.clear(seconds, text, hue)
        API.CreateCooldownBar(seconds, text, hue)
        hash = cls._hash(seconds, text, hue)
        cls.timers.append({
            "created": time.time(),
            "seconds": seconds,
            "hash": hash
        })

    @classmethod
    def exists(cls, seconds, text, hue=21):
        cls._cleanupExpired()
        hash = cls._hash(seconds, text, hue)
        for timer in cls.timers:
            if timer["hash"] == hash:
                return True
        return False
        
    @classmethod
    def clear(cls, seconds, text, hue):
        hash = cls._hash(seconds, text, hue)
        cls.timers = [t for t in cls.timers if t["hash"] != hash]
        
    @classmethod
    def _hash(cls, seconds, text, hue):
        s = f"{seconds}{text}{hue}"
        return hashlib.md5(s.encode("ascii")).hexdigest()
    
    @classmethod
    def _cleanupExpired(cls):
        now = time.time()
        cls.timers = [
            t for t in cls.timers
            if now - t["created"] < t["seconds"]
        ]
#=========== End of _Utils\Timer.py ============#

#=========== Start of .\Train\animal-taming.py ============#







class AnimalTaming:
    _maxDistance = 18
    _animals = {
        # between 30 - 31
        "cat": Animal("cat", 0x00C9, 0x0000, 30, 39, ["feline"]),
        "chicken": Animal("chicken", 0x00D0, 0x0000, 30, 39, None),
        "mountain goat": Animal("mountain goat", 0x0058, 0x0000, 30, 39, None),
        # between 31.1 - 51.1
        "Cow (brown)": Animal("cow", 0x00E7, 0x0000, 31.1, 51.1, None),
        "Cow (black)": Animal("cow", 0x00D8, 0x0000, 31.1, 51.1, None),
        "Goat": Animal("goat", 0x00D1, 0x0000, 31.1, 51.1, None),
        "Pig": Animal("pig", 0x00CB, 0x0000, 31.1, 51.1, None),
        "Sheep": Animal("sheep", 0x00CF, 0x0000, 31.1, 51.1, None),
        # between 43.1 - 63.1
        "Hind": Animal("hind", 0x00ED, 0x0000, 43.1, 63.1, None),
        "Timber Wolf": Animal("timber wolf", 0x00E1, 0x0000, 43.1, 63.1, ["canine"]),
        # between 49.1 - 69.1
        "Boar": Animal("boar", 0x0122, 0x0000, 49.1, 69.1, None),
        "Desert Ostard": Animal(
            "desert ostard", 0x00D2, 0x0000, 49.1, 69.1, ["ostard"]
        ),
        "forest ostard (green)": Animal(
            "forest ostard", 0x00DB, 0x88A0, 49.1, 69.1, ["ostard"]
        ),
        "forest ostard (red)": Animal(
            "forest ostard", 0x00DB, 0x889D, 49.1, 69.1, ["ostard"]
        ),
        "horse": Animal("horse", 0x00C8, 0x0000, 49.1, 69.1, None),
        "horse2": Animal("horse", 0x00E2, 0x0000, 49.1, 69.1, None),
        "horse3": Animal("horse", 0x00CC, 0x0000, 49.1, 69.1, None),
        "horse4": Animal("horse", 0x00E4, 0x0000, 49.1, 69.1, None),
        # between 55.1 - 75.1
        "Black bear": Animal("black bear", 0x00D3, 0x0000, 55.1, 75.1, ["bear"]),
        "Llama": Animal("llama", 0x00DC, 0x0000, 55.1, 75.1, None),
        "Polar bear": Animal("polar bear", 0x00D5, 0x0000, 55.1, 75.1, ["bear"]),
        "Walrus": Animal("walrus", 0x00DD, 0x0000, 55.1, 75.1, None),
        # between 61.1 - 81.1
        "Brown Bear": Animal("brown bear", 0x00A7, 0x0000, 61.1, 81.1, ["bear"]),
        "cougar": Animal("cougar", 0x003F, 0x0000, 61.1, 81.1, ["feline"]),
        # between 73.1 - 93.1
        "snow leopard": Animal("snow leopard", 0x0040, 0x0000, 73.1, 93.1, ["feline"]),
        "snow leopard2": Animal("snow leopard", 0x0041, 0x0000, 73.1, 93.1, ["feline"]),
        # between 79.1 - 99.1
        "great hart": Animal("great hart", 0x00EA, 0x0000, 79.1, 99.1, None),
    }

    def __init__(self):
        self._running = True
        self._killList = []
        self._magic = Magic()

        self._animalBeingTamed = None
        self._tameHandled = False
        self._isTaming = False
        self._ownPetSerial = None

    def main(self):
        self._checkSkill()

    def tick(self):
        animalSkillInfo = Util.getSkillInfo("Animal Taming")
        if animalSkillInfo["value"] >= 90:
            if not self._ownPetSerial:
                self._ownPetSerial = API.RequestTarget()
            self._magic.regenMana(26)
            API.PreTarget(self._ownPetSerial, "beneficial")
            API.CastSpell("Combat training")
            API.Pause(2)

        else:
            if not self._isTaming:
                self._attackTamed(self._animalBeingTamed)

                animalSkillInfo = Util.getSkillInfo("Animal Taming")
                if animalSkillInfo["value"] == animalSkillInfo["cap"]:
                    API.SysMsg("You've already maxed out Animal Taming!", 65)
                    API.Stop()

                API.ClearJournal()

                # If there is no animal being tamed, try to find an animal to tame
                if self._animalBeingTamed == None:
                    self._animalBeingTamed = self._findAnimalToTame()
                    if self._animalBeingTamed == None:
                        API.Pause(0.5)
                        return
                    else:
                        API.HeadMsg(
                            "Found animal to tame", self._animalBeingTamed.Serial, 90
                        )

                # Check if animal is close enough to tame
                distance = Math.distanceBetween(API.Player, self._animalBeingTamed)
                if distance > self._maxDistance:
                    API.SysMsg("Animal moved too far away, ignoring for now", 1100)
                    self._animalBeingTamed = None
                    return
                elif self._animalBeingTamed != None and distance > 1:
                    self._followMobile(self._animalBeingTamed)
                    animal = API.FindMobile(self._animalBeingTamed.Serial)
                    isBlocked = False
                    lastCoordX = None
                    lastCoordY = None
                    count = 0
                    while animal and Math.distanceBetween(API.Player, self._animalBeingTamed) > 2 and not isBlocked:
                        if count >= 10:
                            isBlocked = True
                        hasMoved = False
                        if lastCoordX != API.Player.X:
                            lastCoordX = API.Player.X
                            hasMoved = True
                        if lastCoordY != API.Player.Y:
                            lastCoordY = API.Player.Y
                            hasMoved = True
                        if not hasMoved:
                            count += 1
                        animal = API.FindMobile(self._animalBeingTamed.Serial)
                        API.Pause(0.1)

                # Tame the animal if a tame is not currently being attempted and enough time has passed since last using Animal Taming
                if not self._isTaming:
                    self._tame()

            if self._isTaming:
                if self._animalBeingTamed and not Timer.exists(13, "Animal Taming"):
                    self._animalBeingTamed = None
                    self._isTaming = False
                    return
                self._followMobile(self._animalBeingTamed)
                self._animalBeingTamed = API.FindMobile(self._animalBeingTamed.Serial)
                if self._animalBeingTamed == None:
                    self._isTaming = False
                if API.InJournalAny(
                    ["It seems to accept you as master.", "That wasn't even challenging."]
                ):
                    Animal.rename(self._animalBeingTamed, "Tamed")
                    Animal.release(self._animalBeingTamed)
                    self._attackTamed(self._animalBeingTamed)
                    self._animalBeingTamed = None
                    self._isTaming = False
                elif API.InJournalAny(
                    [
                        "You fail to tame the creature.",
                        "The animal is too angry to continue taming.",
                        "You must wait a few moments to use another skill.",
                        "That is too far away.",
                        "You are too far away to continue taming.",
                        "Someone else is already taming that creature.",
                    ]
                ):
                    self._animalBeingTamed = None
                    self._isTaming = False

    def _tame(self):
        animal = API.FindMobile(self._animalBeingTamed.Serial)
        if not animal:
            return
        API.CancelTarget()
        API.PreTarget(self._animalBeingTamed.Serial)
        API.UseSkill("Animal Taming")
        Timer.create(13, "Animal Taming")
        self._isTaming = True

    def _pathfindToMobile(animalSerial):
        animal = API.FindMobile(animal.Serial)
        if animal:
            API.PathfindEntity(animal)

    def _followMobile(self, animal):
        animal = API.FindMobile(animal)
        if animal:
            API.AutoFollow(animal.Serial)

    def _attackTamed(self, animal):
        if not animal:
            return
        animal = API.FindMobile(animal.Serial)
        if not animal or animal.IsDead:
            return
        while animal and animal.Hits > 0 and not animal.IsDead:
            API.HeadMsg(f"Killing this animal", animal.Serial, 33)
            API.PreTarget(animal.Serial, "Harmful")
            spell = "Flamestrike"
            self._magic.cast(spell)
            API.Pause(3)
            animal = API.FindMobile(animal.Serial)

    def _getAnimalIDsAtOrOverTamingDifficulty(self):
        animalSkillInfo = Util.getSkillInfo("Animal Taming")["value"]
        animalList = []
        for animal in self._animals:
            if (
                animalSkillInfo >= self._animals[animal].minTamingSkill
                and animalSkillInfo < self._animals[animal].maxTamingSkill
            ):
                animalList.append(self._animals[animal].mobileID)
        return animalList

    def _findAnimalToTame(self):
        tameableAnimals = []
        animalIds = self._getAnimalIDsAtOrOverTamingDifficulty()
        for animalId in animalIds:
            animals = API.GetAllMobiles(
                animalId,
                self._maxDistance,
                [
                    API.Notoriety.Enemy,
                    API.Notoriety.Criminal,
                    API.Notoriety.Gray,
                    # API.Notoriety.Innocent,
                ],
            )
            for animal in animals:
                if self._hasPath(animal):
                    tameableAnimals.append(animal)
        if len(tameableAnimals) > 0:
            finalAnimal = None
            finalDistance = math.inf
            for tameableAnimal in tameableAnimals:
                distance = Math.distanceBetween(API.Player, tameableAnimal)
                if distance < finalDistance:
                    finalAnimal = tameableAnimal
                    finalDistance = distance
            return finalAnimal
        API.SysMsg("No animal")
        return None

    def _hasPath(self, animal):
        return API.GetPath(int(animal.X), int(animal.Y), distance=self._maxDistance + 4)

    def _checkSkill(self):
        animalSkillInfo = Util.getSkillInfo("Animal Taming")
        if animalSkillInfo["value"] < 31:
            API.SysMsg("Buy Taming Skill Up, stopping", 33)
            API.Stop()

    def _isRunning(self):
        return self._running


animalTaming = AnimalTaming()
animalTaming.main()
while animalTaming._isRunning():
    # animalTaming.gump.tick()
    # animalTaming.gump.tickSubGumps()
    animalTaming.tick()
    API.Pause(0.1)
#=========== End of .\Train\animal-taming.py ============#

