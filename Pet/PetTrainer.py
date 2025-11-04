import API
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)

from Util import Util

petSerials = []

for mob in API.GetAllMobiles():
    if mob.IsRenamable and not mob.IsHuman:
        petSerials.append(mob.Serial)

while not API.StopRequested:
    enemies = Util.scanEnemies(15)
    wizard = None
    for enemy in enemies:
        if enemy.Graphic == 0x0190:
            wizard = enemy
    if wizard:
        for petSerial in petSerials:
            pet = API.FindMobile(petSerial)
            if not pet.InWarMode:
                API.Msg("All kill")
                API.WaitForTarget()
                API.Target(enemy.Serial)

    API.Pause(1)