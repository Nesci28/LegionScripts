import API
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)

from Util import Util

# ========== Configurable Toggles ==========
isDestroyingCorpse = True
takeLeather = True
takeMeat = False
takeFeathers = False
takeWool = False
takeScales = False
takeBlood = False

# ========== Item IDs ==========
leather = 0x1081
hide = 0x1078
meat = 0x09F1
rotwormMeat = 0x2DB9
pultry = 0x09B9
feathers = 0x1BD1
wool = 0x0DF8
lambLeg = 0x1609
dragonScale = 0x26B4
dragonBlood = 0x4077

daggerIds = [
    0x2D2C,  # Harvester's Blade
    0x0F52,  # Dagger
    0x0EC4,  # Skinning Knife
    0x0EC3,  # Butcher's Cleaver
    0x13F6,  # Butcher's Knife
    0x13B6   # Butcher's Knife
]

def getItemName(serial):
    info = API.ItemNameAndProps(serial, True)
    return info[0] if info else ""

def findDagger():
    for dag in daggerIds:
        found = API.FindType(dag, API.Backpack)
        if found:
            return found

    rightHand = API.FindLayer("RightHand")
    leftHand = API.FindLayer("LeftHand")
    if rightHand and rightHand.Graphic in daggerIds:
        return rightHand
    if leftHand and leftHand.Graphic in daggerIds:
        return leftHand

    API.SysMsg("Unable to locate preset dagger", 201)
    return None

def lootItems(container, graphic, nameFilter=None):
    for item in API.ItemsInContainer(container):
        if item.Graphic == graphic and (nameFilter is None or nameFilter in item.Name):
            API.MoveItem(item.Serial, API.Backpack, item.Amount)
            API.Pause(0.1)

def dumpItems(corpse, graphic, nameFilter=None):
    for item in API.ItemsInContainer(API.Backpack):
        if item.Graphic == graphic and (nameFilter is None or nameFilter in item.Name):
            API.MoveItem(item.Serial, corpse, item.Amount)
            API.Pause(0.2)

def runButcher():
    API.ClearJournal()
    dagger = findDagger()
    if not dagger:
        return

    isHarvestersBlade = getItemName(dagger.Serial) == "Harvester's Blade"

    corpse = API.NearestCorpse(2)
    if not corpse or corpse.Serial == 0:
        return

    API.UseObject(dagger.Serial)
    API.WaitForTarget("neutral")
    API.Target(corpse.Serial)
    API.Pause(0.5)
    if API.InJournalAny(["$You skin it(.*)."]):
        if isDestroyingCorpse:
            corpse.Destroy()
        API.IgnoreObject(corpse.Serial)


    # if not isHarvestersBlade:
    #     if takeFeathers:
    #         lootItems(corpse.Serial, feathers)
    #     if takeMeat:
    #         lootItems(corpse.Serial, meat)
    #         lootItems(corpse.Serial, rotwormMeat)
    #         lootItems(corpse.Serial, pultry)
    #         lootItems(corpse.Serial, lambLeg)
    #     if takeLeather:
    #         lootItems(corpse.Serial, hide)
    #     if takeWool:
    #         lootItems(corpse.Serial, wool)
    #     if takeScales:
    #         lootItems(corpse.Serial, dragonScale)
    #     if takeBlood:
    #         lootItems(corpse.Serial, dragonBlood, "Dragon's Blood")
    # else:
    #     API.SysMsg("5")
    #     if not takeFeathers:
    #         dumpItems(corpse.Serial, feathers)
    #     if not takeLeather:
    #         dumpItems(corpse.Serial, leather)
    #     if not takeMeat:
    #         dumpItems(corpse.Serial, meat)
    #         dumpItems(corpse.Serial, pultry)
    #         dumpItems(corpse.Serial, lambLeg)
    #         dumpItems(corpse.Serial, rotwormMeat)
    #     if not takeWool:
    #         dumpItems(corpse.Serial, wool)
    #     if not takeScales:
    #         dumpItems(corpse.Serial, dragonScale)
    #     if not takeBlood:
    #         dumpItems(corpse.Serial, dragonBlood, "Dragon's Blood")

    # if isDestroyingCorpse:
    #     corpse.Destroy()
    # API.IgnoreObject(corpse.Serial)

API.OnHotKey("SHIFT+B", lambda: runButcher())
while not API.StopRequested:
    API.ProcessCallbacks()
    API.Pause(0.1)
