import importlib
import sys

sys.path.append(r".\\TazUO\\LegionScripts\\_Utils")

import _Music
import Util

importlib.reload(Util)
importlib.reload(_Music)

from _Music import Music
from Util import Util


class Peacemaking(Music):
    def __init__(self, running=None, skillCap=None):
        self.running = running
        self.skillCap = skillCap or API.GetSkill("Peacemaking").Cap
        self.instruments = self._findInstruments()
        self.skillName = "Peacemaking"
        self._done = False
        API.SetSkillLock(self.skillName, "up")

    def trainOnce(self):
        errors = Music.validate()
        if errors:
            Util.error(f"{self.skillName} - Missing instruments")
        self.use(API.Player.Serial)
        API.Pause(6)

    def train(self, calculateSkillLabels=None):
        if not self.running() or self._done:
            return True
        if Util.getSkillInfo(self.skillName)["value"] >= self.skillCap:
            self._done = True
            return True
        self.trainOnce()
        if calculateSkillLabels:
            calculateSkillLabels()
        return False

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