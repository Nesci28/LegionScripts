import API
import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Classes"
)

import Magic
import Item

importlib.reload(Magic)
importlib.reload(Item)

magic = Magic.Magic()
amount = API.FindType(2427).Amount
while amount < 20:
    magic.cast("Create Food")
    amount = API.FindType(2427).Amount