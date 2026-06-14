import API
import importlib
import traceback
import time
import re
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Bod
import Gump
import Util
import Math
import Magic
import Python
import Error
import Craft
import Item
import Debug

importlib.reload(Bod)
importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Magic)
importlib.reload(Python)
importlib.reload(Error)
importlib.reload(Craft)
importlib.reload(Item)
importlib.reload(Debug)

from Bod import Bod
from Gump import Gump
from Util import Util
from Math import Math
from Magic import Magic
from Python import Python
from Error import Error
from Craft import Craft
from Item import Item

from bod_skills import bodSkillsStr
from crafting_infos import craftingInfosStr

TAILORING_BOD_BOOK_GRAPHICS = [0x2259]
TAILORING_BOD_BOOK_TEXT = "bulk order book"
TAILORING_CLOTH_RESOURCE_GRAPHIC = 0x1766
TAILORING_LEATHER_NAME_MARKERS = [
    "Leather ",
    " Leather ",
]
TAILORING_SORT_CATEGORIES = {
    "Leather": [
        "Leather Cap",
        "Leather Gloves",
        "Leather Gorget",
        "Leather Leggings",
        "Leather Sleeves",
        "Leather Tunic",
    ],
    "Studded": [
        "Studded Gorget",
    ],
    "Bone": [
        "Bone Armor",
        "Bone Arms",
        "Bone Gloves",
        "Bone Helmet",
        "Bone Leggings",
    ],
    "Footwear": [
        "Boots",
        "Sandals",
        "Shoes",
        "Thigh Boots",
    ],
}
TAILORING_FOOTWEAR_ITEMS = ["Boots", "Sandals", "Shoes", "Thigh Boots"]


