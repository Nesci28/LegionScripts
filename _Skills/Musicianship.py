import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Music
import Util

importlib.reload(Util)
importlib.reload(_Music)

from _Music import Music
from Util import Util


class Musicianship(Music):
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
        self.skillCap = skillCap if skillCap is not None else API.GetSkill("Musicianship").Cap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.instruments = self._findInstruments()
        self.skillName = "Musicianship"
        API.SetSkillLock(self.skillName, "up")

    def trainOnce(self):
        errors = Music.validate()
        if errors:
            API.SysMsg(f"{self.skillName} - Missing instruments", 33)
            API.Stop()
            return
        self.instruments = self._findInstruments()
        API.UseObject(self.instruments[0].Serial)
        API.Pause(0.5)

    def train(self, calculateSkillLabels=None):
        while (
            self.running()
            and Util.getSkillInfo(self.skillName)["value"] < self.skillCap
        ):
            self.trainOnce()
            if not self.running():
                break
            if calculateSkillLabels:
                calculateSkillLabels()
