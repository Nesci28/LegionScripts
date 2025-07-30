import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)

import _Caster
import Util
import Magic

importlib.reload(Util)
importlib.reload(Magic)
importlib.reload(_Caster)
from _Caster import Caster


class EvaluatingIntelligence(Caster):
    spells = [
        {
            "skill": 120,
            "spell": "Reactive Armor",
            "manaCost": 4,
            "castingTime": 1.0,
        }
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, EvaluatingIntelligence.spells)
        if not hasSpellValidation:
            errors.append("Evaluating Intelligence - Missing spells.")
        return errors

    def __init__(
        self,
        skillCap,
        label=None,
        skillLevelLabel=None,
        spellLabel=None,
        runningLabel=None,
    ):
        super().__init__(
            "Evaluating Intelligence",
            skillCap,
            label,
            skillLevelLabel,
            spellLabel,
            runningLabel,
        )
        self.spells = EvaluatingIntelligence.spells

    def _target(self):
        pass
