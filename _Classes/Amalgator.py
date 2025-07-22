import importlib
import sys

sys.path.append(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts\\_Utils"
)
import Util

importlib.reload(Util)


class Amalgator:
    @staticmethod
    def isItemAmalgator(item):
        isAmalgator = item.Graphic == 39270
        return isAmalgator

    @staticmethod
    def isItemEmpty(item):
        isEmpty = item.Hue == 1152
        return isEmpty

    @staticmethod
    def _parse(item):
        if not Amalgator.isItemAmalgator(item):
            raise Exception("Item is not a amalgator")
        if Amalgator.isItemEmpty(item):
            return {
                "itemName": None,
                "type": None,
                "level": None,
                "armorType": None,
                "amountAlreadyFilled": None,
                "amountToFile": None,
                "isEmpty": True,
            }
        props = API.ItemNameAndProps(item.Serial).split("\n")
        itemName = props[2]
        armorTypeStr = props[3]
        type = itemName.split(" ")[0]
        level = Amalgator._getLevel(itemName)
        armorType = armorTypeStr.split(": ")[1]
        amountStr = props[5].split(": ")[1]
        amounts = amountStr.split("/")
        amountAlreadyFilled = amounts[0]
        amountToFile = amounts[1]
        return {
            "itemName": itemName,
            "type": type,
            "level": level,
            "armorType": armorType,
            "amountAlreadyFilled": amountAlreadyFilled,
            "amountToFile": amountToFile,
            "isEmpty": False,
        }

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
        raise Exception("Level not found")

    def __init__(self, item):
        self.item = item
        self._setup()

    def _setup(self):
        values = Amalgator._parse(self.item)
        self.itemName = values["itemName"]
        self.type = values["type"]
        self.level = values["level"]
        self.armorType = values["armorType"]
        self.amountAlreadyFilled = values["amountAlreadyFilled"]
        self.amountToFile = values["amountToFile"]
        self.isEmpty = values["isEmpty"]
