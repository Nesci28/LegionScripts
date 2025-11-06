import API
import importlib
import traceback
from decimal import Decimal
from LegionPath import LegionPath

LegionPath.addSubdirs()

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
import Musicianship
import Peacemaking
import AnimalTaming
import AnimalLore

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
importlib.reload(Musicianship)
importlib.reload(Peacemaking)
importlib.reload(AnimalTaming)
importlib.reload(AnimalLore)

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
from Musicianship import Musicianship
from Peacemaking import Peacemaking
from AnimalTaming import AnimalTaming
from AnimalLore import AnimalLore


class Trainer:
    schools = {
        "Caster": [
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
        ],
        "Bard": [
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
        ],
        "Thief": [
            {
                "skillName": "Hiding",
                "trainer": None,
                "skillLabel": None,
                "capLabel": None,
            },
            {
                "skillName": "Stealth",
                "trainer": None,
                "skillLabel": None,
                "capLabel": None,
            },
        ],
        "Taming": [
            {
                "skillName": "Animal Taming",
                "trainer": AnimalTaming,
                "skillLabel": None,
                "capLabel": None,
            },
            {
                "skillName": "Animal Lore",
                "trainer": AnimalLore,
                "skillLabel": None,
                "capLabel": None,
            },
        ]
    }

    def __init__(self):
        self.errors = []
        self._running = True
        self.gump = None
        self.schoolInputs = []
        self.startBtn = None
        self.tabGumpWidth = 64
        self.mainGumpWidth = 400
        self.totalGumpWidth = self.tabGumpWidth + self.mainGumpWidth

    def main(self):
        try:
            Util.openContainer(API.Backpack)
            self._showGump()
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

    def calculateSkillLabels(self, schoolName):
        for school in self.schools[schoolName]:
            skillName = school["skillName"]
            info = Util.getSkillInfo(skillName)
            school["skillLabel"].Text = Math.truncateDecimal(info["value"], 1)
            school["capLabel"].Text = Math.truncateDecimal(info["cap"], 1)

    def _validate(self, school, skillCap):
        errors = school["trainer"].validate(skillCap)
        self.errors.extend(errors)

    def _onStart(self):
        try:
            if not self.gump.checkValidateForm():
                return

            self.errors.clear()
            workingSkills = []

            for school, box, lbl, skillLbl in self.schoolInputs:
                skillName = school["skillName"]
                desired = Decimal(box.Text)
                current = Util.getSkillInfo(skillName)["value"]
                if desired > current:
                    self._validate(school, desired)
                    workingSkills.append((school, box, lbl, skillLbl))

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
                subGump = self.gump.createSubGump(self.totalGumpWidth, errorHeight, "bottom")
                subGump.addLabel("Validation errors:", 10, 10)
                for i, error in enumerate(self.errors):
                    subGump.addLabel(error, 10, 30 + 15 * i, 33)
            else:
                for school, box, lbl, skillLbl in workingSkills:
                    skillCap = Decimal(box.Text)
                    trainer = None
                    try:
                        trainer = school["trainer"](skillCap, lbl, skillLbl)
                    except:
                        trainer = school["trainer"](skillCap)
                    self.gump.setStatus(f"Training {school['skillName']}...")
                    trainer.train(lambda schoolName=school["name"]: self.calculateSkillLabels(schoolName))
        except Exception as e:
            API.SysMsg(str(e))
            API.SysMsg(traceback.format_exc())

    def _setSkillToCap(self, textbox, maxValue):
        textbox.SetText(str(maxValue))

    def _createSchoolGump(self, gump, schoolName):
        gump.setStatus("Configure training and press okay...")
        gump.addLabel("Select Spell School & Target Skill:", 10, 10)
        gump.addLabel("Current", 270, 30)
        gump.addLabel("Cap", 320, 30)

        y = 60
        x = 155
        schools = self.schools[schoolName]
        for school in schools:
            skillName = school["skillName"]
            lbl = gump.addLabel(skillName, 10, y)
            minValue = Util.getSkillInfo(skillName)["value"]
            maxValue = Util.getSkillInfo(skillName)["cap"]
            textbox = gump.addSkillTextBox(str(minValue), x, y, minValue, maxValue)
            gump.addButton(
                "",
                x + 85,
                y,
                "radioGreen",
                gump.onClick(
                    lambda tb=textbox, maxV=maxValue: self._setSkillToCap(tb, maxV)
                ),
            )
            school["skillLabel"] = gump.addLabel("", x + 115, y)
            school["capLabel"] = gump.addLabel("", x + 165, y)
            school["name"] = schoolName
            self.schoolInputs.append((school, textbox, lbl, school["skillLabel"]))
            y += 30

        self.calculateSkillLabels(schoolName)
        self.startBtn = gump.addButton(
            "", 10, y, "okay", gump.onClick(self._onStart, "Validating...", "")
        )

    def _showGump(self):
        g = Gump(self.tabGumpWidth, 400, None, False)
        self.gump = g

        casterGump = g.addTabButton("Caster", "caster", 400)
        self._createSchoolGump(casterGump, "Caster")

        bardGump = g.addTabButton("Bard", "bard", 400)
        self._createSchoolGump(bardGump, "Bard")
        
        thiefGump = g.addTabButton("Thief", "thief", 400)
        self._createSchoolGump(thiefGump, "Thief")

        tamingGump = g.addTabButton("Taming", "taming", 400)
        self._createSchoolGump(tamingGump, "Taming")

        g.createSubGump(self.totalGumpWidth, 100, withStatus=True)

        g.setActiveTab("Caster")
        g.create()

    def _isRunning(self):
        return self._running

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            trainer.gump.tick()
            trainer.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True


trainer = Trainer()
trainer.main()
while trainer._isRunning():
    # trainer.gump.tick()
    # trainer.gump.tickSubGumps()
    trainer.tick()
    API.Pause(0.1)
