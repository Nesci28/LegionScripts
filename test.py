import API
from LegionPath import LegionPath
import importlib

LegionPath.addSubdirs()


serial = API.RequestTarget()
animal = API.FindMobile(serial)
API.SysMsg(str(animal.Hits))