class BodBot:
    def __init__(self):
        self._running = True
        self.gump = None
        self.scrollArea = None
        self.checkboxes = []
        self.typeCheckboxes = []
        self.containerSerial = API.GetSharedVar("BOD_BOT_CONTAINER_SERIAL") or None
        self.tailorSerial = API.GetSharedVar("BOD_BOT_TAILOR_SERIAL") or None
        self.runebookSerial = API.GetSharedVar("BOD_BOT_RUNEBOOK_SERIAL") or None
        self.beetleSerial = API.GetSharedVar("BOD_BOT_BEETLE_SERIAL") or None
        self.sortChestSerials = API.GetSharedVar("BOD_BOT_SORT_CHEST_SERIALS") or []
        self.bodCountLabel = None
        self.totalLabel = None
        self.clothUsedLabel = None
        self.total = 0
        self.clothUsed = 0
        self.runebookItem = API.GetSharedVar("BOD_BOT_RUNEBOOK_ITEM") or None
        self.beetleMobile = API.GetSharedVar("BOD_BOT_BEETLE_MOBILE") or None

        self.bodSkills = Math.convertToHex(bodSkillsStr)
        self.craftingInfos = Math.convertToHex(craftingInfosStr)
        self.selectedProfession = (
            API.GetSharedVar("BOD_BOT_SELECTED_PROFESSION") or "Tailoring"
        )
        self.selectedType = API.GetSharedVar("BOD_BOT_SELECTED_TYPE") or "Small"
        self.bodSkill = self.bodSkills[self.selectedProfession]
        self.professions = self.bodSkills.keys()
        self.selectedBodGraphic = None
        self.selectedBodHue = None

        self.bodInfos = []
        self.largeBods = []

    def main(self):
        try:
            Util.openContainer(API.Backpack)
            self._showGump()
        except Exception as e:
            API.SysMsg(f"BodBot e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def _showGump(self):
        width = 455
        height = 680
        g = Gump(width, height, self._onClose, gumpId=0xB0D001)
        self.gump = g
        g.addTitle("TAILORING & RESOURCES")

        categoriesPanel = g.addPanel(10, 42, 220, 118, "Crafting Categories")
        categoriesX = categoriesPanel["x"]
        categoriesY = categoriesPanel["y"] + 3

        for i, profession in enumerate(self.professions):
            label = profession.capitalize()
            rowY = categoriesY + i * 27
            g.addRow(categoriesX - 2, rowY - 3, categoriesPanel["width"] + 4, 24, self.selectedProfession == label)
            checkbox = g.addRadio(
                label,
                categoriesX,
                rowY,
                1,
                self.selectedProfession == label,
                self.gump.onClick(
                    lambda profession=profession: self._onProfessionClicked(profession)
                ),
            )
            self.checkboxes.append({"label": label, "checkbox": checkbox})

        bodTypesPanel = g.addPanel(238, 42, width - 248, 118, "BOD Categories")
        for i, type in enumerate(["Small", "Large"]):
            rowY = bodTypesPanel["y"] + 5 + i * 28
            g.addRow(bodTypesPanel["x"] + 2, rowY - 3, bodTypesPanel["width"] - 4, 24, self.selectedType == type)
            checkbox = g.addRadio(
                type,
                bodTypesPanel["x"] + 4,
                rowY,
                2,
                self.selectedType == type,
                self.gump.onClick(lambda type=type: self._onTypeClicked(type)),
            )
            self.typeCheckboxes.append({"label": type, "checkbox": checkbox})

        settingsPanel = g.addPanel(10, 168, width - 20, 156, "Settings")
        radioX = settingsPanel["x"] + 4
        textX = settingsPanel["x"] + 26
        y = settingsPanel["y"] + 4

        selectResourceContainerText = "Select resource container"
        if self.containerSerial:
            selectResourceContainerText = (
                f"Selected resource container ({self.containerSerial})"
            )
        resourceLabel = g.addLabel(selectResourceContainerText, textX, y)
        g.addButton(
            "",
            radioX,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda resourceLabel=resourceLabel: self._onContainerSelectionClicked(
                    resourceLabel
                )
            ),
        )

        y += 20
        selectNpcText = "Select npc"
        if self.tailorSerial:
            selectNpcText = f"Selected npc ({self.tailorSerial})"
        npcLabel = g.addLabel(selectNpcText, textX, y)
        g.addButton(
            "",
            radioX,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda npcLabel=npcLabel: self._onNpcSelectionClicked(npcLabel)
            ),
        )

        y += 20
        selectRunebookText = "Select runebook"
        if self.runebookSerial:
            selectRunebookText = f"Selected runebook ({self.runebookSerial})"
        runebookLabel = g.addLabel(selectRunebookText, textX, y)
        g.addButton(
            "",
            radioX,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda npcLabel=runebookLabel: self._onRunebookSelectionClicked(
                    npcLabel
                )
            ),
        )

        y += 20
        selectBeetleText = "Select Beetle"
        if self.beetleSerial:
            selectBeetleText = f"Selected Beetle ({self.beetleSerial})"
        beetleLabel = g.addLabel(selectBeetleText, textX, y)
        g.addButton(
            "",
            radioX,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda beetleLabel=beetleLabel: self._onBeetleSelectionClicked(
                    beetleLabel
                )
            ),
        )
        g.addButton(
            "CLOTH",
            settingsPanel["x"] + settingsPanel["width"] - 77,
            y - 3,
            "default",
            self.gump.onClick(lambda: self._onClothClicked()),
            True,
            72,
        )

        y += 20
        sortChestText = f"BOD sort chests: {len(self.sortChestSerials)}"
        sortChestLabel = g.addLabel(sortChestText, textX, y)
        g.addButton(
            "",
            radioX,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda sortChestLabel=sortChestLabel: self._onSortChestSelectionClicked(
                    sortChestLabel
                )
            ),
        )
        g.addButton(
            "CLEAR",
            settingsPanel["x"] + settingsPanel["width"] - 77,
            y - 3,
            "default",
            self.gump.onClick(
                lambda sortChestLabel=sortChestLabel: self._onClearSortChestsClicked(
                    sortChestLabel
                )
            ),
            True,
            72,
        )

        listPanelY = settingsPanel["y"] + settingsPanel["height"] + 8
        listPanelBottom = 588
        listPanel = g.addPanel(
            10, listPanelY, width - 20, listPanelBottom - listPanelY, "Fill Status & Items"
        )
        x = listPanel["x"]
        y = listPanel["y"] + 2
        footerHeight = 32

        g.addLabel("Filled", x, y)
        x += 40
        g.addLabel("Partial", x, y)
        x += 50
        g.addLabel("Maxed", x, y)
        x += 47
        g.addLabel(f"Items ({self.selectedProfession})", x, y)
        x += 185
        g.addLabel("Mark", x, y)

        self.scrollArea = g.addScrollArea(
            listPanel["x"], y + 18, listPanel["width"], listPanel["height"] - footerHeight - 22
        )

        footerY = listPanel["y"] + listPanel["height"] - footerHeight
        g.addColorBox(listPanel["x"], footerY, 1, listPanel["width"], Gump.theme["panelHeaderLine"], 0.85)
        g.addColorBox(listPanel["x"], footerY + 1, footerHeight - 1, listPanel["width"], Gump.theme["statusBg"], 0.92, withTexture=True)
        g.addColorBox(listPanel["x"] + int(listPanel["width"] / 2), footerY + 4, footerHeight - 8, 1, Gump.theme["panelHeaderLine"], 0.55)

        bodCountLabel = g.addLabel("BOD COUNT: 0", listPanel["x"] + 12, footerY + 9)
        self.bodCountLabel = bodCountLabel

        clothUsedLabel = g.addLabel("CLOTH USED: 0", listPanel["x"] + 145, footerY + 9)
        self.clothUsedLabel = clothUsedLabel

        totalLabel = g.addLabel("BRIBE: 0", listPanel["x"] + int(listPanel["width"] / 2) + 114, footerY + 9)
        self.totalLabel = totalLabel

        x = 24
        y = 604
        for actionLabel, action in [
            ("BRIBE", "Bribe"),
            ("FILL", "Fill"),
            ("SORT", "Sort"),
            ("TURN IN", "Turn in"),
            ("RESCAN", "Rescan"),
        ]:
            g.addButton(
                actionLabel,
                x,
                y,
                "default",
                self.gump.onClick(lambda action=action: self._onActionClicked(action)),
                True,
                70,
            )
            x += 80

        self.gump.create()
        self.gump.setStatus("Opening...")
        self.gump.pendingCallbacks.append(self._initialScan)

    def _initialScan(self):
        self.gump.setStatus("Scanning BODs...")
        self._scan()
        self.gump.setStatus("Ready.")

    def _onActionClicked(self, action):
        if action == "Bribe":
            self._bribe()
        if action == "Fill":
            self._fill()
        if action == "Sort":
            self._sortBods()
        if action == "Turn in":
            self._turnIn()
        if action == "Rescan":
            self._scan()

    def _getFilledBods(self):
        selectedBodGraphic = self.bodSkill["bod"]["graphic"]
        selectedBodHue = self.bodSkill["bod"]["hue"]
        isSmall = self.selectedType == "Small"

        bodItems = Bod.findAllBodItems(selectedBodGraphic, selectedBodHue, isSmall)
        filledBodItems = []
        for bodItem in bodItems:
            if Bod.isFilled(bodItem):
                filledBodItems.append(bodItem)
        return filledBodItems

    def _turnIn(self):
        if not self.npcSerial:
            return
        npc = API.FindMobile(self.npcSerial)
        distance = Math.distanceBetween(API.Player, npc)
        if distance > 1:
            return
        self.gump.setStatus("Turn In...")
        counter = 0
        filledBods = self._getFilledBods()
        while len(filledBods) > 0:
            counter += 1
            self.gump.setStatus(f"Turn In... {counter}/{len(filledBods)}")
            filledBod = filledBods.pop()
            Util.moveItem(filledBod.Serial, self.npcSerial)
            # isStillInBackpack = API.FindItem(filledBod.Serial)
            # API.SysMsg(str(isStillInBackpack))
            # if isStillInBackpack.Serial != 0:
            #     filledBods = self._getFilledBods()
            #     continue
            count = 0
            while not API.HasGump(455) and count < 5:
                API.ContextMenu(self.npcSerial, 403)
                API.Pause(0.1)
                count += 1
                API.SysMsg(str(count))
            if API.HasGump(455):
                API.ReplyGump(1, 455)
            filledBods = self._getFilledBods()
            API.Pause(2)
        self.gump.setStatus("Ready")

    def _sortBods(self):
        if self.selectedProfession != "Tailoring":
            self.gump.setStatus("BOD sorting is Tailoring-only for now.", 33)
            return
        if not self.sortChestSerials:
            self.gump.setStatus("Select at least one BOD sort chest.", 33)
            return

        self.gump.setStatus("Sorting BODs...")
        moved = 0
        skipped = 0
        bodItems = self._findLooseTailoringBods()

        bodsByCategory = {}
        for bodItem in bodItems:
            category = self._getTailoringSortCategory(bodItem)
            if category:
                bodsByCategory.setdefault(category, []).append(bodItem)
            else:
                skipped += 1

        for category, categoryBods in bodsByCategory.items():
            targetBooks = self._findSortBooks(category)
            if not targetBooks:
                skipped += len(categoryBods)
                API.SysMsg(f"No BOD book found for {category}.", 33)
                continue

            remainingBods = list(categoryBods)
            for targetBook in targetBooks:
                if not remainingBods:
                    break

                sourceChestSerial = targetBook.Container
                self.gump.setStatus(f"Sorting {category}...")
                Util.moveItem(targetBook.Serial, API.Backpack)
                if not self._waitForContainer(targetBook.Serial, API.Backpack):
                    continue

                stillRemaining = []
                storedInBook = 0
                for bodItem in remainingBods:
                    Util.moveItem(bodItem.Serial, targetBook.Serial)
                    if self._waitForBodStored(bodItem.Serial, targetBook.Serial):
                        moved += 1
                        storedInBook += 1
                    else:
                        stillRemaining.append(bodItem)

                Util.moveItem(targetBook.Serial, sourceChestSerial)
                self._waitForContainer(targetBook.Serial, sourceChestSerial)

                remainingBods = stillRemaining
                if storedInBook == 0:
                    API.SysMsg(f"{category} book accepted no BODs.", 33)

            skipped += len(remainingBods)

        audit = self._auditLooseTailoringBods()
        report = (
            f"Sorted {moved}; cloth left {audit['cloth']}; unknown {audit['unknown']}."
        )
        self._scan(statusOverride=report)

    def _findLooseTailoringBods(self):
        bodSkill = self.bodSkills["Tailoring"]
        bodGraphic = bodSkill["bod"]["graphic"]
        bodHue = bodSkill["bod"]["hue"]
        bodItems = []
        bodItems += Bod.findAllBodItems(bodGraphic, bodHue, True)
        bodItems += Bod.findAllBodItems(bodGraphic, bodHue, False)
        return bodItems

    def _auditLooseTailoringBods(self):
        audit = {
            "total": 0,
            "cloth": 0,
            "classified": 0,
            "unknown": 0,
            "unknownNames": {},
        }
        for bodItem in self._findLooseTailoringBods():
            audit["total"] += 1
            try:
                values = Bod._parse(bodItem)
            except Exception:
                if self._isTailoringClothBod(bodItem):
                    audit["cloth"] += 1
                else:
                    audit["unknown"] += 1
                    self._addUnknownBodAudit(audit, bodItem, None)
                continue

            if self._getTailoringSortCategory(bodItem):
                audit["classified"] += 1
            elif self._isTailoringClothBod(bodItem, values):
                audit["cloth"] += 1
            else:
                audit["unknown"] += 1
                self._addUnknownBodAudit(audit, bodItem, values)
        return audit

    def _addUnknownBodAudit(self, audit, bodItem, parsedBod):
        itemNames = self._getTailoringBodItemNames(bodItem)
        if parsedBod and parsedBod["itemName"] and not itemNames:
            itemNames = [parsedBod["itemName"]]
        label = ", ".join(itemNames) if itemNames else f"serial {bodItem.Serial}"
        audit["unknownNames"][label] = audit["unknownNames"].get(label, 0) + 1
        API.SysMsg(f"Unknown Tailoring BOD: {label}", 33)

    def _isTailoringClothBod(self, bodItem, parsedBod=None):
        if self._getTailoringBodMaterial(bodItem) == "cloth":
            return True

        itemNames = self._getTailoringBodItemNames(bodItem)
        if parsedBod and parsedBod["itemName"] and not itemNames:
            itemNames = [parsedBod["itemName"]]
        if not itemNames:
            return False

        for itemName in itemNames:
            itemInfo = self.bodSkills["Tailoring"]["items"].get(itemName)
            if not itemInfo:
                return False

            resources = itemInfo.get("resources", [])
            if not resources:
                return False

            isClothItem = all(
                resource.get("graphic") == TAILORING_CLOTH_RESOURCE_GRAPHIC
                for resource in resources
            )
            if not isClothItem:
                return False

        return True

    def _getTailoringBodMaterial(self, bodItem):
        props = API.ItemNameAndProps(bodItem.Serial).split("\n")
        for prop in props:
            prop = prop.strip()
            if prop.lower().startswith("amount to make"):
                break
            material = Bod._getMaterial(prop)
            if material:
                return material
        return None

    def _getTailoringSortCategory(self, bodItem):
        try:
            values = Bod._parse(bodItem)
        except Exception:
            return None

        itemNames = self._getTailoringBodItemNames(bodItem)
        if values["itemName"] and not itemNames:
            itemNames = [values["itemName"]]
        if not itemNames:
            return None

        typeName = "Small" if values["isSmall"] else "Large"
        categories = []
        for itemName in itemNames:
            categoryName = self._getTailoringItemCategory(itemName)
            if not categoryName:
                return None
            categories.append(categoryName)

        if len(set(categories)) == 1:
            return f"{categories[0]} {typeName}"
        if len(set(categories)) > 1:
            return f"Mixed {typeName}"
        return None

    def _getTailoringBodItemNames(self, bodItem):
        props = API.ItemNameAndProps(bodItem.Serial).split("\n")
        itemNames = []
        isReadingItems = False
        for prop in props:
            prop = prop.strip()
            if prop.lower().startswith("amount to make"):
                isReadingItems = True
                continue
            if not isReadingItems:
                continue

            match = re.search(r"([a-zA-Z '-]+):\s*(\d+)", prop)
            if match:
                itemNames.append(match.group(1).strip())

        return itemNames

    def _getTailoringItemCategory(self, itemName):
        if itemName in TAILORING_FOOTWEAR_ITEMS:
            return "Footwear"
        if itemName.startswith("Bone "):
            return "Bone"
        if itemName.startswith("Studded "):
            return "Studded"
        if any(marker in itemName for marker in TAILORING_LEATHER_NAME_MARKERS):
            return "Leather"
        return None

    def _findSortBooks(self, category):
        categoryWords = category.lower().split()
        books = []
        for chestSerial in self.sortChestSerials:
            chest = API.FindItem(chestSerial)
            if not chest:
                continue
            Util.openContainer(chest)
            for item in Util.itemsInContainer(chestSerial):
                props = API.ItemNameAndProps(item.Serial, True).lower()
                if not self._isBodBook(item, props):
                    continue
                if all(word in props for word in categoryWords):
                    books.append(item)
        return books

    def _isBodBook(self, item, props):
        return (
            item.Graphic in TAILORING_BOD_BOOK_GRAPHICS
            or TAILORING_BOD_BOOK_TEXT in props
        )

    def _waitForContainer(self, itemSerial, containerSerial, timeout=3):
        start = time.time()
        while time.time() - start < timeout:
            item = API.FindItem(itemSerial)
            if item and item.Container == containerSerial:
                return True
            API.Pause(0.1)
        return False

    def _waitForBodStored(self, bodSerial, bookSerial, timeout=3):
        start = time.time()
        while time.time() - start < timeout:
            item = API.FindItem(bodSerial)
            if not item or item.Container == bookSerial or item.Container != API.Backpack:
                return True
            API.Pause(0.1)
        return False

    def _fill(self):
        if not self.containerSerial:
            return
        resourceChest = API.FindItem(self.containerSerial)
        distance = Math.distanceBetween(API.Player, resourceChest)
        if distance > 1:
            return
        self.gump.setStatus("Filling...")
        self.clothUsed = 0
        self._setClothUsedLabel()
        counter = 0
        for bodInfo in self.bodInfos:
            isFilled = Bod.isFilled(bodInfo["bod"].item)
            if not isFilled:
                counter += 1
        currentCounter = 0
        lastClothCount = self._countAvailableCloth(resourceChest)

        def updateClothUsed():
            nonlocal lastClothCount
            currentClothCount = self._countAvailableCloth(resourceChest)
            self.clothUsed += max(0, lastClothCount - currentClothCount)
            lastClothCount = currentClothCount
            self._setClothUsedLabel()

        for bodInfo in self.bodInfos:
            isFilled = Bod.isFilled(bodInfo["bod"].item)
            if not isFilled:
                currentCounter += 1
                self.gump.setStatus(f"Filling... {currentCounter}/{counter}")
                bodInfo["bod"].fill(updateClothUsed)
                updateClothUsed()
            self._resetScrollAreaElement(bodInfo)
        self.gump.setStatus("Ready")

    def _setClothUsedLabel(self):
        if self.clothUsedLabel:
            self.clothUsedLabel.Text = f"CLOTH USED: {self.clothUsed}"

    def _countAvailableCloth(self, resourceChest):
        containers = [API.Backpack]
        if resourceChest:
            containers.append(resourceChest.Serial)

        total = 0
        for container in containers:
            for item in Util.itemsInContainer(container):
                if item.Graphic == TAILORING_CLOTH_RESOURCE_GRAPHIC and item.Hue == 0:
                    total += item.Amount
        return total

    def _bribe(self):
        if not self.runebookSerial:
            return
        self.gump.setStatus("Bribing...")
        self.total = 0
        counter = 0
        for bodInfo in self.bodInfos:
            isMaxed = Bod.isMaxed(bodInfo["bod"].item)
            if not isMaxed:
                counter += 1
        currentCounter = 0
        runeIndex = 0
        for bodInfo in self.bodInfos:
            isMaxed = Bod.isMaxed(bodInfo["bod"].item)
            if not isMaxed:
                currentCounter += 1
                self.gump.setStatus(f"Bribing... {currentCounter}/{counter}")
                while not Bod.isMaxed(bodInfo["bod"].item):
                    total = bodInfo["bod"].bribe()
                    if total == -1:
                        self.runebookItem.recall(runeIndex)
                        runeIndex += 1
                        continue
                    self.total += total
                    self.totalLabel.Text = f"BRIBE: {str(self.total)}"
            self._resetScrollAreaElement(bodInfo)
        self.gump.setStatus("Ready")

    def _resetScrollAreaElement(self, bodInfo, isChanging=True):
        for el in bodInfo["elements"]:
            el.Dispose()
        if not isChanging:
            return
        bodInfo["elements"].clear()
        labels = self._generateLabels(bodInfo["bod"])
        bodInfo["isFilledIconButton"] = labels["isFilledIconButton"]
        bodInfo["isMaxBribedIconButton"] = labels["isMaxBribedIconButton"]
        bodInfo["isPartiallyFilledIconButton"] = labels["isPartiallyFilledIconButton"]
        bodInfo["markButton"] = labels["markButton"]
        bodInfo["label"] = labels["label"]
        self._appendToScrollArea(bodInfo)

    def _scan(self, statusOverride=None):
        if not self.scrollArea:
            return
        if not statusOverride:
            self.gump.setStatus("Scanning BODs...")
        self.scrollArea.Clear()
        self.bodInfos = []

        craftingInfo = None
        resourceChest = None
        if self.containerSerial:
            resourceChest = API.FindItem(self.containerSerial)

        selectedBodGraphic = self.bodSkill["bod"]["graphic"]
        selectedBodHue = self.bodSkill["bod"]["hue"]
        isSmall = self.selectedType == "Small"

        bodItems = Bod.findAllBodItems(selectedBodGraphic, selectedBodHue, isSmall)
        craft = None
        if resourceChest:
            craftingInfo = self.craftingInfos[self.selectedProfession]
            craft = Craft(self.bodSkill, craftingInfo, resourceChest)

        try:
            for bodItem in bodItems:
                try:
                    bodInfo = Bod(self.bodSkill, bodItem, craftingInfo, craft)
                    labels = self._generateLabels(bodInfo)
                    self.bodInfos.append(
                        {
                            "bod": bodInfo,
                            "id": Python.v4(),
                            "label": labels["label"],
                            "isFilledIconButton": labels["isFilledIconButton"],
                            "isMaxBribedIconButton": labels["isMaxBribedIconButton"],
                            "isPartiallyFilledIconButton": labels[
                                "isPartiallyFilledIconButton"
                            ],
                            "markButton": labels["markButton"],
                            "elements": [],
                        }
                    )
                except:
                    pass
            for i, bodInfo in enumerate(self.bodInfos):
                yOffset = i * 18
                bodInfo["yOffset"] = yOffset
                self._appendToScrollArea(bodInfo)

            if self.bodCountLabel:
                self.bodCountLabel.Text = f"BOD COUNT: {len(self.bodInfos)}"
            self.gump.setStatus(statusOverride or "Ready.")
        except Exception as e:
            API.SysMsg(str(e))
            API.SysMsg(traceback.format_exc())
            self.gump.setStatus("Scan failed.", 33)

    def _appendToScrollArea(self, bodInfo):
        yOffset = bodInfo["yOffset"]
        for el, dx in zip(
            [
                bodInfo["isFilledIconButton"],
                bodInfo["isPartiallyFilledIconButton"],
                bodInfo["isMaxBribedIconButton"],
                bodInfo["label"],
                bodInfo["markButton"],
            ],
            [8, 54, 100, 150, 338],
        ):
            el.SetX(dx)
            el.SetY(yOffset)
            self.scrollArea.Add(el)
            bodInfo["elements"].append(el)
        API.AddControlOnClick(
            bodInfo["markButton"],
            self.gump.onClick(lambda bodInfo=bodInfo: self._markBod(bodInfo)),
        )

    def _generateLabels(self, bod):
        isFilledIcon = 11410
        isMaxBribedIcon = 11410
        isPartiallyFilledIcon = 11410
        if Bod.isFilled(bod.item, False):
            isFilledIcon = 11400
        isFilledIconButton = self.gump.createNativeButton(
            "", isFilledIcon, isFilledIcon, isFilledIcon
        )
        if Bod.isPartiallyFilled(bod.item):
            isPartiallyFilledIcon = 11400
        isPartiallyFilledIconButton = self.gump.createNativeButton(
            "", isPartiallyFilledIcon, isPartiallyFilledIcon, isPartiallyFilledIcon
        )
        if Bod.isMaxed(bod.item):
            isMaxBribedIcon = 11400
        isMaxBribedIconButton = self.gump.createNativeButton(
            "", isMaxBribedIcon, isMaxBribedIcon, isMaxBribedIcon
        )
        label = self.gump.createLabel(bod.itemName)
        markButton = self.gump.createNativeButton("", 30083, 30084, 30085)
        return {
            "label": label,
            "isFilledIconButton": isFilledIconButton,
            "isMaxBribedIconButton": isMaxBribedIconButton,
            "isPartiallyFilledIconButton": isPartiallyFilledIconButton,
            "markButton": markButton,
        }

    def _markBod(self, bodInfo):
        bodInfo["bod"].item.SetHue(11)

    def _onBeetleSelectionClicked(self, beetleLabel):
        targetSerial = API.RequestTarget()
        if not targetSerial:
            return
        mobile = API.FindMobile(targetSerial)
        self.beetleMobile = mobile
        self.beetleSerial = targetSerial
        API.SetSharedVar("BOD_BOT_BEETLE_ITEM", mobile)
        API.SetSharedVar("BOD_BOT_BEETLE_SERIAL", targetSerial)
        beetleLabel.Text = f"Selected beetle ({targetSerial})"

    def _onRunebookSelectionClicked(self, runebookLabel):
        targetSerial = API.RequestTarget()
        if not targetSerial:
            return
        item = API.FindItem(targetSerial)
        isRunebook = Item.isRunebookOrAtlas(item)
        if not isRunebook:
            return
        runebookItem = Item(item)
        self.runebookItem = runebookItem
        self.runebookSerial = targetSerial
        API.SetSharedVar("BOD_BOT_RUNEBOOK_ITEM", runebookItem)
        API.SetSharedVar("BOD_BOT_RUNEBOOK_SERIAL", targetSerial)
        runebookLabel.Text = f"Selected runebook ({targetSerial})"

    def _onNextClicked(self):
        pass

    def _onClothClicked(self):
        self.gump.setStatus("Grabing and cuting bolts")
        if not self.beetleMobile:
            self.gump.setStatus("Ready")
            return
        bolts = Util.findTypeWorld(3995)
        beetle = API.FindMobile(self.beetleSerial)
        scissors = API.FindType(3998, API.Backpack)
        if not bolts or not beetle or not scissors:
            return
        API.ClearJournal()
        while not API.InJournalAny(["That container cannot hold more weight."]):
            Util.moveItem(bolts.Serial, API.Backpack, 60)
            Util.useObjectWithTarget(scissors.Serial)
            inBackpackBolts = API.FindType(3995, API.Backpack)
            API.Target(inBackpackBolts)
            inBackpackCloths = None
            while not inBackpackCloths:
                inBackpackCloths = API.FindType(5990, API.Backpack)
                API.Pause(0.1)
            API.SysMsg(f"Found cloths {inBackpackCloths.Serial} - {self.beetleSerial}")
            Util.moveItem(inBackpackCloths.Serial, self.beetleSerial)
            API.SysMsg("Moving")
        self.gump.setStatus("Ready")

    def _onNpcSelectionClicked(self, npcLabel):
        targetSerial = API.RequestTarget()
        if not targetSerial:
            return
        self.npcSerial = targetSerial
        API.SetSharedVar("BOD_BOT_TAILOR_SERIAL", targetSerial)
        npcLabel.Text = f"Selected npc ({targetSerial})"
        self._scan()

    def _onContainerSelectionClicked(self, resourceLabel):
        targetSerial = API.RequestTarget()
        if not targetSerial:
            return
        self.containerSerial = targetSerial
        API.SetSharedVar("BOD_BOT_CONTAINER_SERIAL", targetSerial)
        resourceLabel.Text = f"Selected resource container ({targetSerial})"
        self._scan()

    def _onSortChestSelectionClicked(self, sortChestLabel):
        targetSerial = API.RequestTarget()
        if not targetSerial:
            return
        if targetSerial not in self.sortChestSerials:
            self.sortChestSerials.append(targetSerial)
        API.SetSharedVar("BOD_BOT_SORT_CHEST_SERIALS", self.sortChestSerials)
        sortChestLabel.Text = f"BOD sort chests: {len(self.sortChestSerials)}"

    def _onClearSortChestsClicked(self, sortChestLabel):
        self.sortChestSerials = []
        API.SetSharedVar("BOD_BOT_SORT_CHEST_SERIALS", self.sortChestSerials)
        sortChestLabel.Text = "BOD sort chests: 0"

    def _onTypeClicked(self, type):
        for checkbox in self.typeCheckboxes:
            checkbox["checkbox"].IsChecked = checkbox["label"] == type
        self.selectedType = type
        API.SetSharedVar("BOD_BOT_SELECTED_TYPE", type)
        self._scan()

    def _onProfessionClicked(self, profession):
        for checkbox in self.checkboxes:
            checkbox["checkbox"].IsChecked = checkbox["label"] == profession
        self.selectedProfession = profession
        API.SetSharedVar("BOD_BOT_SELECTED_PROFESSION", profession)
        self.bodSkill = self.bodSkills[self.selectedProfession]
        self._scan()

    def _isRunning(self):
        return self._running

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            for subGump in self.gump.subGumps:
                subGump.destroy()
            self.gump.destroy()
            self.gump = None
        API.Stop()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            qt.gump.tick()
            qt.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True


qt = BodBot()
qt.main()
while qt._isRunning():
    qt.tick()
    # qt.run()
    API.Pause(0.1)
