import API
import importlib
import sys
import traceback
import json

sys.path.append(r".\\TazUO\\LegionScripts\\_Classes")
sys.path.append(r".\\TazUO\\LegionScripts\\_Utils")
sys.path.append(r".\\TazUO\\LegionScripts\\_Skills")

import Bod
import Gump
import Util
import Math
import Timer
import Magic
import Python
import Error
import Craft

importlib.reload(Bod)
importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Timer)
importlib.reload(Magic)
importlib.reload(Python)
importlib.reload(Error)
importlib.reload(Craft)

from Bod import Bod
from Gump import Gump
from Util import Util
from Math import Math
from Timer import Timer
from Magic import Magic
from Python import Python
from Error import Error
from Craft import Craft

class BodBot:
    def __init__(self):
        bodSkillsJson = open(r".\\TazUO\\LegionScripts\\_Jsons\\bod-skills.json")
        bodSkillsStr = json.load(bodSkillsJson)
        craftingInfosJson = open(r".\\TazUO\\LegionScripts\\_Jsons\\crafting-infos.json")
        craftingInfosStr = json.load(craftingInfosJson)

        self._running = True
        self.gump = None
        self.scrollArea = None
        self.checkboxes = []
        self.typeCheckboxes = []
        self.containerSerial = None
        self.bodCountLabel = None
        
        self.bodSkills = Math.convertToHex(bodSkillsStr)
        self.craftingInfos = Math.convertToHex(craftingInfosStr)
        self.selectedProfession = "Tailoring"
        self.selectedType = "Small"
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
        height = 400
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
                self.gump.onClick(lambda profession=profession: self._onProfessionClicked(profession))
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
                self.gump.onClick(lambda type=type: self._onTypeClicked(type))
            )
            self.typeCheckboxes.append({"label": type, "checkbox": checkbox})
            x += 125
        x = 1
        y += 25

        resourceLabel = g.addLabel("Select resource container", 25, y)
        g.addButton(
            "",
            x,
            y,
            "radioBlue",
            self.gump.onClick(lambda resourceLabel=resourceLabel: self._onContainerSelectionClicked(resourceLabel))
        )
        
        x = 1
        y += 25

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
        self.scrollArea = API.CreateGumpScrollArea(x, y, scrollAreaWidth, scrollAreaHeight)
        self.gump.gump.Add(self.scrollArea)
        self._scan()
        y += scrollAreaHeight + 25

        bodCountLabel = g.addLabel("Bod count: 0", 25, y)
        self.bodCountLabel = bodCountLabel
        y += 25

        for action in ["Bribe", "Fill", "Turn in", "Rescan"]:
            g.addButton(
                action,
                x,
                y,
                "default",
                self.gump.onClick(lambda action=action: self._onActionClicked(action)),
                True
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

    def _turnIn(self):
        self.gump.setStatus("Turn In...")
        for bodInfo in self.bodInfos:
            isFilled = Bod.isFilled(bodInfo["bod"].item)
            if not isFilled:
                continue
            bodInfo["bod"].turnIn()
            self._resetScrollAreaElement(bodInfo, False)
            API.Pause(1)
        self.gump.setStatus("Ready")

    def _fill(self):
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
        self.gump.setStatus("Bribing...")
        counter = 0
        for bodInfo in self.bodInfos:
            isMaxed = Bod.isMaxed(bodInfo["bod"].item)
            if not isMaxed:
                counter += 1
        currentCounter = 0
        for bodInfo in self.bodInfos:
            isMaxed = Bod.isMaxed(bodInfo["bod"].item)
            if not isMaxed:
                currentCounter += 1
                self.gump.setStatus(f"Bribing... {currentCounter}/{counter}")
                bodInfo["bod"].bribe()
            self._resetScrollAreaElement(bodInfo)
        self.gump.setStatus("Ready")

    def _resetScrollAreaElement(self, bodInfo, isChanging = True):
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

        bodSkill = self.bodSkills[self.selectedProfession]
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
            craft = Craft(bodSkill, craftingInfo, resourceChest)

        for bodItem in bodItems:
            bodInfo = Bod(self.bodSkill, bodItem, craftingInfo, craft)
            labels = self._generateLabels(bodInfo)
            self.bodInfos.append({
                "bod": bodInfo,
                "id": Python.v4(),
                "label": labels["label"],
                "isFilledIconButton": labels["isFilledIconButton"],
                "isMaxBribedIconButton": labels["isMaxBribedIconButton"],
                "isPartiallyFilledIconButton": labels["isPartiallyFilledIconButton"],
                "markButton": labels["markButton"],
                "elements": []
            })
        for i, bodInfo in enumerate(self.bodInfos):
            yOffset = i * 18
            bodInfo["yOffset"] = yOffset
            self._appendToScrollArea(bodInfo)

        if self.bodCountLabel:
            self.bodCountLabel.Text = f"Bod count: {len(self.bodInfos)}"

    def _appendToScrollArea(self, bodInfo):
        yOffset = bodInfo["yOffset"]
        for el, dx in zip(
            [bodInfo["isFilledIconButton"], bodInfo["isPartiallyFilledIconButton"], bodInfo["isMaxBribedIconButton"], bodInfo["label"], bodInfo["markButton"]],
            [7, 53, 100, 137, 288]
        ):
            el.SetX(dx)
            el.SetY(yOffset)
            self.scrollArea.Add(el)
            bodInfo["elements"].append(el)
        API.AddControlOnClick(bodInfo["markButton"], self.gump.onClick(lambda bodInfo=bodInfo: self._markBod(bodInfo)))

    def _generateLabels(self, bod):
        isFilledIcon = 11410
        isMaxBribedIcon = 11410
        isPartiallyFilledIcon = 11410
        if (Bod.isFilled(bod.item, False)):
            isFilledIcon = 11400
        isFilledIconButton = API.CreateGumpButton("", 996, isFilledIcon, isFilledIcon, isFilledIcon)
        if (Bod.isPartiallyFilled(bod.item)):
            isPartiallyFilledIcon = 11400
        isPartiallyFilledIconButton = API.CreateGumpButton("", 996, isPartiallyFilledIcon, isPartiallyFilledIcon, isPartiallyFilledIcon)
        if (Bod.isMaxed(bod.item)):
            isMaxBribedIcon = 11400
        isMaxBribedIconButton = API.CreateGumpButton("", 996, isMaxBribedIcon, isMaxBribedIcon, isMaxBribedIcon)
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


    def _onContainerSelectionClicked(self, resourceLabel):
        targetSerial = API.RequestTarget()
        if not targetSerial:
            return
        self.containerSerial = targetSerial
        resourceLabel.Text = f"Select resource container ({targetSerial})"
        self._scan()

    def _onTypeClicked(self, type):
        for checkbox in self.typeCheckboxes:
            if checkbox["label"] != type:
                checkbox["checkbox"].IsChecked = False
        self.selectedType = type
        self._scan()

    def _onProfessionClicked(self, profession):
        for checkbox in self.checkboxes:
            if checkbox["label"] != profession:
                checkbox["checkbox"].IsChecked = False
        self.selectedProfession = profession
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
