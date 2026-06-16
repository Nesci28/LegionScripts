import re
import time
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)

from Util import Util


class Bod:
    @staticmethod
    def _itemProps(item, includeProps=False, attempts=5):
        for _ in range(attempts):
            if includeProps:
                props = API.ItemNameAndProps(item.Serial, True)
            else:
                props = API.ItemNameAndProps(item.Serial)
            if props:
                return props.split("\n")
            API.Pause(0.1)
        raise ValueError("Could not read BOD properties")

    @staticmethod
    def findAllBodItems(selectedBodGraphic, selectedBodHue, isSmall):
        bods = []
        items = Util.itemsInContainer(API.Backpack)
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
        try:
            values = Bod._parse(item)
        except ValueError as e:
            API.SysMsg(str(e), 33)
            return True
        amountToFill = values["amountToFill"]
        if not values["isSmall"]:
            API.SysMsg("This function only works on small bod")
            API.Stop()
        amountAlreadyFilled = values["amountAlreadyFilled"]
        missingItem = amountToFill - amountAlreadyFilled - currentCount
        return missingItem <= 0

    @staticmethod
    def isFilled(item, isColoring=True):
        try:
            values = Bod._parse(item)
        except ValueError:
            return False
        isDone = False
        amountToFill = values["amountToFill"]
        if values["isSmall"]:
            amountAlreadyFilled = values["amountAlreadyFilled"]
            isDone = amountToFill - amountAlreadyFilled == 0
        if not values["isSmall"]:
            comparisonResults = []
            try:
                props = Bod._itemProps(item)
            except ValueError:
                return False
            for prop in reversed(props):
                if prop.strip().lower().startswith("amount to make"):
                    break
                parts = prop.rsplit(": ", 1)
                if len(parts) == 2:
                    value = int(parts[1])
                    comparisonResults.append(value == amountToFill)
            isDone = all(comparisonResults)
        # if isDone and isColoring:
        #     item.Hue = 33
        return isDone
    
    @staticmethod
    def isPartiallyFilled(item):
        try:
            values = Bod._parse(item)
        except ValueError:
            return False
        isDone = False
        amountToFill = values["amountToFill"]
        if values["isSmall"]:
            amountAlreadyFilled = values["amountAlreadyFilled"]
            isDone = amountToFill - amountAlreadyFilled == 0
            return not isDone and amountAlreadyFilled > 0

        comparisonResults = []
        try:
            props = Bod._itemProps(item)
        except ValueError:
            return False
        for prop in reversed(props):
            if prop.strip().lower().startswith("amount to make"):
                break
            parts = prop.rsplit(": ", 1)
            if len(parts) == 2:
                value = int(parts[1])
                comparisonResults.append(value == amountToFill)
        isPartiallyDone = any(comparisonResults)
        return isPartiallyDone

    @staticmethod
    def isMaxed(item):
        try:
            values = Bod._parse(item)
        except ValueError:
            return False
        isExceptional = values["isExceptional"]
        amountToFill = values["amountToFill"]
        isDone = isExceptional == True and amountToFill == 20
        # if isDone:
        #     item.Hue = 45
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
            "barbed leather",
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
        props = Bod._itemProps(item)
        isSmall = props[2 + 1] == "Small Bulk Order"
        itemName = None
        amountAlreadyFilled = 0
        amountToFill = None
        isExceptionalLine = props[4 + 1]
        isExceptional = isExceptionalLine != "Normal"
        material = Bod._getMaterial(props[3 + 1])
        resourceHue = None
        craftingInfoMaterial = None
        amountToMakeLine = props[5 + 1]
        match = re.search(r"Amount To Make:\s*(\d+)", amountToMakeLine)
        amountToFill = match.group(1)
        itemNameLine = props[6 + 1]
        match = re.search(r"([a-zA-Z '-]+):\s*(\d+)", itemNameLine)
        itemName = match.group(1).strip()
        if craftingInfo:
            resourceHue = craftingInfo["materialHues"][material]["hue"]
            craftingInfoMaterial = craftingInfo["materialHues"][material]
        if isSmall:

            amountAlreadyFilled = int(match.group(2))
        return {
            "itemName": itemName,
            "amountAlreadyFilled": amountAlreadyFilled,
            "amountToFill": int(amountToFill),
            "isExceptional": isExceptional,
            "resourceHue": resourceHue,
            "material": craftingInfoMaterial,
            "isSmall": isSmall,
            "isFilled": int(amountToFill) - amountAlreadyFilled == 0,
        }

    def __init__(self, bodSkill, item, craftingInfo=None, craft=None):
        self.item = item
        self.craftingInfo = craftingInfo
        self.bodSkill = bodSkill
        self.craft = craft
        self.count = 0
        self._setup()

    def turnIn(self):
        if not Bod.isFilled(self.item):
            return
        npcs = API.NearestMobiles([API.Notoriety.Invulnerable], 1)
        while len(npcs) == 0:
            API.SysMsg("No npcs found. move", 32)
            API.Pause(1)
            npcs = API.NearestMobiles([API.Notoriety.Invulnerable], 1)

        API.ClearJournal()
        while not API.InJournalAny(["$An offer may be available in about (.*) minutes."]):
            self._acceptBod(npcs)
            API.Pause(1)
        for npc in npcs:
            Util.moveItem(self.item.Serial, npc.Serial)
            # while not API.HasGump(17003):
            #     API.Pause(0.1)
            # API.ReplyGump(7, 17003)
            # while not API.HasGump(17000):
            #     API.Pause(0.1)
            # API.CloseGump(17000)
            self._acceptBod(npcs)
            API.Pause(1)
            break

    def bribe(self):
        while not Bod.isMaxed(self.item):
            npcs = API.NearestMobiles([API.Notoriety.Invulnerable], 1)
            while len(npcs) == 0:
                API.SysMsg("No npcs found. move", 32)
                API.Pause(1)
                npcs = API.NearestMobiles([API.Notoriety.Invulnerable], 1)
                return -1
            for npc in npcs:
                API.ClearJournal()
                API.ContextMenu(npc.Serial, 419)
                if not API.WaitForTarget("any", 1):
                    API.IgnoreObject(npc.Serial)
                    continue
                total = 0
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
                        API.ClearJournal()
                        while not self._findBridePrice():
                            Util.moveItem(self.item.Serial, npc.Serial)
                            API.Pause(0.1)
                        for journalEntry in API.JournalEntries:
                            match = re.search(r"([0-9][0-9,]*)\s+gold", journalEntry.Text, re.IGNORECASE)
                            if match:
                                total += int(match.group(1).replace(",", ""))
                        API.Pause(1)
                        break
                    API.Pause(0.1)
                return total

    def fill(self, onCraftAttempt=None):
        self._fillBod()
        if Bod.isFilled(self.item):
            return True
        if not self.isSmall:
            return True
        pendingAcceptedItems = 0

        if not self.craft or not self.craftingInfo:
            API.SysMsg(
                "A Craft Class and craftingInfo must be defined to fill a bod", 33
            )
            API.Stop()
            return False
        if hasattr(self.craft, "isBlocked"):
            self.craft.isBlocked = False
        # self.item.Hue = 18
        while not Bod.hasEnoughItem(self.item, pendingAcceptedItems):
            isValidItem = self.craft.craft(
                self.isExceptional,
                self.bodSkillItem,
                self.resourceHue,
                self.material,
            )
            if onCraftAttempt:
                onCraftAttempt()
            if isValidItem is None:
                self.craft.emptyResource()
                return False
            if isValidItem:
                craftedItem = getattr(self.craft, "lastCraftedItem", None)
                beforeFilledCount = self._amountAlreadyFilled()
                if not self._fillCraftedItem(craftedItem):
                    self.craft.emptyResource()
                    return False
                afterFilledCount = self._amountAlreadyFilled()
                if afterFilledCount > beforeFilledCount:
                    pendingAcceptedItems = 0
                else:
                    pendingAcceptedItems += 1
                self.count = pendingAcceptedItems
        Bod.isFilled(self.item)
        self.craft.emptyResource()
        return True

    def _acceptBod(self, npcs):
        for npc in npcs:
            API.ContextMenu(npc.Serial, 403)
            start_time = time.time()
            while not API.HasGump(455):
                if time.time() - start_time > 1:
                    API.SysMsg("Timeout", 33)
                    API.CancelTarget()
                    break
                API.Pause(0.1)
            API.ReplyGump(1, 455)

    def _amountAlreadyFilled(self):
        try:
            values = Bod._parse(self.item, self.craftingInfo)
            return values["amountAlreadyFilled"]
        except ValueError:
            return self.amountAlreadyFilled

    def _craftedItemAccepted(self, craftedItem):
        if not craftedItem:
            return None
        item = API.FindItem(craftedItem.Serial)
        return not item or item.Container != API.Backpack

    def _fillCraftedItem(self, craftedItem):
        self._fillBod()
        if self._craftedItemAccepted(craftedItem):
            return True

        if craftedItem:
            self._fillBod(craftedItem.Serial)
            if self._craftedItemAccepted(craftedItem):
                return True

        API.SysMsg(
            "Crafted {} but the BOD did not accept it; stopping fill.".format(
                self.itemName
            ),
            33,
        )
        if hasattr(self.craft, "isBlocked"):
            self.craft.isBlocked = True
        return False

    def _fillBod(self, targetSerial=None):
        while not API.HasGump(456):
            API.UseObject(self.item.Serial)
            API.Pause(0.1)
        API.ReplyGump(11, 456)
        if not API.WaitForTarget("any", 3):
            return False
        API.Target(targetSerial or API.Backpack)
        API.Pause(1)
        return True

    def _findBridePrice(self):
        return API.InJournal(r"$\d gold")

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
            self.bodSkillItem = dict(self.bodSkill["items"][values["itemName"]])
            self.bodSkillItem["name"] = values["itemName"]
        self.material = values["material"]
        self.isSmall = values["isSmall"]
