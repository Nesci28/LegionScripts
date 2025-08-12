import API
import importlib
import sys
import traceback
from collections import OrderedDict

sys.path.append(r".\\TazUO\\LegionScripts\\_Classes")
sys.path.append(r".\\TazUO\\LegionScripts\\_Utils")
sys.path.append(r".\\TazUO\\LegionScripts\\_Skills")

import Gump
import Util
import Math
import Musicianship
import Peacemaking
import Magic

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Musicianship)
importlib.reload(Peacemaking)
importlib.reload(Magic)

from Gump import Gump
from Util import Util
from Math import Math
from Musicianship import Musicianship
from Peacemaking import Peacemaking
from Magic import Magic


class Debug:
    magic = Magic()
    
    def main(self):
        container = API.FindItem(0x41C617E5)
        Util.openContainer(container)
        # API.SysMsg(str(container))
        resourceInChest = Util.findTypeWithSpecialHue(
            3966,
            container,
            200,
            0,
        )
        API.SysMsg(str(resourceInChest))


Debug().main()
