import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
import Util

importlib.reload(Util)


class Refinement:
    @staticmethod
    def isItemRefinement(item):
        isRefinement = item.Graphic in [5162, 5163, 11617, 19672, 19674, 19673]
        return isRefinement

    @staticmethod
    def _parse(item):
        if not Refinement.isItemRefinement(item):
            API.SysMsg("Item is not a refinement", 33)
            API.Stop()
        props = API.ItemNameAndProps(item.Serial).split("\n")
        itemName = props[0]
        type = itemName.split(" ")[0]
        armorTypeStr = props[2]
        level = Refinement._getLevel(itemName)
        armorType = armorTypeStr.split(": ")[1]
        return {"itemName": itemName, "type": type, "level": level, "armorType": armorType}

    @staticmethod
    def _getLevel(name):
        n = name.lower()
        if "defense" in n:
            return 1
        if "protection" in n:
            return 2
        if "hardening" in n:
            return 3
        if "fortification" in n:
            return 4
        if "invulnerability" in n:
            return 5
        API.SysMsg("Level not found", 33)
        API.Stop()

    def __init__(self, item):
        self.item = item
        self._setup()
        
    def _setup(self):
        values = Refinement._parse(self.item)
        self.itemName = values["itemName"]
        self.level = values["level"]
        self.armorType = values["armorType"]
        self.type = values["type"]

