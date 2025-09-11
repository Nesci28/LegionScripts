import API
from LegionPath import LegionPath
import importlib

LegionPath.addSubdirs()

import Util
importlib.reload(Util)

from Util import Util

API.SysMsg("Util")
