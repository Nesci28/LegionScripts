try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass
# API is injected by TazUO at runtime; the import above is IDE-only.
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