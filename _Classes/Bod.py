import re

import Util


class Bod:
    @staticmethod
    def findAllBodItems(selectedBodGraphic, selectedBodHue, isSmall):
        bods = []
        items = Util.Util.itemsInContainer(API.Backpack)
        for item in items:
            if item.Graphic != selectedBodGraphic or item.Hue != selectedBodHue:
                continue
            isSmallBod = Bod.isSmallBod(item)
            if isSmallBod and isSmall:
                bods.append(item)
            if not isSmallBod and not isSmall:
                bods.append(item)
        return bods

    @staticmethod
    def hasEnoughItem(item, currentCount):
        values = Bod._parse(item)
        amountToFill = values["amountToFill"]
        if not values["isSmall"]:
            API.SysMsg("This function only works on small bod")
            API.Stop()
        amountAlreadyFilled = values["amountAlreadyFilled"]
        missingItem = amountToFill - amountAlreadyFilled - currentCount
        return missingItem <= 0

    @staticmethod
    def isFilled(item, isColoring=True):
        values = Bod._parse(item)
        isDone = False
        amountToFill = values["amountToFill"]
        if values["isSmall"]:
            amountAlreadyFilled = values["amountAlreadyFilled"]
            isDone = amountToFill - amountAlreadyFilled == 0
        if not values["isSmall"]:
            comparisonResults = []
            props = API.ItemNameAndProps(item.Serial).split("\n")
            for prop in reversed(props):
                if prop.strip().lower().startswith("amount to make"):
                    break
                parts = prop.rsplit(": ", 1)
                if len(parts) == 2:
                    value = int(parts[1])
                    comparisonResults.append(value == amountToFill)
            isDone = all(comparisonResults)
        if isDone and isColoring:
            item.Hue = 33
        return isDone

    @staticmethod
    def isMaxed(item):
        values = Bod._parse(item)
        isExceptional = values["isExceptional"]
        amountToFill = values["amountToFill"]
        isDone = isExceptional == True and amountToFill == 20
        if isDone:
            item.Hue = 45
        return isDone

    @staticmethod
    def isSmallBod(item):
        try:
            values = Bod._parse(item)
            isSmall = values["isSmall"]
            return isSmall
        except:
            return False

    @staticmethod
    def _getMaterial(materialProp):
        materials = [
            "cloth",
            "spined leather",
            "horned leather",
            "gold",
            "dull copper",
            "shadow iron",
            "copper",
            "bronze",
            "verite",
            "valorite",
            "agapite",
            "iron",
        ]
        materialProp = materialProp.lower()
        for material in materials:
            if material in materialProp:
                return material
        match = re.search(r"made with ([a-z\s]+?) ingots?", materialProp)
        if match:
            possible = match.group(1).strip()
            return possible
        return None

    @staticmethod
    def _parse(item, craftingInfo=None):
        props = API.ItemNameAndProps(item.Serial).split("\n")
        isSmall = props[2 + 1] == "Small Bulk Order"
        itemName = None
        amountAlreadyFilled = None
        amountToFill = None
        isExceptionalLine = props[4 + 1]
        isExceptional = isExceptionalLine != "Normal"
        material = Bod._getMaterial(props[3 + 1])
        resourceHue = None
        craftingInfoMaterial = None
        amountToMakeLine = props[5 + 1]
        match = re.search(r"Amount To Make:\s*(\d+)", amountToMakeLine)
        amountToFill = match.group(1)
        if craftingInfo:
            resourceHue = craftingInfo["materialHues"][material]["hue"]
            craftingInfoMaterial = craftingInfo["materialHues"][material]
        if isSmall:
            itemNameLine = props[6 + 1]
            match = re.search(r"([a-zA-Z '-]+):\s*(\d+)", itemNameLine)
            itemName = match.group(1).strip()
            amountAlreadyFilled = int(match.group(2))
        return {
            "itemName": itemName,
            "amountAlreadyFilled": amountAlreadyFilled,
            "amountToFill": int(amountToFill),
            "isExceptional": isExceptional,
            "resourceHue": resourceHue,
            "material": craftingInfoMaterial,
            "isSmall": isSmall,
        }

    def __init__(self, bodSkill, item, craftingInfo=None, craft=None):
        self.item = item
        self.craftingInfo = craftingInfo
        self.bodSkill = bodSkill
        self.craft = craft
        self.count = 0
        self._setup()

    def bride(self):
        while not Bod.isMaxed(self.item):
            npcs = API.NearestMobiles([API.Notoriety.Invulnerable], 1)
            while len(npcs) == 0:
                API.SysMsg("No npcs found. move", 32)
                API.Pause(1)
                npcs = API.NearestMobiles([API.Notoriety.Invulnerable], 1)
            for npc in npcs:
                API.ClearJournal()
                API.ContextMenu(npc.Serial, 419)
                if not API.WaitForTarget("any", 1):
                    API.IgnoreObject(npc.Serial)
                    continue
                while True:
                    if API.InJournal("My business is being watched by the Guild"):
                        API.IgnoreObject(npc.Serial)
                        break
                    if API.InJournal(
                        "So you want to do a little business"
                    ) and API.WaitForTarget("any", 1):
                        API.ClearJournal()
                        API.Target(self.item.Serial)
                        while not self._findBridePrice():
                            API.Pause(0.1)
                        Util.Util.moveItem(self.item.Serial, npc.Serial)
                        API.Pause(1)
                        break
                    API.Pause(0.1)

    def fill(self):
        self._fillBod()
        Bod.isFilled(self.item)
        if not self.isSmall:
            return

        if not self.craft or not self.craftingInfo:
            API.SysMsg(
                "A Craft Class and craftingInfo must be defined to fill a bod", 33
            )
            API.Stop()
        self.item.Hue = 18
        while not Bod.hasEnoughItem(self.item, self.count):
            isValidItem = self.craft.craft(
                self.isExceptional,
                self.bodSkillItem,
                self.resourceHue,
                self.material,
            )
            if isValidItem:
                self.count += 1
        self._fillBod()
        Bod.isFilled(self.item)
        self.craft.emptyResource()

    def _fillBod(self):
        while not API.HasGump(456):
            API.UseObject(self.item.Serial)
            API.Pause(0.1)
        API.ReplyGump(11, 456)
        API.WaitForTarget()
        API.Target(API.Backpack)
        API.Pause(1)

    def _findBridePrice(self):
        if API.InJournal("0 gold coin"):
            API.SysMsg("0 Gold Coin")
            return True
        if API.InJournal("100 gold coin"):
            API.SysMsg("100 Gold Coin")
            return True
        if API.InJournal("200 gold coin"):
            API.SysMsg("200 Gold Coin")
            return True
        if API.InJournal("300 gold coin"):
            API.SysMsg("300 Gold Coin")
            return True
        if API.InJournal("400 gold coin"):
            API.SysMsg("400 Gold Coin")
            return True
        if API.InJournal("500 gold coin"):
            API.SysMsg("500 Gold Coin")
            return True
        if API.InJournal("600 gold coin"):
            API.SysMsg("600 Gold Coin")
            return True
        if API.InJournal("700 gold coin"):
            API.SysMsg("700 Gold Coin")
            return True
        if API.InJournal("800 gold coin"):
            API.SysMsg("800 Gold Coin")
            return True
        if API.InJournal("900 gold coin"):
            API.SysMsg("900 Gold Coin")
            return True
        if API.InJournal("1000 gold coin"):
            API.SysMsg("1000 Gold Coin")
            return True
        return False

    def _update(self):
        values = Bod._parse(self.item, self.craftingInfo)
        self.amountAlreadyFilled = values["amountAlreadyFilled"]
        self.amountToFill = values["amountToFill"]
        self.resourceHue = values["resourceHue"]
        self.isExceptional = values["isExceptional"]
        self.material = values["material"]

    def _setup(self):
        values = Bod._parse(self.item, self.craftingInfo)
        self.itemName = values["itemName"]
        self.amountToFill = values["amountToFill"]
        self.isExceptional = values["isExceptional"]
        self.amountAlreadyFilled = values["amountAlreadyFilled"]
        self.resourceHue = values["resourceHue"]
        if self.bodSkill and values["itemName"]:
            self.bodSkillItem = self.bodSkill["items"][values["itemName"]]
        self.material = values["material"]
        self.isSmall = values["isSmall"]
