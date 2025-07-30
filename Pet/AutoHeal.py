import API
import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)

import Math

importlib.reload(Math)


# Settings
useMagery = True
useMageryHighHP = True
useVet = False
bandageSerial = API.Backpack

petSerials = []
petMobiles = []

# -- Movement Detection --
def isMoving():
    return API.Player.IsWalking

# -- Targeted Cast --
def castAtTarget(spell, level, targetSerial, poisonCheck=0):
    if not API.WaitForTarget("Beneficial", fcDelay(level)):
        return False
    mob = API.FindMobile(targetSerial)
    if not mob or Math.Math.distanceBetween(API.Player, mob) > 10:
        return False
    if poisonCheck == 1 and not mob.IsPoisoned:
        return False
    if poisonCheck == -1 and mob.IsPoisoned:
        return False
    API.Target(targetSerial)
    API.CreateCooldownBar(fcrDelay() / 1000.0, f"{spell} Cooldown", 88)
    return True

# -- HP Percent Helper --
def mobilePercentHP(mob):
    return min(100, int((mob.Hits / 25.0) * 100))

# -- Pet Management --
def findMyPets():
    global petSerials
    petSerials.clear()
    for mob in API.GetAllMobiles():
        if mob.IsRenamable and not mob.IsHuman:
            petSerials.append(mob.Serial)
    if petSerials:
        for s in petSerials:
            mob = API.FindMobile(s)
            if mob:
                API.HeadMsg(f"Pet Located: {mob.Name}", s)

def rebuildPetList():
    global petMobiles
    petMobiles.clear()
    for s in petSerials:
        m = API.FindMobile(s)
        if m:
            petMobiles.append(m)

# -- Healing Logic --
def curePets(healthPercent):
    if isMoving() or not useMagery or API.Player.Mana < 15 or API.BuffExists("Veterinary"):
        return False
    rebuildPetList()
    for mob in petMobiles:
        if mob.IsPoisoned and mobilePercentHP(mob) < healthPercent and Math.Math.distanceBetween(API.Player, mob) <= 10:
            API.CastSpell("Arch Cure")
            return castAtTarget("Arch Cure", 4, mob.Serial, 1)
    return False

def healPets(healthPercent):
    if isMoving() or not useMagery or API.Player.Mana < 15 or API.BuffExists("Veterinary"):
        return False
    rebuildPetList()
    for mob in petMobiles:
        isGhost = mob.Hits == 0
        if not isGhost and not mob.IsPoisoned and mobilePercentHP(mob) < healthPercent and Math.Math.distanceBetween(API.Player, mob) <= 10:
            API.CastSpell("Greater Heal")
            return castAtTarget("Greater Heal", 4, mob.Serial, -1)
    return False

def vetPets(healthPercent):
    if not useVet or API.BuffExists("Veterinary"):
        return False
    rebuildPetList()
    for mob in petMobiles:
        if Math.Math.distanceBetween(API.Player, mob) > 2:
            continue
        if mobilePercentHP(mob) >= healthPercent and not mob.IsPoisoned:
            continue
        bandage = API.FindType(0x0E21, bandageSerial)
        if bandage:
            API.UseObject(bandage.Serial)
            if API.WaitForTarget("Beneficial", 2):
                API.Target(mob.Serial)
            API.Pause(0.25)
            return True
    return False

def usePriority():
    if vetPets(80): return True
    if curePets(50): return True
    if healPets(50): return True
    if curePets(95): return True
    if useMageryHighHP and healPets(90): return True
    if vetPets(90): return True
    return False

# -- Initialization --
findMyPets()
API.HeadMsg("Heal Pets Ready!", API.Player)

# -- Main Loop --
while True:
    if not API.Player.IsDead:
        while petSerials:
            rebuildPetList()
            if not petMobiles:
                break
            if usePriority():
                API.Pause(0.4)
                continue
            API.Pause(0.4)
        findMyPets()
        API.Pause(0.5)
    else:
        API.Pause(1.0)
