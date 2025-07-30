import API
import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Classes"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
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
    API.Msg("All Kill")
    API.WaitForTarget()
    API.Target(closestEnemy)
