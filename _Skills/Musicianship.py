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
    def __init__(self, running, skillCap=API.GetSkill("Musicianship").Cap):
        self.running = running
        self.skillCap = skillCap
        self.instruments = self._findInstruments()
        self.skillName = "Musicianship"
        API.SetSkillLock(self.skillName, "up")

    def trainOnce(self):
        API.UseObject(self.instruments[0].Serial)
        API.Pause(0.5)

    def train(self, calculateSkillLabels=None):
        while (
            self.running()
            and Util.getSkillInfo(self.skillName)["value"] < self.skillCap
        ):
            self.trainOnce()
            if not self.running:
                break
            if calculateSkillLabels:
                calculateSkillLabels()
