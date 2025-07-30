import API
import json
import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Classes"
)

import Util
import Bod
import Craft

importlib.reload(Util)
importlib.reload(Bod)
importlib.reload(Craft)

selectedSkill = "Tailoring"

bodSkillsJson = open(
    r".\\TazUO\\LegionScripts\\_Jsons\\bod-skills.json"
)
bodSkillsStr = json.load(bodSkillsJson)
bodSkills = Util.Util.convertToHex(bodSkillsStr)

def main():
    bods = []

    bodSkill = bodSkills[selectedSkill]
    selectedBodGraphic = bodSkill["bod"]["graphic"]
    selectedBodHue = bodSkill["bod"]["hue"]

    items = Util.Util.itemsInContainer(API.Backpack)
    for item in items:
        if (
            item.Graphic != selectedBodGraphic
            or item.Hue != selectedBodHue
            or Bod.Bod.isSmallBod(item)
        ):
            continue
        bod = Bod.Bod(bodSkill, item)
        bods.append(bod)

    unfilledLargeBods = []
    for bod in bods:
        isFilled = Bod.Bod.isFilled(bod.item)
        if not isFilled:
            unfilledLargeBods.append(bod)  
  
    API.SysMsg(f"Unfilled Large Bods found: {len(unfilledLargeBods)}")
  
    for bod in unfilledLargeBods:
        bod.fill()

main()
