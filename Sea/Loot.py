import API
import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Classes"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
import Util

importlib.reload(Util)

beetleSerial = 0x07869E50

chestSerial = API.RequestTarget()
chest = API.FindItem(chestSerial)

Util.Util.openContainer(chest)
items = Util.Util.itemsInContainer(chest)
for item in items:
    if item.Graphic in [7154, 7127, 4225, 17619, 17617]:
        Util.Util.moveItem(item.Serial, beetleSerial)
    if item.Graphic == 7136 and item.Hue == 1193:
        Util.Util.moveItem(item.Serial, beetleSerial)

    if item.Graphic in [16932, 41662, 3758, 5162, 3785, 11617, 19672, 19673, 19674, 41668, 5152, 5163]:
        Util.Util.moveItem(item.Serial, API.Backpack)
    if item.Graphic == 5362 and item.Hue == 1117:
        Util.Util.moveItem(item.Serial, API.Backpack)

    if item.Graphic == 4216 and item.Hue in [2220, 2117, 2129]:
        Util.Util.moveItem(item.Serial, API.Backpack)
        scissor = API.FindType(3998)
        API.UseObject(scissor)
        API.WaitForTarget()
        API.Target(item.Serial)
        API.Pause(1)
        backpackItems = Util.Util.itemsInContainer(API.Backpack)
        for backpackItem in backpackItems:
            if backpackItem.Graphic in [4225]:
                Util.Util.moveItem(backpackItem.Serial, beetleSerial)