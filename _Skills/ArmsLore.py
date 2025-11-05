import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)

from Util import Util


class ArmsLore:
    def __init__(self, skillCap=API.GetSkill("Arms Lore").Cap):
        self.skillCap = skillCap
        self.weapon = Util.findItemWithProps(
            ["One-handed Weapon"]
        ) or Util.findItemWithProps(["Two-handed Weapon"])
        if not self.weapon:
            API.SysMsg("Need a weapon in inventory", 33)
            API.Stop()
        API.SetSkillLock("Arms Lore", "up")

    def trainOnce(self):
        API.UseSkill("Arms Lore")
        API.WaitForTarget("any", 3)
        API.Target(self.weapon)
        API.Pause(1.3)

    def train(self):
        value = API.GetSkill("Arms Lore").Value
        while value < self.skillCap:
            self.trainOnce()
