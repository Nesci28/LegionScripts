#=========== Consolidated Imports ============#
import API


#=========== Start of .\Farm\auto-heal.py ============#

HEAL_THRESHOLD_PERCENT = 90
LOOP_TIMER = 0.1
RECALCULATE_HEALTH_ON_EVERY_LOOP = False

# Do not touch below

minHealth = int(HEAL_THRESHOLD_PERCENT * API.Player.HitsMax / 100)

while not API.StopRequested:
    if RECALCULATE_HEALTH_ON_EVERY_LOOP:
        minHealth = int(HEAL_THRESHOLD_PERCENT * API.Player.HitsMax / 100)
    if API.Player.Hits <= minHealth:
        API.CastSpell("Greater Heal")
        API.WaitForTarget()
        API.TargetSelf()
    if API.Player.IsPoisoned:
        API.CastSpell("Arch Cure")
        API.WaitForTarget()
        API.TargetSelf()
    API.Pause(LOOP_TIMER)
#=========== End of .\Farm\auto-heal.py ============#

