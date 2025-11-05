#=========== Consolidated Imports ============#
from decimal import Decimal
import API
import System
import importlib
import os
import re
import sys


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

#=========== Start of .\Sea\high-seas.py ============#




# --- Global Variables ---
cannons = {
    "forwardPort": {},
    "amidshipsPort": {},
    "forwardStarboard": {},
    "amidshipsStarboard": {},
}

gumpIdConst = 888888


def getCannonInfo(gumpId):
    for info in cannons.values():
        if info.get("gumpId") == gumpId:
            return info
    raise Exception("Cannon not found for gumpId")


def getItemInBackpack(graphic):
    return API.FindType(graphic, API.Backpack)


def isCannonInState(gumpId, stateText):
    info = getCannonInfo(gumpId)
    if not API.HasGump(gumpId):
        API.UseObject(info["item"].Serial)
        API.Pause(1)
    return API.GumpContains(stateText, gumpId)


def waitForUniqueGump(item):
    startGump = API.HasGump()
    for _ in range(10):
        API.UseObject(item.Serial)
        API.Pause(1)
        if API.HasGump() != startGump:
            return API.HasGump()
    raise Exception("Unable to open unique gump for item")


# --- Main Logic ---
def setup():
    graphics = [0x4216, 0x4217, 0x4218, 0x4219]
    items = []
    for g in graphics:
        items += API.FindTypeAll(g, 4294967295, 2)

    if len(items) != 4:
        raise Exception("Must be standing in the middle of 4 cannons.")

    for item in items:
        gumpId = waitForUniqueGump(item)
        isForward = API.GumpContains("Forward")
        isPort = API.GumpContains("Port")
        position = "forward" if isForward else "amidships"
        side = "Port" if isPort else "Starboard"
        key = position + side
        cannons[key] = {"item": item, "serial": item.Serial, "gumpId": gumpId}


def reload():
    for info in cannons.values():
        for contained in API.ItemsInContainer(info["item"].Serial):
            Util.Util.moveItem(contained, API.Backpack)

    itemTypes = {"balls": 0x4224, "cords": 0x1420, "charges": 0xA2BE}
    items = {k: getItemInBackpack(v) for k, v in itemTypes.items()}
    counts = {k: floor(item.Amount / 4) for k, item in items.items()}

    for info in cannons.values():
        for kind in ["balls", "cords", "charges"]:
            Util.Util.moveItem(items[kind], info["item"], counts[kind])


def prep(gumpId):
    if API.GumpContains("PREP", gumpId):
        for _ in range(10):
            API.ReplyGump(1, gumpId)
            API.Pause(0.05)



def prepAll(side):
    for name, info in cannons.items():
        if side == "all" or side.lower() in name.lower():
            gumpId = info.get("gumpId")
            if not isCannonInState(gumpId, "FIRE"):
                prep(gumpId)
    API.SysMsg("Done Prepping")


def fireCannons(side):
    if side == "port":
        API.Msg("Fire Port Broadside")
    elif side == "starboard":
        API.Msg("Fire Starboard Broadside")
    API.Pause(2)
    prepAll(side)


# --- Gump UI ---
def sendGump():
    width = 240
    height = 120
    g = API.CreateGump(True, True)
    g.SetWidth(width)
    g.SetHeight(height)
    g.CenterXInViewPort()
    g.CenterYInViewPort()

    for x, y, w, h in [
        (-5, -5, width, 5),
        (-5, height - 10, width, 5),
        (-5, -5, 5, height),
        (width - 10, -5, 5, height),
    ]:
        border = API.CreateGumpColorBox(1, "#a86b32")
        border.SetX(x)
        border.SetY(y)
        border.SetWidth(w)
        border.SetHeight(h)
        g.Add(border)

    bg = API.CreateGumpColorBox(0.75, "#000000")
    bg.SetWidth(width - 10)
    bg.SetHeight(height - 10)
    g.Add(bg)

    buttonRows = [
        [("Left", fireCannons, "port"), ("Right (NPC)", fireCannons, "starboard")],
        [("Reload", reload, None), ("Prep", prepAll, "all")],
    ]

    yOffset = 10
    buttons = []

    for i, row in enumerate(buttonRows):
        y = yOffset + (45 * i)
        for j, (label, action, arg) in enumerate(row):
            x = 20 + (75 * j)
            btn = API.CreateGumpButton("", 996, 9722, 9721, 9721)
            btn.SetX(x)
            btn.SetY(y)
            g.Add(btn)
            buttons.append((btn, action, arg))

            lbl = API.CreateGumpLabel(label)
            lbl.SetX(x + 30)
            lbl.SetY(y)
            g.Add(lbl)

    statusLabel = API.CreateGumpLabel("")
    statusLabel.SetX(20)
    statusLabel.SetY(height - 30)
    g.Add(statusLabel)

    API.AddGump(g)

    while True:
        API.Pause(0.1)
        for btn, action, arg in buttons:
            if btn.IsClicked:
                statusLabel.Text = f"Running: {label}"
                try:
                    action(arg) if arg else action()
                except Exception as e:
                    API.SysMsg(f"Error: {str(e)}", 33)
                statusLabel.Text = ""  # Clear after action


# --- Entry Point ---
def main():
    setup()
    sendGump()


main()
#=========== End of .\Sea\high-seas.py ============#

