import API
import random
import json

# ===== USER CONFIGS =====
isLooting = False
trainBushido = False
runeBookSerial = 0x468AD8F3
mapsBagSerial = 0x4616DF16
unravelItemsBagSerial = 0x407B2C55
keepItemsBagSerial = 0x407B2C56
darkGuardianRuneIndex = 13
dropoffRuneIndex = 14
# ===== END USER CONFIGS =====

# ===== GLOBAL STATE =====
lsMana = 10
wwMana = 15
dsMana = 30
originX = API.Player.X
originY = API.Player.Y
toDropoffCoord = {"x": 2105, "y": 2320, "z": 7}
toOutsideGuardianRoomCoord = {"x": 350, "y": 15, "z": -1}
toGuardianCoord = {"x": 365, "y": 15, "z": -1}
# ========================

f = open("C:\Games\Taz_BleedingEdge\TazUO-Launcher.win-x64\TazUO\LegionScripts\spelldef.json")
spells = json.load(f)

def randomDirection():
    return random.choice([
        "East", "West", "South", "North",
        "Southeast", "Northeast", "Southwest", "Northwest"
    ])

def getDirection(fromX, fromY, toX, toY):
    dx, dy = toX - fromX, toY - fromY
    if dx > 0 and dy == 0: return "East"
    if dx < 0 and dy == 0: return "West"
    if dy > 0 and dx == 0: return "South"
    if dy < 0 and dx == 0: return "North"
    if dx > 0 and dy > 0: return "Southeast"
    if dx > 0 and dy < 0: return "Northeast"
    if dx < 0 and dy > 0: return "Southwest"
    if dx < 0 and dy < 0: return "Northwest"
    return None

def walk(direction):
    API.Walk(direction)
    API.Pause(0.045)

def simpleWalkTo(targetX, targetY, maxRetries=500):
    retries = 0
    while (API.Player.X != targetX or API.Player.Y != targetY) and retries < maxRetries:
        dx = targetX - API.Player.X
        dy = targetY - API.Player.Y
        direction = getDirection(API.Player.X, API.Player.Y, targetX, targetY)
        walk(direction if direction else randomDirection())
        API.Pause(0.15)
        retries += 1
    if retries >= maxRetries:
        API.SysMsg("simpleWalkTo failed: too many retries", 33)

def moveToCoordinates(targetX, targetY):
    simpleWalkTo(targetX, targetY)

def isSpellFizzled(spellName):
    s = None
    for spell in spells:
        if spell["Name"].lower() == spellName.lower():
            s = spell
            break
    if not s:
        raise Exception(f"Invalid spellName: {spellName}!")
    API.ClearJournal()
    iterations = int(s["CastTime"] / 0.1)
    for _ in range(iterations):
        if API.InJournalAny([
            "You lost your concentration.",
            "Your spell fizzles.",
            "You can't cast that spell right now.",
            "You fail to cast"
        ]):
            API.SysMsg("Spell fizzled!", 33)
            return True
        API.Pause(0.1)
    return False

def detectRecallMethod():
    magery = API.GetSkill("Magery").Value
    chivalry = API.GetSkill("Chivalry").Value

    if magery >= 40:
        return "magery"
    elif chivalry >= 40:
        return "chilvary"
    else:
        API.SysMsg("No travel skill detected. Need Magery or Chivalry!", 33)
        API.Stop()

def recallToLocation(index, runebookItem):
    method = detectRecallMethod()
    API.UseObject(runebookItem)
    API.Pause(1)
    if not API.HasGump(89):
        API.SysMsg("Runebook's gump did not open")
        return

    API.ClearJournal()
    if method == "magery":
        API.ReplyGump(index + 50, 89)
    else:
        API.ReplyGump(index + 74, 89)
    while isSpellFizzled("recall"):
        return recallToLocation(index, runebookItem)

def findEnemies():
    return API.NearestMobiles([API.Notoriety.Enemy], maxDistance=12)

def attack(enemy):
    API.Target(enemy.Serial)
    API.Attack(enemy.Serial)
    API.Pause(1.0)

def engageEnemies():
    enemy = findEnemies()
    if not enemy:
        return False
    while enemy:
        for e in enemy:
            attack(e)
            API.Pause(0.5)
        API.Pause(1.0)
        enemy = findEnemies()
    return True

def castEvasionIfTraining():
    if trainBushido:
        API.CastSpell("Evasion")

def moveToDarkGuardians():
    global originX, originY
    recallToLocation(darkGuardianRuneIndex, runeBookSerial)
    moveToCoordinates(toGuardianCoord["x"], toGuardianCoord["y"])
    originX = API.Player.X
    originY = API.Player.Y

def offload():
    recallToLocation(dropoffRuneIndex, runeBookSerial)
    moveToCoordinates(toDropoffCoord["x"], toDropoffCoord["y"])
    API.SysMsg("Drop-off: Trash/unravel/keep logic not fully implemented in Legion", 33)
    moveToDarkGuardians()

def moveToOrigin():
    moveToCoordinates(originX, originY)

def wiggle():
    maxRadius = 7
    for _ in range(30):
        offsetX = random.randint(-maxRadius, maxRadius)
        offsetY = random.randint(-maxRadius, maxRadius)
        if abs(offsetX) + abs(offsetY) < 2:
            continue
        targetX = originX + offsetX
        targetY = originY + offsetY
        moveToCoordinates(targetX, targetY)
        API.Pause(random.uniform(0.5, 1.0))
        moveToCoordinates(originX, originY)
        return

def main():
    moveToDarkGuardians()
    while not API.Player.IsDead:
        fought = engageEnemies()
        if fought:
            castEvasionIfTraining()
            moveToOrigin()
            offload()
        else:
            API.Pause(1.0)
            wiggle()

main()