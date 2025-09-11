import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster

importlib.reload(_Caster)

from _Caster import Caster


class Necromancy(Caster):
    spells = [
        {
            "skill": 50,
            "spell": "Pain Spike",
            "manaCost": 5,
            "castingTime": 0.75,
        },
        {
            "skill": 70,
            "spell": "Horrific Beast",
            "manaCost": 11,
            "castingTime": 1.75,
        },
        {
            "skill": 90,
            "spell": "Wither",
            "manaCost": 23,
            "castingTime": 1,
        },
        {
            "skill": 100,
            "spell": "Lich Form",
            "manaCost": 25,
            "castingTime": 1.75,
        },
        {
            "skill": 120,
            "spell": "Vampiric Embrace",
            "manaCost": 25,
            "castingTime": 1.75,
        },
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, Necromancy.spells)
        if not hasSpellValidation:
            errors.append("Necromancy - Missing spells.")
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
            "Necromancy", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = Necromancy.spells

    def _target(self):
        API.TargetSelf()
