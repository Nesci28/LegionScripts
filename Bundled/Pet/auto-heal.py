#=========== Consolidated Imports ============#
from decimal import Decimal
import API
import System
import importlib
import os
import re
import sys
import time


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

#=========== Start of _Jsons\spell_def_magic.py ============#
SPELLS = [ {'castTime': 1, 'hasTarget': False, 'manaCost': 4, 'name': 'Create Food'},
  {'castTime': 1, 'hasTarget': False, 'manaCost': 4, 'name': 'Reactive Armor'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 4, 'name': 'Clumsy'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 4, 'name': 'Feeblemind'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 4, 'name': 'Heal'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 4, 'name': 'Magic Arrow'},
  {'castTime': 1, 'hasTarget': False, 'manaCost': 4, 'name': 'Night Sight'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 4, 'name': 'Weaken'},
  {'castTime': 1.25, 'hasTarget': True, 'manaCost': 6, 'name': 'Agility'},
  {'castTime': 1.25, 'hasTarget': True, 'manaCost': 6, 'name': 'Cunning'},
  {'castTime': 1.25, 'hasTarget': True, 'manaCost': 6, 'name': 'Cure'},
  {'castTime': 1.25, 'hasTarget': True, 'manaCost': 6, 'name': 'Harm'},
  {'castTime': 1.25, 'hasTarget': True, 'manaCost': 6, 'name': 'Magic Trap'},
  {'castTime': 1.25, 'hasTarget': True, 'manaCost': 6, 'name': 'Remove Trap'},
  {'castTime': 1.25, 'hasTarget': False, 'manaCost': 6, 'name': 'Protection'},
  {'castTime': 1.25, 'hasTarget': True, 'manaCost': 6, 'name': 'Strength'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Bless'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Fireball'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Magic Lock'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Poison'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Telekinesis'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Teleport'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Unlock'},
  { 'castTime': 1.75,
    'hasTarget': True,
    'manaCost': 11,
    'name': 'Wall of Stone'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 11, 'name': 'Arch Cure'},
  { 'castTime': 1.75,
    'hasTarget': False,
    'manaCost': 11,
    'name': 'Arch Protection'},
  {'castTime': 1.75, 'hasTarget': True, 'manaCost': 11, 'name': 'Curse'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 11, 'name': 'Fire Field'},
  {'castTime': 1.75, 'hasTarget': True, 'manaCost': 11, 'name': 'Greater Heal'},
  {'castTime': 1.75, 'hasTarget': True, 'manaCost': 11, 'name': 'Lightning'},
  {'castTime': 1.75, 'hasTarget': True, 'manaCost': 11, 'name': 'Mana Drain'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 11, 'name': 'Recall'},
  {'castTime': 5.5, 'hasTarget': True, 'manaCost': 14, 'name': 'Blade Spirits'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 14, 'name': 'Dispel Field'},
  {'castTime': 1.5, 'hasTarget': False, 'manaCost': 14, 'name': 'Incognito'},
  { 'castTime': 1.5,
    'hasTarget': False,
    'manaCost': 14,
    'name': 'Magic Reflection'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 14, 'name': 'Mind Blast'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 14, 'name': 'Paralyze'},
  {'castTime': 1.5, 'hasTarget': False, 'manaCost': 14, 'name': 'Poison Field'},
  { 'castTime': 9,
    'hasTarget': False,
    'manaCost': 14,
    'name': 'Summon Creature'},
  {'castTime': 1.75, 'hasTarget': True, 'manaCost': 20, 'name': 'Dispel'},
  {'castTime': 1.75, 'hasTarget': True, 'manaCost': 20, 'name': 'Energy Bolt'},
  {'castTime': 1.75, 'hasTarget': True, 'manaCost': 20, 'name': 'Explosion'},
  { 'castTime': 1.75,
    'hasTarget': False,
    'manaCost': 20,
    'name': 'Invisibility'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 20, 'name': 'Mark'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 20, 'name': 'Mass Curse'},
  { 'castTime': 1.75,
    'hasTarget': False,
    'manaCost': 20,
    'name': 'Paralyze Field'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 20, 'name': 'Reveal'},
  { 'castTime': 2,
    'hasTarget': False,
    'manaCost': 40,
    'name': 'Chain Lightning'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 40, 'name': 'Energy Field'},
  {'castTime': 2, 'hasTarget': True, 'manaCost': 40, 'name': 'Flamestrike'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 40, 'name': 'Gate Travel'},
  {'castTime': 2, 'hasTarget': True, 'manaCost': 40, 'name': 'Mana Vampire'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 40, 'name': 'Mass Dispel'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 40, 'name': 'Meteor Swarm'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 40, 'name': 'Polymorph'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 40, 'name': 'Earthquake'},
  { 'castTime': 2.25,
    'hasTarget': True,
    'manaCost': 50,
    'name': 'Energy Vortex'},
  {'castTime': 2.25, 'hasTarget': True, 'manaCost': 50, 'name': 'Resurrection'},
  { 'castTime': 2.25,
    'hasTarget': False,
    'manaCost': 50,
    'name': 'Air Elemental'},
  { 'castTime': 2.25,
    'hasTarget': False,
    'manaCost': 50,
    'name': 'Air Elemental'},
  { 'castTime': 2.25,
    'hasTarget': False,
    'manaCost': 50,
    'name': 'Summon Daemon'},
  { 'castTime': 2.25,
    'hasTarget': False,
    'manaCost': 50,
    'name': 'Earth Elemental'},
  { 'castTime': 2.25,
    'hasTarget': False,
    'manaCost': 50,
    'name': 'Fire Elemental'},
  { 'castTime': 2.25,
    'hasTarget': False,
    'manaCost': 50,
    'name': 'Water Elemental'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 14, 'name': 'Animate Dead'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 9, 'name': 'Blood Oath'},
  {'castTime': 1.5, 'hasTarget': False, 'manaCost': 11, 'name': 'Corpse Skin'},
  {'castTime': 0.75, 'hasTarget': False, 'manaCost': 7, 'name': 'Curse Weapon'},
  {'castTime': 0.75, 'hasTarget': False, 'manaCost': 7, 'name': 'Evil Omen'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 11, 'name': 'Horrific Beast'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 23, 'name': 'Lich Form'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 17, 'name': 'Mind Rot'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 10, 'name': 'Pain Spike'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 17, 'name': 'Poison Strike'},
  {'castTime': 2, 'hasTarget': True, 'manaCost': 23, 'name': 'Strangle'},
  {'castTime': 2, 'hasTarget': True, 'manaCost': 24, 'name': 'Summon Familiar'},
  { 'castTime': 2,
    'hasTarget': False,
    'manaCost': 24,
    'name': 'Vampiric Embrace'},
  { 'castTime': 2,
    'hasTarget': False,
    'manaCost': 20,
    'name': 'Vengeful Spirit'},
  {'castTime': 1.5, 'hasTarget': False, 'manaCost': 20, 'name': 'Wither'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 17, 'name': 'Wraith Form'},
  {'castTime': 2, 'hasTarget': True, 'manaCost': 17, 'name': 'Exorcism'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 10, 'name': 'Cleanse by Fire'},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 10, 'name': 'Close Wounds'},
  { 'castTime': 0.5,
    'hasTarget': False,
    'manaCost': 7,
    'name': 'Consecrate Weapon'},
  {'castTime': 0.25, 'hasTarget': False, 'manaCost': 5, 'name': 'Dispel Evil'},
  {'castTime': 1, 'hasTarget': False, 'manaCost': 9, 'name': 'Divine Fury'},
  {'castTime': 0.5, 'hasTarget': False, 'manaCost': 11, 'name': 'Enemy of One'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 14, 'name': 'Holy Light'},
  { 'castTime': 1.5,
    'hasTarget': False,
    'manaCost': 20,
    'name': 'Noble Sacrifice'},
  {'castTime': 1.5, 'hasTarget': False, 'manaCost': 20, 'name': 'Remove Curse'},
  { 'castTime': 1.5,
    'hasTarget': False,
    'manaCost': 20,
    'name': 'Sacred Journey'},
  { 'castTime': 0.5,
    'hasTarget': False,
    'manaCost': 24,
    'name': 'Arcane Circle'},
  {'castTime': 3, 'hasTarget': True, 'manaCost': 20, 'name': 'Gift of Renewal'},
  { 'castTime': 1,
    'hasTarget': False,
    'manaCost': 10,
    'name': 'Immolating Weapon'},
  {'castTime': 1, 'hasTarget': False, 'manaCost': 11, 'name': 'Attune Weapon'},
  {'castTime': 1.5, 'hasTarget': False, 'manaCost': 14, 'name': 'Thunderstorm'},
  { 'castTime': 1.5,
    'hasTarget': False,
    'manaCost': 24,
    'name': "Nature's Fury"},
  {'castTime': 1.5, 'hasTarget': True, 'manaCost': 20, 'name': 'Summon Fey'},
  {'castTime': 2, 'hasTarget': True, 'manaCost': 24, 'name': 'Summon Fiend'},
  {'castTime': 2.5, 'hasTarget': False, 'manaCost': 24, 'name': 'Reaper Form'},
  {'castTime': 2.5, 'hasTarget': False, 'manaCost': 32, 'name': 'Wildfire'},
  { 'castTime': 3,
    'hasTarget': False,
    'manaCost': 32,
    'name': 'Essence of Wind'},
  {'castTime': 3, 'hasTarget': False, 'manaCost': 32, 'name': 'Dryad Allure'},
  { 'castTime': 3.5,
    'hasTarget': False,
    'manaCost': 40,
    'name': 'Ethereal Voyage'},
  {'castTime': 3.5, 'hasTarget': True, 'manaCost': 40, 'name': 'Word of Death'},
  {'castTime': 4, 'hasTarget': True, 'manaCost': 40, 'name': 'Gift of Life'},
  { 'castTime': 3,
    'hasTarget': False,
    'manaCost': 24,
    'name': 'Arcane Empowerment'},
  {'castTime': 1, 'hasTarget': True, 'manaCost': 9, 'name': 'Nether Bolt'},
  { 'castTime': 5.5,
    'hasTarget': False,
    'manaCost': 12,
    'name': 'Healing Stone'},
  {'castTime': 1.5, 'hasTarget': False, 'manaCost': 14, 'name': 'Purge Magic'},
  {'castTime': 0.75, 'hasTarget': False, 'manaCost': 10, 'name': 'Enchant'},
  {'castTime': 1.75, 'hasTarget': False, 'manaCost': 17, 'name': 'Sleep'},
  { 'castTime': 1.75,
    'hasTarget': False,
    'manaCost': 17,
    'name': 'Eagle Strike'},
  { 'castTime': 2,
    'hasTarget': False,
    'manaCost': 24,
    'name': 'Animated Weapon'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 20, 'name': 'Stone Form'},
  { 'castTime': 5.5,
    'hasTarget': False,
    'manaCost': 50,
    'name': 'Spell Trigger'},
  {'castTime': 2, 'hasTarget': False, 'manaCost': 24, 'name': 'Mass Sleep'},
  { 'castTime': 2,
    'hasTarget': False,
    'manaCost': 24,
    'name': 'Cleansing Winds'},
  {'castTime': 2.75, 'hasTarget': False, 'manaCost': 30, 'name': 'Bombard'},
  {'castTime': 2.5, 'hasTarget': False, 'manaCost': 24, 'name': 'Spell Plague'},
  {'castTime': 2.5, 'hasTarget': False, 'manaCost': 28, 'name': 'Hail Storm'},
  { 'castTime': 2.75,
    'hasTarget': True,
    'manaCost': 30,
    'name': 'Nether Cyclone'},
  { 'castTime': 2.75,
    'hasTarget': True,
    'manaCost': 40,
    'name': 'Rising Colossus'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 4, 'name': 'Inspire'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 4, 'name': 'Invigorate'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 4, 'name': 'Resilience'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 4, 'name': 'Perseverance'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 4, 'name': 'Tribulation'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 4, 'name': 'Despair'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 6, 'name': 'Death Ray'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 6, 'name': 'Ethereal Burst'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 6, 'name': 'Nether Blast'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 4, 'name': 'Mystic Weapon'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 6, 'name': 'Command Undead'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 6, 'name': 'Conduit'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 6, 'name': 'Mana Shield'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 6, 'name': 'Summon Reaper'},
  { 'castTime': 0,
    'hasTarget': False,
    'manaCost': 3,
    'name': 'Honorable Execution'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 3, 'name': 'Counter Attack'},
  { 'castTime': 0,
    'hasTarget': False,
    'manaCost': 3,
    'name': 'Lightning Strike'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 3, 'name': 'Confidence'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 3, 'name': 'Evasion'},
  {'castTime': 0, 'hasTarget': False, 'manaCost': 3, 'name': 'Momentum Strike'}]
