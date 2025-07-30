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

importlib.reload(Bod)
importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Timer)
importlib.reload(Magic)
importlib.reload(Python)

from Bod import Bod
from Gump import Gump
from Util import Util
from Math import Math
from Timer import Timer
from Magic import Magic
from Python import Python

class BodBot:
    def __init__(self):
        bodSkillsJson = open(r".\\TazUO\\LegionScripts\\_Jsons\\bod-skills.json")
        bodSkillsStr = json.load(bodSkillsJson)

        self._running = True
        self.gump = None
        self.scrollArea = None
        self.checkboxes = []
        self.typeCheckboxes = []
        
        self.bodSkills = Math.convertToHex(bodSkillsStr)
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

    def _scan(self):
        self.scrollArea.Clear()
        self.bodInfos = []
        selectedBodGraphic = self.bodSkill["bod"]["graphic"]
        selectedBodHue = self.bodSkill["bod"]["hue"]
        isSmall = self.selectedType == "Small"
        bodItems = Bod.findAllBodItems(selectedBodGraphic, selectedBodHue, isSmall)
        for bodItem in bodItems:
            bodInfo = Bod(self.bodSkill, bodItem)
            labels = self._generateLabel(bodInfo)
            self.bodInfos.append({ "bod": bodInfo, "id": Python.v4(), "label": labels["label"], "isFilledIcon": labels["isFilledIcon"], "isMaxBribedIcon": labels["isMaxBribedIcon"] })
        for i, bodInfo in enumerate(self.bodInfos):
            idLabel = API.CreateGumpLabel(bodInfo["id"])
            idLabel.IsVisible = False
            self.scrollArea.Add(idLabel)
            isFilledIcon = bodInfo["isFilledIcon"]
            isFilledIcon.SetX(0)
            isFilledIcon.SetY(i * 18)
            self.scrollArea.Add(isFilledIcon)
            isMaxBribedIcon = bodInfo["isMaxBribedIcon"]
            isMaxBribedIcon.SetX(50)
            isMaxBribedIcon.SetY(i * 18)
            self.scrollArea.Add(isMaxBribedIcon)
            label = bodInfo["label"]
            label.SetX(100)
            label.SetY(i * 18)
            self.scrollArea.Add(label)

    def _generateLabel(self, bod):
        isFilledIcon = 11410
        isMaxBribedIcon = 11410
        if (Bod.isFilled(bod.item, False)):
            isFilledIcon = 11400
        isFilledIcon = API.CreateGumpButton("", 996, isFilledIcon, isFilledIcon, isFilledIcon)
        if (Bod.isMaxed(bod.item)):
            isMaxBribedIcon = 11400
        isMaxBribedIcon = API.CreateGumpButton("", 996, isMaxBribedIcon, isMaxBribedIcon, isMaxBribedIcon)
        label = API.CreateGumpLabel(bod.itemName)
        return {
            "label": label,
            "isFilledIcon": isFilledIcon,
            "isMaxBribedIcon": isMaxBribedIcon,
        }

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

        scrollAreaWidth = width - 13
        scrollAreaHeight = round(height / 2)

        g.addLabel("Filled", x, y)
        x += 50
        g.addLabel("Maxed", x, y)
        x += 50
        g.addLabel("Item required", x, y)
        x = 1
        y += 20
        self.scrollArea = API.CreateGumpScrollArea(x, y, scrollAreaWidth, scrollAreaHeight)
        self.gump.gump.Add(self.scrollArea)
        self._scan()
        y += scrollAreaHeight + 20

        for action in ["Bribe", "Fill", "Turn in"]:
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
        self.gump.create()

    def _onActionClicked(self, action):
        if action == "Bribe":
            self._bribe()
            return
        if action == "Fill":
            self._fill()
        if action == "Turn in":
            return

    def _fill(self):
        self.gump.setStatus("Filling...")
        for i, bodInfo in enumerate(self.bodInfos):
            self.bodInfos[i]["isFilledIcon"] = 11400
            self._resetScrollAreaElement(bodInfo)
            API.Pause(1)
        self.gump.setStatus("Ready")

    def _bribe(self):
        self.gump.setStatus("Bribing...")
        for i, bodInfo in enumerate(self.bodInfos):
            isMaxed = Bod.isMaxed(bodInfo["bod"].item)
            if not isMaxed:
                bodInfo["bod"].bribe()
            self.bodInfos[i]["isMaxBribedIcon"] = 11400
            self._resetScrollAreaElement(bodInfo)
        self.gump.setStatus("Ready")

    def _resetScrollAreaElement(self, bodInfo):
        try:
            API.SysMsg(str(bodInfo["id"]))
            API.SysMsg(str(self.scrollArea.Children))
            index = Python.findIndex(bodInfo["id"], self.scrollArea.Children, "Text")
            API.SysMsg(str(index))
            if (index == -1):
                pass
            startIndex = index * 3
            isFilledIcon = self.scrollArea.Children[startIndex]
            isMaxedIcon = self.scrollArea.Children[startIndex + 1]
            itemNameLabel = self.scrollArea.Children[startIndex + 2]
            isFilledIconX = isFilledIcon.GetX()
            isFilledIconY = isFilledIcon.GetY()
            isFilledIcon.Dispose()
            isMaxedIconX = isMaxedIcon.GetX()
            isMaxedIconY = isMaxedIcon.GetY()
            isMaxedIcon.Dispose()
            itemNameLabelX = itemNameLabel.GetX()
            itemNameLabelY = itemNameLabel.GetY()
            itemNameLabel.Dispose()

            bod = self.bodInfos[index]
            isFilledIcon = bod["isFilledIcon"]
            isFilledIcon.SetX(isFilledIconX)
            isFilledIcon.SetY(isFilledIconY)
            self.scrollArea.Add(isFilledIcon)
            isMaxBribedIcon = bod["isMaxBribedIcon"]
            isMaxBribedIcon.SetX(isMaxedIconX)
            isMaxBribedIcon.SetY(isMaxedIconY)
            self.scrollArea.Add(isMaxBribedIcon)
            label = bod["label"]
            label.SetX(itemNameLabelX)
            label.SetY(itemNameLabelY)
            self.scrollArea.Add(label)
        except Exception as e:
            API.SysMsg(str(e))



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
