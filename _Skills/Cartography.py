import importlib

import _Crafting

importlib.reload(_Crafting)

from _Crafting import CraftingSkill


class Cartography(CraftingSkill):
    skillName = "Cartography"
