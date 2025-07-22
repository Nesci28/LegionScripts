import API
import importlib
import sys
from decimal import Decimal

sys.path.append(r".\\TazUO\\LegionScripts\\_Classes")
sys.path.append(r".\\TazUO\\LegionScripts\\_Utils")
sys.path.append(r".\\TazUO\\LegionScripts\\_Skills")

import Gump
import Util
import Math
import Musicianship
import Peacemaking

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Musicianship)
importlib.reload(Peacemaking)

from Gump import Gump
from Util import Util
from Math import Math
from Musicianship import Musicianship
from Peacemaking import Peacemaking


class BardTrainer:
    schools = [
        {
            "skillName": "Peacemaking",
            "trainer": Peacemaking,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Musicianship",
            "trainer": Musicianship,
            "skillLabel": None,
            "capLabel": None,
        },
    ]

    def __init__(self):
        self.errors = []
        self._running = True
        self.gumpHeight = 130 + 30 * len(self.schools)
        self.gumpWidth = 400
        self.gump = Gump(self.gumpWidth, self.gumpHeight, self._onClose)
        self.schoolInputs = []
        self.startBtn = None
        self.trainingQueue = []

    def main(self):
        try:
            Util.openContainer(API.Backpack)
            self._showGump()
        except Exception as e:
            API.SysMsg(f"BardTrainer error: {e}", 33)
            self._onClose()

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

    def _validate(self, school):
        c = school["trainer"]
        errors = c.validate()
        for error in errors:
            self.errors.append(error)

    def _isRunning(self):
        return self._running

    def _startTraining(self, workingSkills):
        self.trainingQueue = []
        for school, box, _, _ in workingSkills:
            trainer = school["trainer"](self._isRunning, Decimal(box.Text))
            self.trainingQueue.append((trainer, school["skillName"]))

    def tick(self):
        if not self.trainingQueue or not self._running:
            return True
        trainer, skillName = self.trainingQueue[0]
        self.gump.setStatus(f"Training {skillName}...")
        if trainer.train(self.calculateSkillLabels):
            self.trainingQueue.pop(0)
        if not self.trainingQueue:
            self.gump.setStatus("Training complete.", 66)
            return True
        return False

    def _onStart(self):
        isFormValidated = self.gump.checkValidateForm()
        if not isFormValidated:
            return

        self.errors = []
        workingSkills = []

        for school, box, lbl, skillLbl in self.schoolInputs:
            skillName = school["skillName"]
            val = Decimal(box.Text)
            skillValue = Util.getSkillInfo(skillName)["value"]
            if val > skillValue:
                self._validate(school)
                workingSkills.append((school, box, lbl, skillLbl))

        sumNeeded = sum(
            Decimal(box.Text) - Util.getSkillInfo(school["skillName"])["value"]
            for school, box, _, _ in workingSkills
        )
        charSkillInfo = Util.getCharSkillInfo()
        if charSkillInfo["totalPlus"] + sumNeeded - charSkillInfo["totalMinus"] > 720:
            self.errors.append("Too many distributed skill points")

        self.startBtn.SetWidth(0)
        self.startBtn.SetHeight(0)

        if self.errors:
            self.gump.setStatus("Validation failed, error detected", 33)
            subGump = self.gump.createSubGump(
                self.gumpWidth, max(20 * len(self.errors), 100), "bottom"
            )
            subGump.addLabel("Validation errors:", 10, 10)
            for i, error in enumerate(self.errors):
                subGump.addLabel(error, 10, 30 + 15 * i, 33)
        else:
            self._startTraining(workingSkills)

    def calculateSkillLabels(self):
        for school in self.schools:
            skillName = school["skillName"]
            currentValue = Util.getSkillInfo(skillName)["value"]
            currentCap = Util.getSkillInfo(skillName)["cap"]
            school["skillLabel"].Text = Math.truncateDecimal(currentValue, 1)
            school["capLabel"].Text = Math.truncateDecimal(currentCap, 1)

    def _setSkillToCap(self, textbox, maxValue):
        textbox.SetText(str(maxValue))

    def _showGump(self):
        self.gump.setStatus("Configure training and press okay...")
        self.gump.addLabel("Select Spell School & Target Skill:", 10, 10)
        self.gump.addLabel("Current", 270, 30)
        self.gump.addLabel("Cap", 320, 30)

        y = 60
        x = 155
        for school in self.schools:
            skillName = school["skillName"]
            lbl = self.gump.addLabel(skillName, 10, y)
            minValue = Util.getSkillInfo(skillName)["value"]
            maxValue = Util.getSkillInfo(skillName)["cap"]
            textbox = self.gump.addSkillTextBox(str(minValue), x, y, minValue, maxValue)
            self.gump.addButton(
                "",
                x + 85,
                y,
                "radioGreen",
                self.gump.onClick(
                    lambda tb=textbox, maxV=maxValue: self._setSkillToCap(tb, maxV)
                ),
            )
            school["skillLabel"] = self.gump.addLabel("", x + 115, y)
            school["capLabel"] = self.gump.addLabel("", x + 165, y)
            self.schoolInputs.append((school, textbox, lbl, school["skillLabel"]))
            y += 30

        self.calculateSkillLabels()

        self.startBtn = self.gump.addButton(
            "",
            10,
            y,
            "okay",
            self.gump.onClick(lambda: self._onStart(), "Validating...", ""),
        )
        self.gump.create()


trainer = BardTrainer()
trainer.main()
while trainer._isRunning():
    trainer.gump.tick()
    trainer.gump.tickSubGumps()
    trainer.tick()
    API.Pause(0.1)
