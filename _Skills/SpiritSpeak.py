import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster

importlib.reload(_Caster)

from _Caster import Caster


class SpiritSpeak(Caster):
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
            "Spirit Speak",
            skillCap,
            label,
            skillLevelLabel,
            spellLabel,
            runningLabel,
        )

    def _trainer(self, skillLevel, spells):
        API.UseSkill("Spirit Speak")
        API.Pause(10.2)

    def _target(self):
        pass
