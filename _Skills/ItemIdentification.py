import importlib
try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass
# API is injected by TazUO at runtime; the import above is IDE-only.
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)


class ItemIdentification:
    def __init__(self, skillCap=None):
        if skillCap is None:
            skillCap = API.GetSkill("Item Identification").Cap
        self.skillCap = skillCap
        self.weapon = Util.Util.findItemWithProps(
            ["One-handed Weapon"]
        ) or Util.Util.findItemWithProps(["Two-handed Weapon"])
        if not self.weapon:
            API.SysMsg("Need a weapon in inventory", 33)
            API.Stop()
        API.SetSkillLock("Item Identification", "up")

    def trainOnce(self):
        API.UseSkill("Item Identification")
        API.WaitForTarget("any", 3)
        API.Target(self.weapon)
        API.Pause(1.3)

    def train(self):
        value = API.GetSkill("Item Identification").Value
        while value < self.skillCap:
            self.trainOnce()