#=========== End of _Jsons\spell_def_magic.py ============#

#=========== Start of _Utils\Magic.py ============#







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

#=========== Start of .\Pet\auto-heal.py ============#






# Settings
useMagery = True
useMageryHighHP = True
useVet = False
bandageSerial = API.Backpack

petSerials = []
petMobiles = []
magic = Magic()

# -- Movement Detection --
def isMoving():
    return API.Player.IsWalking

# -- Targeted Cast --
def castAtTarget(spell, level, targetSerial, poisonCheck=0):
    mob = API.FindMobile(targetSerial)
    if not mob or Math.distanceBetween(API.Player, mob) > 10:
        return False
    if poisonCheck == 1 and not mob.IsPoisoned:
        return False
    if poisonCheck == -1 and mob.IsPoisoned:
        return False
    # API.PreTarget(targetSerial, "beneficial")
    API.CastSpell(spell)
    API.WaitForTarget()
    API.Target(targetSerial)
    return True

# -- HP Percent Helper --
def mobilePercentHP(mob):
    return min(100, int((mob.Hits / 25.0) * 100))

# -- Pet Management --
def findMyPets():
    global petSerials
    petSerials.clear()
    for mob in API.GetAllMobiles():
        if mob.IsRenamable and not mob.IsHuman:
            petSerials.append(mob.Serial)
    if petSerials:
        for s in petSerials:
            mob = API.FindMobile(s)
            if mob:
                API.HeadMsg(f"Pet Located: {mob.Name}", s)

