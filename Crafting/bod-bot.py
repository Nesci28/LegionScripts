import API
import importlib
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Bod
import Gump
import Util
import Math
import Timer
import Magic
import Python
import Error
import Craft
import Item

importlib.reload(Bod)
importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Timer)
importlib.reload(Magic)
importlib.reload(Python)
importlib.reload(Error)
importlib.reload(Craft)
importlib.reload(Item)

from Bod import Bod
from Gump import Gump
from Util import Util
from Math import Math
from Timer import Timer
from Magic import Magic
from Python import Python
from Error import Error
from Craft import Craft
from Item import Item

from bod_skills import bodSkillsStr
from crafting_infos import craftingInfosStr

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
        self.bodCountLabel = None
        self.totalLabel = None
        self.total = 0
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
        width = 375
        height = 470
        g = Gump(width, height, self._onClose)
        self.gump = g

        y = 1
        x = 1

        for i, profession in enumerate(self.professions):
            label = profession.capitalize()
            checkbox = g.addCheckbox(
                label,
                x,
                y,
                self.selectedProfession == label,
                self.gump.onClick(
                    lambda profession=profession: self._onProfessionClicked(profession)
                ),
            )
            self.checkboxes.append({"label": label, "checkbox": checkbox})
            if (i + 1) % 3 == 0 and i != len(self.professions) - 1:
                y += 25
                x = 0
            else:
                x += 125
        x = 1
        y += 25

        for i, type in enumerate(["Small", "Large"]):
            checkbox = g.addCheckbox(
                type,
                x,
                y,
                i == 0,
                self.gump.onClick(lambda type=type: self._onTypeClicked(type)),
            )
            self.typeCheckboxes.append({"label": type, "checkbox": checkbox})
            x += 125
        x = 1
        y += 25

        selectResourceContainerText = "Select resource container"
        if self.containerSerial:
            selectResourceContainerText = (
                f"Selected resource container ({self.containerSerial})"
            )
        resourceLabel = g.addLabel(selectResourceContainerText, 25, y)
        g.addButton(
            "",
            x,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda resourceLabel=resourceLabel: self._onContainerSelectionClicked(
                    resourceLabel
                )
            ),
        )

        x = 1
        y += 20

        selectNpcText = "Select npc"
        if self.tailorSerial:
            selectNpcText = f"Selected npc ({self.tailorSerial})"
        npcLabel = g.addLabel(selectNpcText, 25, y)
        g.addButton(
            "",
            x,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda npcLabel=npcLabel: self._onNpcSelectionClicked(npcLabel)
            ),
        )

        x = 1
        y += 20

        selectNpcText = "Select runebook"
        if self.runebookSerial:
            selectNpcText = f"Selected runebook ({self.runebookSerial})"
        npcLabel = g.addLabel(selectNpcText, 25, y)
        g.addButton(
            "",
            x,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda npcLabel=npcLabel: self._onRunebookSelectionClicked(npcLabel)
            ),
        )
        # g.addButton(
        #     "Next",
        #     225,
        #     y,
        #     "default",
        #     self.gump.onClick(lambda: self._onNextClicked()),
        #     True,
        # )

        x = 1
        y += 20

        selectBeetleText = "Select Beetle"
        if self.beetleSerial:
            selectBeetleText = f"Selected Beetle ({self.beetleSerial})"
        beetleLabel = g.addLabel(selectBeetleText, 25, y)
        g.addButton(
            "",
            x,
            y,
            "radioBlue",
            self.gump.onClick(
                lambda beetleLabel=beetleLabel: self._onBeetleSelectionClicked(
                    beetleLabel
                )
            ),
        )
        g.addButton(
            "Cloth",
            225,
            y,
            "default",
            self.gump.onClick(lambda: self._onClothClicked()),
            True,
        )

        x = 1
        y += 20

        scrollAreaWidth = width - 13
        scrollAreaHeight = round(height / 2)

        g.addLabel("Filled", x, y)
        x += 40
        g.addLabel("Partial", x, y)
        x += 50
        g.addLabel("Maxed", x, y)
        x += 47
        g.addLabel("Item required", x, y)
        x += 150
        g.addLabel("Mark", x, y)
        x = 1
        y += 20
        self.scrollArea = API.CreateGumpScrollArea(
            x, y, scrollAreaWidth, scrollAreaHeight
        )
        self.gump.gump.Add(self.scrollArea)
        self._scan()

        y += scrollAreaHeight + 2
        x = 1

        bodCountLabel = g.addLabel("Bod count: 0", 1, y)
        self.bodCountLabel = bodCountLabel

        totalLabel = g.addLabel("Bribe total: 0", 150, y)
        self.totalLabel = totalLabel
        y += 25

        for action in ["Bribe", "Fill", "Turn in", "Rescan"]:
            g.addButton(
                action,
                x,
                y,
                "default",
                self.gump.onClick(lambda action=action: self._onActionClicked(action)),
                True,
            )
            x += 75
        x = 1
        self._scan()
        self.gump.create()

    def _onActionClicked(self, action):
        if action == "Bribe":
            self._bribe()
        if action == "Fill":
            self._fill()
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

    def _fill(self):
        if not self.containerSerial:
            return
        resourceChest = API.FindItem(self.containerSerial)
        distance = Math.distanceBetween(API.Player, resourceChest)
        if distance > 1:
            return
        self.gump.setStatus("Filling...")
        counter = 0
        for bodInfo in self.bodInfos:
            isFilled = Bod.isFilled(bodInfo["bod"].item)
            if not isFilled:
                counter += 1
        currentCounter = 0
        for bodInfo in self.bodInfos:
            isFilled = Bod.isFilled(bodInfo["bod"].item)
            if not isFilled:
                currentCounter += 1
                self.gump.setStatus(f"Filling... {currentCounter}/{counter}")
                bodInfo["bod"].fill()
            self._resetScrollAreaElement(bodInfo)
        self.gump.setStatus("Ready")

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
                    self.totalLabel.Text = f"Bribe total: {str(self.total)}"
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

    def _scan(self):
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
                self.bodCountLabel.Text = f"Bod count: {len(self.bodInfos)}"
        except Exception as e:
            API.SysMsg(str(e))
            API.SysMsg(traceback.format_exc())

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
            [7, 53, 100, 137, 288],
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
        isFilledIconButton = API.CreateGumpButton(
            "", 996, isFilledIcon, isFilledIcon, isFilledIcon
        )
        if Bod.isPartiallyFilled(bod.item):
            isPartiallyFilledIcon = 11400
        isPartiallyFilledIconButton = API.CreateGumpButton(
            "", 996, isPartiallyFilledIcon, isPartiallyFilledIcon, isPartiallyFilledIcon
        )
        if Bod.isMaxed(bod.item):
            isMaxBribedIcon = 11400
        isMaxBribedIconButton = API.CreateGumpButton(
            "", 996, isMaxBribedIcon, isMaxBribedIcon, isMaxBribedIcon
        )
        label = API.CreateGumpLabel(bod.itemName)
        markButton = API.CreateGumpButton("", 996, 30083, 30084, 30085)
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

    def _onTypeClicked(self, type):
        for checkbox in self.typeCheckboxes:
            if checkbox["label"] != type:
                checkbox["checkbox"].IsChecked = False
        self.selectedType = type
        API.SetSharedVar("BOD_BOT_SELECTED_TYPE", type)
        self._scan()

    def _onProfessionClicked(self, profession):
        for checkbox in self.checkboxes:
            if checkbox["label"] != profession:
                checkbox["checkbox"].IsChecked = False
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
