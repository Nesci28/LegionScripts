import API
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Math

importlib.reload(Math)


enemies = API.NearestMobiles([
    API.Notoriety.Enemy,
    API.Notoriety.Criminal,
    API.Notoriety.Gray,
    API.Notoriety.Innocent,
    API.Notoriety.Murderer
    ], 12)

closestDistance = 999
closestEnemy = None
for enemy in enemies:
    if enemy.IsRenamable:
        continue
    distance = Math.Math.distanceBetween(API.Player, enemy)
    if distance < closestDistance:
        closestDistance = distance
        closestEnemy = enemy

if closestEnemy:
    API.HeadMsg(f"Enemy Located: {closestEnemy.Name}", closestEnemy.Serial)
    API.Dismount()
    API.Msg("All Kill")
    API.WaitForTarget()
    API.Target(closestEnemy)
else:
    API.Mount()
