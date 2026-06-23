import importlib

import _Crafting

importlib.reload(_Crafting)

from _Crafting import CraftingSkill


class Tinkering(CraftingSkill):
    skillName = "Tinkering"
