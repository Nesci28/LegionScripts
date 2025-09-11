import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster
import Util
import Math

importlib.reload(_Caster)
from _Caster import Caster

importlib.reload(Util)
importlib.reload(Math)


class Mysticism(Caster):
    spells = [
        {
            "skill": 60,
            "spell": "Stone Form",
            "manaCost": 11,
            "castingTime": 1.25,
        },
        {
            "skill": 80,
            "spell": "Cleansing Winds",
            "manaCost": 20,
            "castingTime": 1.75,
        },
        {
            "skill": 95,
            "spell": "Hail Storm",
            "manaCost": 50,
            "castingTime": 2,
        },
        {
            "skill": 120,
            "spell": "Nether Cyclone",
            "manaCost": 50,
            "castingTime": 2.25,
        },
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, Mysticism.spells)
        if not hasSpellValidation:
            errors.append("Mysticism - Missing spells.")
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
            "Mysticism", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = Mysticism.spells

    def _target(self):
        API.TargetSelf()
