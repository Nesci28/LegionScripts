import importlib
from decimal import Decimal
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster
import Util

importlib.reload(_Caster)
importlib.reload(Util)

from _Caster import Caster
from Util import Util


class AnimalTaming(Caster):
    spells = [
        {
            "skill": 120,
            "spell": "Combat Training",
            "manaCost": 40,
            "castingTime": 1,
        }
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, AnimalTaming.spells)
        if not hasSpellValidation:
            errors.append("Animal Taming - Missing spells.")
        skillValue = API.GetSkill("Animal Taming").Value
        if skillValue < 90:
            errors.append("Animal Taming - Should be higher then 90.")
        hasPet = AnimalTaming._findMyPets()
        if not hasPet:
            errors.append("Animal Taming - Missing pet.")
        return errors

    @staticmethod
    def _findMyPets():
        for mob in API.GetAllMobiles():
            if mob.IsRenamable and not mob.IsHuman:
                return mob
        return None

    def __init__(
        self,
        skillCap,
        label=None,
        skillLevelLabel=None,
        spellLabel=None,
        runningLabel=None,
    ):
        super().__init__(
            "Animal Taming", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = AnimalTaming.spells
        self.pet = AnimalTaming._findMyPets()

    def _target(self):
        API.Target(self.pet.Serial)
