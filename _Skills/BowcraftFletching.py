import importlib
from decimal import Decimal

import _Crafting

importlib.reload(_Crafting)

from _Crafting import CraftingSkill


class BowcraftFletching(CraftingSkill):
    skillName = "Bowcraft/Fletching"

    @classmethod
    def validate(cls, skillCap=None):
        errors = super().validate(skillCap)
        skill = _Crafting.API.GetSkill(cls.skillName)
        if not skill:
            errors.append(f"{cls.skillName} - API.GetSkill returned None.")
        elif Decimal(str(skill.Value)) < Decimal("30"):
            errors.append(f"{cls.skillName} - Buy skill to 30.0 before using trainer.")
        return errors
