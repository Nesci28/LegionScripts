import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Music
import Util

importlib.reload(Util)
importlib.reload(_Music)

from _Music import Music
from Util import Util


class Peacemaking(Music):
    @staticmethod
    def validate(skillCap=None):
        return Music.validate()

    def __init__(self, skillCap=None, label=None, skillLevelLabel=None, running=None):
        if callable(skillCap):
            running = skillCap
            skillCap = label
            label = None
            skillLevelLabel = None

        self.running = running or (lambda: True)
        self.skillCap = skillCap if skillCap is not None else API.GetSkill("Peacemaking").Cap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.instruments = self._findInstruments()
        self.skillName = "Peacemaking"
        self._done = False
        API.SetSkillLock(self.skillName, "up")

    def trainOnce(self):
        errors = Music.validate()
        if errors:
            API.SysMsg(f"{self.skillName} - Missing instruments", 33)
            API.Stop()
            return
        self.use(API.Player.Serial)
        API.Pause(6)

    def train(self, calculateSkillLabels=None):
        while (
            self.running()
            and Util.getSkillInfo(self.skillName)["value"] < self.skillCap
        ):
            self.trainOnce()
            if calculateSkillLabels:
                calculateSkillLabels()

        self._done = Util.getSkillInfo(self.skillName)["value"] >= self.skillCap
        return self._done

    def use(self, targetSerial):
        API.ClearJournal()
        self.instruments = self._findInstruments()
        API.UseSkill(self.skillName)
        API.Pause(0.25)
        if API.InJournalAny(
            ["You must wait a few moments to use another skill.", "$You must wait(.*)"]
        ):
            API.Pause(0.1)
            return self.use(targetSerial)
        if API.InJournalAny(
            ["What instrument shall you play?", "$What instrument(.*)"]
        ):
            API.WaitForTarget("any", 2)
            API.Target(self.instruments[0].Serial)
        API.WaitForTarget("any", 2)
        API.Target(targetSerial)
        API.CreateCooldownBar(6, "Peacemaking cooldown", 906)
