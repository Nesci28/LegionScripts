import importlib
from decimal import Decimal
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)

from Util import Util


class AnimalLore:
    @staticmethod
    def validate(skillCap):
        errors = []
        hasPet = AnimalLore._findMyPets()
        if not hasPet:
            errors.append("Animal Lore - Missing pet.")
        return errors

    @staticmethod
    def _findMyPets():
        for mob in API.GetAllMobiles():
            if mob.IsRenamable and not mob.IsHuman:
                return mob
        return None

    def __init__(self, skillCap=API.GetSkill("Animal Lore").Cap):
        self.skillCap = skillCap
        self.pet = AnimalLore._findMyPets()
        API.SetSkillLock("Animal Lore", "up")

    def trainOnce(self):
        API.UseSkill("Animal Lore")
        API.WaitForTarget("any", 3)
        API.Target(self.pet.Serial)
        API.WaitForGump(475)
        API.Pause(0.1)
        API.CloseGump(475)
        API.Pause(1.1)

    def train(self, calculareSkillLabels):
        value = API.GetSkill("Animal Lore").Value
        while Decimal(float(value)) < Decimal(self.skillCap):
            self.trainOnce()
            calculareSkillLabels()


                    