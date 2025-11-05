import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster
import Util

importlib.reload(_Caster)
importlib.reload(Util)

from _Caster import Caster
from Util import Util


class Magery(Caster):
    spells = [
        {
            "skill": 45,
            "spell": "Fireball",
            "manaCost": 9,
            "castingTime": 1,
        },
        {
            "skill": 55,
            "spell": "Lightning",
            "manaCost": 11,
            "castingTime": 1.25,
        },
        {
            "skill": 65,
            "spell": "Paralyze",
            "manaCost": 14,
            "castingTime": 1.5,
        },
        {
            "skill": 75,
            "spell": "Reveal",
            "manaCost": 20,
            "castingTime": 1.75,
        },
        {
            "skill": 90,
            "spell": "Flamestrike",
            "manaCost": 40,
            "castingTime": 2,
        },
        {
            "skill": 120,
            "spell": "Earthquake",
            "manaCost": 50,
            "castingTime": 2.25,
        },
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, Magery.spells)
        if not hasSpellValidation:
            errors.append("Magery - Missing spells.")
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
            "Magery", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = Magery.spells
        self.spellbook = API.FindType(0x0EFA, API.Backpack)
        if not self.spellbook:
            API.SysMsg("You need a spellbook in you inventory", 33)
            API.Stop()

    def _target(self):
        targetType = Util.getTypeOfTarget()
        if targetType == None:
            return
        if targetType == "Harmful":
            API.Target(self.spellbook.Serial)
        else:
            API.TargetSelf()