def rebuildPetList():
    global petMobiles
    petMobiles.clear()
    for s in petSerials:
        m = API.FindMobile(s)
        if m:
            petMobiles.append(m)

# -- Healing Logic --
def curePets(healthPercent):
    if isMoving() or not useMagery or API.Player.Mana < 15 or API.BuffExists("Veterinary"):
        return False
    rebuildPetList()
    for mob in petMobiles:
        if mob.IsPoisoned and mobilePercentHP(mob) < healthPercent and Math.distanceBetween(API.Player, mob) <= 10:
            return castAtTarget("Arch Cure", 4, mob.Serial, 1)
    return False

def healPets(healthPercent):
    if isMoving() or not useMagery or API.Player.Mana < 15 or API.BuffExists("Veterinary"):
        return False
    rebuildPetList()
    for mob in petMobiles:
        isGhost = mob.Hits == 0
        if not isGhost and not mob.IsPoisoned and mobilePercentHP(mob) < healthPercent and Math.distanceBetween(API.Player, mob) <= 10:
            return castAtTarget("Greater Heal", 4, mob.Serial, -1)
    return False

def vetPets(healthPercent):
    if not useVet or API.BuffExists("Veterinary"):
        return False
    rebuildPetList()
    for mob in petMobiles:
        if Math.distanceBetween(API.Player, mob) > 2:
            continue
        if mobilePercentHP(mob) >= healthPercent and not mob.IsPoisoned:
            continue
        bandage = API.FindType(0x0E21, bandageSerial)
        if bandage:
            API.UseObject(bandage.Serial)
            if API.WaitForTarget("Beneficial", 2):
                API.Target(mob.Serial)
            API.Pause(0.25)
            return True
    return False

def usePriority():
    if vetPets(80): return True
    if curePets(50): return True
    if healPets(50): return True
    if curePets(95): return True
    if useMageryHighHP and healPets(90): return True
    if vetPets(90): return True
    return False

# -- Initialization --
findMyPets()
API.HeadMsg("Heal Pets Ready!", API.Player)

# -- Main Loop --
while not API.StopRequested:
    if not API.Player.IsDead:
        while petSerials:
            rebuildPetList()
            if not petMobiles:
                break
            if usePriority():
                API.Pause(0.4)
                continue
            API.Pause(0.4)
        findMyPets()
        API.Pause(0.5)
    else:
        API.Pause(1.0)
#=========== End of .\Pet\auto-heal.py ============#

