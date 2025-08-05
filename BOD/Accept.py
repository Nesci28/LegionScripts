import API
import time
import importlib
import sys
import json

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Classes"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
import Bod
import Util
import Math

importlib.reload(Bod)
importlib.reload(Util)
importlib.reload(Math)

from Bod import Bod
from Util import Util
from Math import Math

bodSkillsJson = open(
    r".\\TazUO\\LegionScripts\\_Jsons\\bod-skills.json"
)
bodSkillsStr = json.load(bodSkillsJson)
bodSkills = Math.convertToHex(bodSkillsStr)

selectedSkill = "Tailoring"
tailorNpcSerial = 0x0046ACAC  # First spot (Cyrus)


def getFilledSmallBods():
    bodSkill = bodSkills[selectedSkill]
    selectedBodGraphic = bodSkill["bod"]["graphic"]
    selectedBodHue = bodSkill["bod"]["hue"]
    smallBods = Bod.findAllBodItems(selectedBodGraphic, selectedBodHue, True)
    fullSmallBods = []
    for smallBod in smallBods:
        if Bod.isFilled(smallBod, False):
            fullSmallBods.append(smallBod)
    return fullSmallBods

def main():
    filledSmallBods = getFilledSmallBods()
    while len(filledSmallBods) > 0:
        filledSmallBod = filledSmallBods.pop()
        Util.moveItem(filledSmallBod.Serial, tailorNpcSerial)
        API.ContextMenu(tailorNpcSerial, 403)
        start_time = time.time()
        while not API.HasGump(455):
            if time.time() - start_time > 1:
                API.SysMsg("Timeout", 33)
                API.CancelTarget()
                break
            API.Pause(0.1)
        API.ReplyGump(1, 455)
        filledSmallBods = getFilledSmallBods()


main()
