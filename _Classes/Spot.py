import importlib

import Util

importlib.reload(Util)

from Util import Util

class Spot:
    def __init__(self, minLevel, maxLevel, x, y):
        self.minLevel = minLevel
        self.maxLevel = maxLevel
        self.x = x
        self.y = y

    def isRightSpot(self, skillName):
        values = Util.getSkillInfo(skillName)
        value = values["value"]
        return value >= self.minLevel and value <= self.maxLevel

    def move(self):
        hasPath = API.GetPath(self.x, self.y)
        if hasPath:
            API.Pathfind(self.x, self.y)