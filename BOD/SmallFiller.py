import API
import json
import importlib
import sys

sys.path.append(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts"
)
sys.path.append(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts\\_Utils"
)
sys.path.append(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts\\_Classes"
)

import Util
import Bod
import Craft

importlib.reload(Util)
importlib.reload(Bod)
importlib.reload(Craft)

selectedSkill = "Blacksmithy"

bodSkillsJson = open(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts\\_Jsons\\bod-skills.json"
)
bodSkillsStr = json.load(bodSkillsJson)
bodSkills = Util.Util.convertToHex(bodSkillsStr)

craftingInfosJson = open(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts\\_Jsons\\crafting-infos.json"
)
craftingInfosStr = json.load(craftingInfosJson)
craftingInfos = Util.Util.convertToHex(craftingInfosStr)


def main():
    resourceChestSerial = API.RequestTarget()
    resourceChest = API.FindItem(resourceChestSerial)
    Util.Util.openContainer(resourceChest)

    trash = API.FindType(0x0E77, 4294967295, 2)
    if not trash:
        API.SysMsg("No trash found", 33)
        API.Stop()
    salvageBag = API.FindType(0x0E76, API.Backpack, hue=0x024E)
    if not salvageBag:
        API.SysMsg("No salvage bag found", 33)
        API.Stop()

    bodSkill = bodSkills[selectedSkill]
    selectedBodGraphic = bodSkill["bod"]["graphic"]
    selectedBodHue = bodSkill["bod"]["hue"]

    craftingInfo = craftingInfos[selectedSkill]

    bods = []

    items = Util.Util.itemsInContainer(API.Backpack)
    for item in items:
        if (
            item.Graphic != selectedBodGraphic
            or item.Hue != selectedBodHue
            or not Bod.Bod.isSmallBod(item)
        ):
            continue
        API.SysMsg("1")
        craft = Craft.Craft(bodSkill, craftingInfo, resourceChest)
        API.SysMsg("2")
        bod = Bod.Bod(bodSkill, item, craftingInfo, craft)
        API.SysMsg("3")
        bods.append(bod)

    unfilledBods = []

    for bod in bods:
        isFilled = Bod.Bod.isFilled(bod.item)
        if not isFilled:
            unfilledBods.append(bod)
  
    API.SysMsg(f"Unfilled Small Bods found: {len(unfilledBods)}")
  
    for bod in unfilledBods:
        bod.fill()


main()
