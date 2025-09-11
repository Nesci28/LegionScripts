import API
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Magic
import Item

importlib.reload(Magic)
importlib.reload(Item)

magic = Magic.Magic()
amount = API.FindType(2427).Amount
while amount < 20:
    magic.cast("Create Food")
    amount = API.FindType(2427).Amount