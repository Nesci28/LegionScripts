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
        npcs = API.NearestMobiles([API.Notoriety.Invulnerable], 1)
        for npc in npcs:
            API.SysMsg(npc.Title)


Debug().main()
