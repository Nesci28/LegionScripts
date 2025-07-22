import API
import importlib
import sys
import traceback
from decimal import Decimal

sys.path.append(r".\\TazUO\\LegionScripts\\_Classes")
sys.path.append(r".\\TazUO\\LegionScripts\\_Utils")
sys.path.append(r".\\TazUO\\LegionScripts\\_Skills")

import Gump
import Util
import Math
import Magery
import Mysticism
import Necromancy
import Chivalry
import Spellweaving
import Bushido
import EvaluatingIntelligence
import SpiritSpeak
import Meditation

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Magery)
importlib.reload(Mysticism)
importlib.reload(Necromancy)
importlib.reload(Chivalry)
importlib.reload(Spellweaving)
importlib.reload(Bushido)
importlib.reload(EvaluatingIntelligence)
importlib.reload(SpiritSpeak)
importlib.reload(Meditation)

from Gump import Gump
from Util import Util
from Math import Math
from Magery import Magery
from Mysticism import Mysticism
from Necromancy import Necromancy
from Chivalry import Chivalry
from Spellweaving import Spellweaving
from Bushido import Bushido
from EvaluatingIntelligence import EvaluatingIntelligence
from SpiritSpeak import SpiritSpeak
from Meditation import Meditation


class CasterTrainer:
    schools = [
        {
            "skillName": "Magery",
            "trainer": Magery,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Evaluating Intelligence",
            "trainer": EvaluatingIntelligence,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Meditation",
            "trainer": Meditation,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Mysticism",
            "trainer": Mysticism,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Spellweaving",
            "trainer": Spellweaving,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Chivalry",
            "trainer": Chivalry,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Bushido",
            "trainer": Bushido,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Necromancy",
            "trainer": Necromancy,
            "skillLabel": None,
            "capLabel": None,
        },
        {
            "skillName": "Spirit Speak",
            "trainer": SpiritSpeak,
            "skillLabel": None,
            "capLabel": None,
        },
    ]

    def __init__(self):
        self.errors = []
        self._running = True
        self.gump = None
        self.schoolInputs = []
        self.startBtn = None

    def main(self):
        try:
            Util.openContainer(API.Backpack)
            self._showGump()
            self.gump.create()
        except Exception as e:
            API.SysMsg(f"CasterTrainer e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            self.gump.tick()
            self.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True

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

    def calculateSkillLabels(self):
        for school in self.schools:
            skillName = school["skillName"]
            info = Util.getSkillInfo(skillName)
            school["skillLabel"].Text = Math.truncateDecimal(info["value"], 1)
            school["capLabel"].Text = Math.truncateDecimal(info["cap"], 1)

    def _validate(self, school, skillCap):
        errors = school["trainer"].validate(skillCap)
        self.errors.extend(errors)

    def _onStart(self):
        if not self.gump.checkValidateForm():
            return

        self.errors.clear()
        workingSkills = []

        for school, box, lbl, skillLbl, spellLabel in self.schoolInputs:
            skillName = school["skillName"]
            desired = Decimal(box.Text)
            current = Util.getSkillInfo(skillName)["value"]
            if desired > current:
                self._validate(school, desired)
                workingSkills.append((school, box, lbl, skillLbl, spellLabel))

        totalNeeded = sum(
            Decimal(box.Text) - Util.getSkillInfo(school["skillName"])["value"]
            for school, box, *_ in workingSkills
        )
        charInfo = Util.getCharSkillInfo()
        if charInfo["totalPlus"] + totalNeeded - charInfo["totalMinus"] > 720:
            self.errors.append("Too many distributed skill point")

        self.startBtn.SetWidth(0)
        self.startBtn.SetHeight(0)

        if self.errors:
            self.gump.setStatus("Validation failed, error detected", 33)
            errorHeight = max(20 * len(self.errors), 100)
            subGump = self.gump.createSubGump(self.gumpWidth, errorHeight, "bottom")
            subGump.addLabel("Validation errors:", 10, 10)
            for i, error in enumerate(self.errors):
                subGump.addLabel(error, 10, 30 + 15 * i, 33)
        else:
            for school, box, lbl, skillLbl, spellLabel in workingSkills:
                skillCap = Decimal(box.Text)
                trainer = school["trainer"](skillCap, lbl, skillLbl, spellLabel)
                self.gump.setStatus(f"Training {school['skillName']}...")
                trainer.train(self.calculateSkillLabels)

    def _setSkillToCap(self, textbox, maxValue):
        textbox.SetText(str(maxValue))

    def _showGump(self):
        self.gumpHeight = 130 + 30 * len(self.schools)
        self.gumpWidth = 400

        g = Gump(self.gumpWidth, self.gumpHeight, self._onClose)
        self.gump = g
        g.setStatus("Configure training and press okay...")
        g.addLabel("Select Spell School & Target Skill:", 10, 10)
        spellLabel = g.addLabel("", 155, 0)
        g.addLabel("Current", 270, 30)
        g.addLabel("Cap", 320, 30)

        self.schoolInputs = []
        y = 60
        for school in self.schools:
            skillName = school["skillName"]
            lbl = g.addLabel(skillName, 10, y)
            minVal = Util.getSkillInfo(skillName)["value"]
            maxVal = Util.getSkillInfo(skillName)["cap"]
            box = g.addSkillTextBox(str(minVal), 155, y, minVal, maxVal)
            g.addButton(
                "",
                240,
                y,
                "radioGreen",
                g.onClick(lambda tb=box, mv=maxVal: self._setSkillToCap(tb, mv)),
            )
            school["skillLabel"] = g.addLabel("", 270, y)
            school["capLabel"] = g.addLabel("", 320, y)
            self.schoolInputs.append(
                (school, box, lbl, school["skillLabel"], spellLabel)
            )
            y += 30

        self.calculateSkillLabels()
        self.startBtn = g.addButton(
            "", 10, y, "okay", g.onClick(self._onStart, "Validating...", "")
        )
        spellLabel.SetY(y)

    def _isRunning(self):
        return self._running


trainer = CasterTrainer()
trainer.main()
while trainer._isRunning():
    trainer.gump.tick()
    trainer.gump.tickSubGumps()
    trainer.tick()
    API.Pause(0.1)
