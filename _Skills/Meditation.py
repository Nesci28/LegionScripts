import importlib
import sys

sys.path.append(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts\\_Utils"
)

import _Caster
import Util
import Magic

importlib.reload(Util)
importlib.reload(Magic)
importlib.reload(_Caster)
from _Caster import Caster


class Meditation(Caster):
    @staticmethod
    def validate(skillCap):
        return []

    def __init__(
        self,
        skillCap,
        label=None,
        skillLevelLabel=None,
        spellLabel=None,
        runningLabel=None,
    ):
        super().__init__(
            "Meditation", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )

    def trainOnce(self):
        self.magic.cast("Clumsy")

    def train(self):
        value = API.GetSkill("Meditation").Value
        while value < self.skillCap:
            self.trainOnce()
