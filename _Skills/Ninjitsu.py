import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster

importlib.reload(_Caster)

from _Caster import Caster


class Ninjitsu(Caster):
    spells = [
        {
            "skill": 60,
            "spell": "Mirror Image",
            "manaCost": 10,
            "castingTime": 2,
        },
        {
            "skill": 70,
            "spell": "Focus Attack",
            "manaCost": 5,
            "castingTime": 2,
        },
        {
            "skill": 85,
            "spell": "Shadowjump",
            "manaCost": 15,
            "castingTime": 2,
        },
        {
            "skill": 120,
            "spell": "Death Strike",
            "manaCost": 10,
            "castingTime": 2,
        },
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, Ninjitsu.spells)
        if not hasSpellValidation:
            errors.append("Ninjitsu - Missing spells.")
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
            "Ninjitsu", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = Ninjitsu.Spells

    def _target(self):
        API.TargetSelf()
