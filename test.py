import API
from LegionPath import LegionPath

LegionPath.addSubdirs()

mobiles = API.GetAllMobiles(None, 1, [API.Notoriety.Unknown, API.Notoriety.Innocent, API.Notoriety.Ally])
for mobile in mobiles:
    API.SysMsg(str(mobile.IsDead))
