import API
import importlib
import sys
import json

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Classes"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)

import Util
import Bod

importlib.reload(Util)
importlib.reload(Bod)

bodSkillsJson = open(
    r".\\TazUO\\LegionScripts\\_Jsons\\bod-skills.json"
)
bodSkillsStr = json.load(bodSkillsJson)
bodSkills = Util.Util.convertToHex(bodSkillsStr)

selectedSkill = "Tailoring"


def main():
    bodSkill = bodSkills[selectedSkill]
    selectedBodGraphic = bodSkill["bod"]["graphic"]
    selectedBodHue = bodSkill["bod"]["hue"]
    bods = []
    items = Util.Util.itemsInContainer(API.Backpack)
    for item in items:
        if (
            item.Graphic != selectedBodGraphic
            or item.Hue != selectedBodHue
            or not Bod.Bod.isSmallBod(item)
        ):
            continue        
        bod = Bod.Bod(bodSkill, item)
        bods.append(bod)

    unBridedBods = []
    for bod in bods:
        isBribed = Bod.Bod.isMaxed(bod.item)
        if not isBribed:
            unBridedBods.append(bod)

    API.SysMsg(f"Found {len(unBridedBods)} bods")

    for bod in unBridedBods:
        bod.bride()


main()
