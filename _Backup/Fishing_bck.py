############ README ############
#   If using a boat:    You must be at the very front of the boat
#                       Boat should be pointing East
#   If using a galleon: Place the npc on bottom right side of the boat
#                       Boat and Player must be facing North
#
################################

#############    Setup Section    ################
import API

# House
runeBookSerial = 0x467468CC
runeIndex = 14
homeWalkingSteps = [ "North", "North", "West", "West", "West", "North", "North", "North", "North", "East", "East" ]
sosContainerSerial = 0x427B44A2
otherContainerSerial = 0x4693B8B7
itemBeforeDroppingCount = 10

# Boat
isUsingGalleon = True
tillerManSerial = 0
shipKeySerial = 0
shipRuneIndex = 15
isKeepingAllFishes = True
cargoHoldSerial = 0x46EC4427
#cargoHoldSerial = None
#beetleSerial = 0x06208FC0
beetleSerial = None
tillerManSerial = 0
tillerManName = "Vera the pilot of the Titanic"
toPositionWalkingSteps = ["East", "East", "East"]

# Traps
isUsingTraps = False
isFishing = True
maxTrapCount = 45
beforePickingTrapsTimer = 1000 * 60 * 5
isDebugging = True

toKeepFishes = [
  { "name": "uncommon shiner", "qty": 0 },
  { "name": "brook trout", "qty": 0 },
  { "name": "bluegill sunfish", "qty": 0 },
  { "name": "smallmouth bass", "qty": 0 },
  { "name": "green catfish", "qty": 0 },
  { "name": "kokanee salmon", "qty": 0 },
  { "name": "walleye", "qty": 0 },
  { "name": "rainbow trout", "qty": 0 },
  { "name": "pike", "qty": 0 },
  { "name": "pumpkinseed sunfish", "qty": 0 },
  { "name": "yellow perch", "qty": 0 },
  { "name": "redbelly bream", "qty": 0 },

  { "name": "bonefish", "qty": 0 },
  { "name": "tarpon", "qty": 0 },
  { "name": "blue grouper", "qty": 0 },
  { "name": "cape cod", "qty": 0 },
  { "name": "yellowfin tuna", "qty": 0 },
  { "name": "gray snapper", "qty": 0 },
  { "name": "red drum", "qty": 0 },
  { "name": "shad", "qty": 0 },
  { "name": "captain snook", "qty": 0 },
  { "name": "mahi-mahi", "qty": 0 },
  { "name": "red grouper", "qty": 0 },
  { "name": "bonito", "qty": 0 },
  { "name": "cobia", "qty": 0 },
  { "name": "amberjack", "qty": 0 },
  { "name": "haddock", "qty": 0 },
  { "name": "bluefish", "qty": 0 },
  { "name": "red snook", "qty": 0 },
  { "name": "black seabass", "qty": 0 },

  { "name": "grim cisco", "qty": 0 },
  { "name": "infernal tuna ", "qty": 0 },
  { "name": "lurker fish ", "qty": 0 },
  { "name": "orc bass", "qty": 0 },
  { "name": "snaggletooth bass ", "qty": 0 },
  { "name": "tormented pike ", "qty": 0 },
  { "name": "darkfish ", "qty": 0 },
  { "name": "drake fish ", "qty": 0 },
]

###########  End  Setup Section    ###############

import time
import re

JOURNAL_ENTRY_DELAY = 0.2
SAY_DELAY = 1
DRAG_DELAY = 1.5

ENEMY_MAX_RANGE = 8
MAX_ROW_BOAT_TRAP_COUNT = 12
#MAX_GALLEON_TRAP_COUNT = 30
GALLEON_TRAP_STEP_COUNT = 2
MOVING_BOAT_DELAY = 1.5
FISH_STEAK_IDS = [ 0x097B, 0x097A ]
FISH_IDS = [ 0x09CF, 0x09CE, 0x09CC, 0x09CD ]
SHORE_FISH_IDS = [ 0x09CE, 0x09CC, 0x4306, 0x09CD, 0x44C6, 0x4303, 0x09CF, 0x4302, 0x44C4, 0x4307 ]
DEEP_SEA_FISH_IDS = [ 0x44C3, 0x4306, 0x44C4, 0x4302, 0x44C5, 0x4307, 0x4303, 0x44C6, 0x09CC, 0x09CD, 0x09CE ]
SHOE_IDS = [ 0x170F, 0x170D, 0x1711, 0x170C, 0x170E, 0x1712, 0x170B, 0x1710 ]
CRAB_IDS = [0x44D2, 0x44D1]
LOBSTER_IDS = [0x44D4, 0x44D3]
DISCARD_IDS = [ 0x44D1, 0x44D2, 0x44D4, 0x44D3 ]
PLAYER_BAG = API.Backpack
KNIFE_ID = 0x13F6
IN_BAG_FULL_TRAP_ID = 0x44D0
IN_BAG_EMPTY_TRAP_ID = 0x44CF
IN_WATER_TRAP_ID = 0x44CC
LOOTING_ITEM_IDS = [ 0x0DCA, 0x0EED, 0x14EE, 0x3196, 0x573A ] #0x14EB Map
LOOTING_SOS_IDS = [ 0xA30C ]
TIMER_TRAPS = "timerTraps"
FISH_TIMEOUT_TIMER = 1000 * 10
TRAP_COORDS = {
    0: [-2, 0],
    1: [-1, 3],
    2: [1, 3],
    3: [3, 3],
    4: [1, 1],
    5: [3, 1],
    6: [1, -1],
    7: [3, -1],
    8: [3, -3],
    9: [1, -3],
    10: [-1, -3],
    11: [-3, -3],
}

CRAB_LOBSTER_PATTERN = r'^(?:\d+\s)?(lobster|crab)$'
LOBSTER_PATTERN = r'^(?:\d+\s)?(lobster)$'
CRAB_PATTERN = r'^(?:\d+\s)?(crab)$'
RARE_BIG_FISH_PATTERN = r"^yellowtail barracuda|a big fish$"

lootedCorpseSerials = [  ]
lastTrapCount = 0


def debug(message):
    if isDebugging:
        API.SysMsg(f"{time.strftime('%d-%m %H:%M:%S')} - {message}")


def log(message):
    API.SysMsg(f"{time.strftime('%d-%m %H:%M:%S')} - {message}")


def findNpcByName(npcName):
    mobiles = API.GetAllMobiles()

    filtered_mobiles = [mobile for mobile in mobiles 
                   if not mobile.IsDestroyed
                   and mobile.Distance <= 15
                   and mobile.Name == npcName
                   and not API.OnIgnoreList(mobile.Serial)
                   ]
    
    return None if len(filtered_mobiles) == 0 else filtered_mobiles[0]


def reset():
    moveToTillerMan(True)
    API.ClearLeftHand()
    API.Pause(1)
    fishingPole = API.FindType(0x0DBF, API.Backpack)
    if fishingPole == None:
        API.HeadMsg('No fishing poles!!', API.Player)
        API.Stop()
    return fishingPole


def getTillerMan():
    tillerMan = None
    if tillerManSerial:
        tillerMan = API.FindItem(tillerManSerial)
    elif tillerManName:
        tillerMan = findNpcByName(tillerManName)
    return tillerMan


def moveToTillerMan(isMovingToFishingSpot):
    tillerMan = getTillerMan()
    if tillerMan is None:
        return
    tillerManPosition = (tillerMan.X, tillerMan.Y)
    playerStartX = API.Player.X
    playerStartY = API.Player.Y
    if playerStartX == tillerManPosition[0] and playerStartY == tillerManPosition[1]:
        if isMovingToFishingSpot:
            for walkingStep in toPositionWalkingSteps:
                API.Walk(walkingStep)
                API.Pause(0.15)
        return
    API.Pathfind(tillerMan)
    API.Pause(0.5)
    while API.Pathfinding:
        API.Pause(0.50)
    moveToTillerMan(isMovingToFishingSpot)


def recallFromRuneBook(runeBookSerial, runeIndex):
    Player = API.Player
    startX = Player.X
    startY = Player.Y
    API.UseObject(runeBookSerial)
    expireAt = time.time + 10
    while not API.HasGump(0x59) and time.time < expireAt:
        API.Pause(0.1)
    API.ReplyGump(49 + runeIndex, 0x59)
    API.Pause(4)
    endX = Player.X
    endY = Player.Y
    if startX == endX and startY == endY:
        recallFromRuneBook(runeBookSerial, runeIndex)


def dropLoot():
    recallFromRuneBook(runeBookSerial, runeIndex)
    backpack = API.Backpack
    for walkingStep in homeWalkingSteps:
        API.Walk(walkingStep)
        API.Pause(0.1)
    for lootingItemId in LOOTING_ITEM_IDS:
        while True:
            item = API.FindType(lootingItemId, backpack)
            if not item:
                break
            drag(item.Serial, otherContainerSerial)
    for lootingItemId in LOOTING_SOS_IDS:
        while True:
            item = API.FindType(lootingItemId, backpack)
            if not item:
                break
            drag(item.Serial, sosContainerSerial)
    API.Pause(1)
    if shipKeySerial:
        cast("Recall", shipKeySerial)
        API.Pause(4)
    if shipRuneIndex:
        recallFromRuneBook(runeBookSerial, shipRuneIndex)
    reset()


def loot():
    corpse = API.NearestCorpse(7)
    while corpse:
        if corpse.Serial in lootedCorpseSerials:
            continue
        API.UseObject(corpse.Serial)
        API.Pause(1)

        for item in API.ItemsInContainer(corpse):
            if item.Graphic in LOOTING_ITEM_IDS + LOOTING_SOS_IDS:
                drag(item.Serial, PLAYER_BAG)

        lootedCorpseSerials.append(corpse.Serial)
        API.IgnoreObject(corpse)
        corpse = API.NearestCorpse(7)


def drag(itemSerial, destination, amount = 0):
    API.MoveItem(itemSerial, destination, amount)
    API.Pause(DRAG_DELAY)


def findByNotorieties(notoriety):
    mobiles = API.GetAllMobiles()

    filtered_mobiles = [mobile for mobile in mobiles 
                if not mobile.IsDestroyed
                and mobile.Distance <= ENEMY_MAX_RANGE
                and not mobile.IsHuman
                and not mobile.IsGhost
                and mobile.NotorietyFlag in notoriety
                and not API.OnIgnoreList(mobile.Serial)
                ]
    
    return filtered_mobiles


def checkLoot():
    totalCount = 0
    for item in API.ItemsInContainer(PLAYER_BAG):
        if item.Graphic in LOOTING_ITEM_IDS + LOOTING_SOS_IDS and item.Graphic != 0x0EED:
            count = getItemCount(item)
            totalCount += count
    if totalCount >= itemBeforeDroppingCount:
        dropLoot()


def dropToCargoHoldOrBeetle():
    if cargoHoldSerial:
        discard()
        moveToTillerMan(False)
        cargoHold = API.FindItem(cargoHoldSerial)
        if not cargoHold:
            cutFishes()
        if cargoHold:
            API.UseObject(cargoHold)
            dragFish(cargoHold)
    if beetleSerial:
        discard()
        beetle = API.FindMobile(beetleSerial)
        if not beetle:
            cutFishes()
        if beetle:
            openBeetleBackpack()
            dragFish(beetle)
    reset()


def dragFish(containerSerial):
    for item in API.ItemsInContainer(PLAYER_BAG):
        if item.Graphic in FISH_IDS + DEEP_SEA_FISH_IDS + SHORE_FISH_IDS + CRAB_IDS + LOBSTER_IDS + FISH_STEAK_IDS:
            drag(item.Serial, containerSerial)


def cut(item):
    API.Pause(DRAG_DELAY)
    API.UseType(KNIFE_ID, container=PLAYER_BAG)
    API.WaitForTarget()
    API.Target(item)
    API.Pause(DRAG_DELAY)


def openBeetleBackpack():
    API.ContextMenu(beetleSerial, 1)
    API.Pause(1)


def cutFishes():
    container = None
    containerSerial = None
    if cargoHoldSerial:
        container = API.FindItem(cargoHoldSerial)
        containerSerial = container.Serial
    if beetleSerial:
        container = API.FindMobile(beetleSerial)
        containerSerial = container.Backpack.Serial
    allFishesKept = True
    for item in API.ItemsInContainer(PLAYER_BAG):
        isMatching = False
        if container:
            if cargoHoldSerial:
                API.UseObject(container)
            if beetleSerial:
                openBeetleBackpack()
            for toKeepFish in toKeepFishes:
                pattern = rf"^(?:\d+\s)?{toKeepFish['name']}$"
                cargoHoldCount = getCountFromContainerFromItemName(item, pattern, containerSerial)
                isMatching = isNameMatching(item, pattern)
                if isMatching:
                    amount = toKeepFish["qty"] - cargoHoldCount
                    if amount > 0:
                        log("Cargo has: {} - Dragging: {}  - For amount: {}".format(cargoHoldCount, getName(item), amount))
                        drag(item.Serial, containerSerial, amount)
                    leftItem = API.FindType(item.Graphic, PLAYER_BAG)
                    if leftItem:
                        cut(item)
                    break
            else:
                allFishesKept = False
        if not isMatching and item.Graphic in FISH_IDS + DEEP_SEA_FISH_IDS + SHORE_FISH_IDS:
            cut(item)
    if container:
        for item in API.ItemsInContainer(PLAYER_BAG):
            if item.Graphic in FISH_STEAK_IDS:
                drag(item.Serial, containerSerial)
    if allFishesKept and isFishing:
        log("All specified fish have been collected. Fishing may be unnecessary now.")


def checkWeight():
    Player = API.Player
    if Player.Weight < Player.WeightMax - 20:
        return
    if isKeepingAllFishes and cargoHoldSerial:
        dropToCargoHoldOrBeetle()
    if not isKeepingAllFishes:
        cutFishes()


def getMasterContainer(corpse):
    corpseItem = API.FindItem(corpse)
    if corpseItem.Container:
        return corpseItem.Container
    
    return corpse


def getName(item):
    API.ItemNameAndProps(item, True) #Ensure we have OPL name and props
    item = API.FindItem(item)
    return item.Name


def isNameMatching(item, pattern):
    try:
        name = getName(item)
        isMatching = bool(re.match(pattern, name))
        return isMatching
    except:
        log("Could not determine the name of : {}".format(item))
        return False


def discard():
    # Rare big fish, crabs and lobsters
    container = None
    if cargoHoldSerial:
        container = API.FindItem(cargoHoldSerial)
    if beetleSerial:
        container = API.FindMobile(beetleSerial)
    for item in API.ItemsInContainer(PLAYER_BAG):
        isMatchingBigFish = isNameMatching(item, RARE_BIG_FISH_PATTERN)
        if isMatchingBigFish:
              cut(item)
    if container:
        for item2 in API.ItemsInContainer(PLAYER_BAG):
            if item2 in FISH_STEAK_IDS:
                drag(item2.Serial, container)
        isMatchingCrab = isNameMatching(item, CRAB_LOBSTER_PATTERN)
        if isMatchingCrab:
            if container:
                drag(item.Serial, container)
    # Shoes
    corpse = API.NearestCorpse(2)
    if corpse:
        for item in API.ItemsInContainer(PLAYER_BAG):
            if item.Graphic in SHOE_IDS:
                drag(item.Serial, corpse.Serial)


def fish( fishingPole, x, y ):
    healSelf()
    discard()
    checkLoot()
    checkWeight()
    loot()
    checkTraps()
    if not isFishing:
        API.Pause(1)
        return True
    spFish = API.FindType(0x0DD6, PLAYER_BAG)
    if spFish:
        API.UseObject(spFish)
        API.Pause( DRAG_DELAY )
    API.Pause(1)
    log("Fishing!!!")
    API.ClearJournal()

    API.ClearRightHand()
    API.Pause(0.75)
    pole = API.FindType(0x0DBF, PLAYER_BAG)
    API.EquipItem(pole)
    API.UseObject(pole)
    API.WaitForTarget(timeout=2)

    static = API.GetTile( x, y )
    if static:
        API.Target( x, y, static.Z, static.Graphic )
    else:
        API.Target(x, y, -5)
    API.Pause( DRAG_DELAY )
    API.CancelTarget()

    expire = time.time + 10
    while not API.InJournalAny(['You pull',
                                 'You fish a while, but fail to catch anything',
                                 'Your fishing pole bends as you pull a big fish from the depths!',
                                 'Uh oh! That doesn\'t look like a fish!',
                                 "The fish don\'t seem to be biting here",
                                 'You need to be closer to the water to fish!']):
        log("Fishing Cooldown!")

        if(time.time > expire):
            return False
        
        enemy = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal])
        if enemy:
            fightEnemy()
        API.Pause( 1 )
    return True


def cast(spell, target):
    API.ClearJournal()
    expire = time.time + 3
    API.CastSpell(spell)
    while time.time < expire:
        if API.InJournal("fizzles"):
            cast(spell, target)
    API.WaitForTarget(timeout=3)
    API.Target(target)
    API.Pause( 0.5 )


def castSelf(spell):
    cast(spell, API.Player)


def healSelf():
    Player = API.Player
    while API.BuffExists("Poisoned"):
        castSelf("Cure")
        API.Pause(3)
    while Player.Hits < Player.HitsMax - 10:
        castSelf("Heal")
        API.Pause(3)


def fightEnemy():
    Player = API.Player
    healSelf()
    enemy = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal])
    if not enemy:
        return
    tactics = API.GetSkill('Tactics')
    magery = API.GetSkill('Magery')        

    if tactics and tactics.Value >= 60:
        expire = time.time + 60
        API.Attack(enemy)
        while not enemy.IsDead and not enemy.IsDestroyed:
            enemy = enemy.serial
            API.Pause( 0.2 )
            if time.time > expire:
                for i in range( 0, 3 ):
                    API.Msg( 0, 'back one' )
                    API.Pause( 0.4 )
                break
    elif magery and magery.Value > 70:
        while not enemy.IsDead and not enemy.IsDestroyed:
            if not API.BuffsExists("Protection"):
                castSelf("Protection")
            if Player.Hits < 50:
                healSelf()
            cast("Energy Bolt", enemy)


def useFishing():
    fishingPole = reset()
    Player = API.Player
    while True:
        x = Player.X - 3
        y = Player.Y - 3
        while fish( fishingPole, x, y ):
            fightEnemy()
            API.Pause(0.5)
        x = Player.X + 3
        y = Player.Y - 3
        while fish( fishingPole, x, y ):
            fightEnemy()
            API.Pause(0.5)
        x = Player.X + 3
        y = Player.Y + 3
        while fish( fishingPole, x, y ):
            fightEnemy()
            API.Pause(0.5)
        x = Player.X - 3
        y = Player.Y + 3
        while fish( fishingPole, x, y ):
            fightEnemy()
            API.Pause(0.5)
        API.Pause( 0.320 )
        pickupTraps()
        for i in range( 0, 12 ):
            API.Msg('Forward one')
            API.Pause( MOVING_BOAT_DELAY )
        API.Pause( 320 + JOURNAL_ENTRY_DELAY )
        if API.InJournal( 'Ar, we\'ve stopped sir.' ):
            API.ClearJournal()


def getItemCount(item):
    count = 0
    props = API.ItemNameAndProps(item, True)
    try:
        name = props.split("\n")[0]
        c = name.partition(' ')[0]
        count += int(c)
    except:
        count += 1
    return count


def getTraps():
    traps = []
    maxR = 4
    if isUsingGalleon:
        maxR = 2
    items = API.FindTypeAll(IN_WATER_TRAP_ID, range=maxR)
    for item in items:
        traps.append(item)
    return traps

    item


def checkOriginalPosition(startX, startY):
    Player = API.Player
    while (Player.X != startX and (Player.X - startX) * (0 if Player.X == startX else 1) < 0) or \
            (Player.Y != startY and (Player.Y - startY) * (0 if Player.Y == startY else 1) < 0):
        API.Pause(0.1)
    return


def pickupTraps():
    if not isUsingTraps:
        return
    global lastTrapCount
    cutFishes()
    discard()
    if not isUsingGalleon:
        traps = getTraps()
        for trap in traps:
            API.UseObject(trap)
            API.Pause(1000)
    if isUsingGalleon:
        Player = API.Player
        startX = Player.X
        startY = Player.Y
        for i in range(lastTrapCount):
            traps = getTraps()
            for trap in traps:
                API.UseObject(trap)
                API.Pause(1000)
            for j in range(GALLEON_TRAP_STEP_COUNT):
                API.Msg('Forward one')
                API.Pause(MOVING_BOAT_DELAY)
        API.Msg('slow back')
        checkOriginalPosition(startX, startY)
        API.Msg('stop')
    API.Pause(1000)
    openTraps()


def openTraps():
    for item in API.ItemsInContainer(PLAYER_BAG):
        if item.Graphic == IN_BAG_FULL_TRAP_ID:
            API.UseObject(item)
            API.Pause(1000)
    dropToCargoHoldOrBeetle()


def checkTraps():
    return #Disabled, moved stuff away from timers, you'll need to reimplement if desired still
    if not isUsingTraps:
        return
    remainingTime = Timer.Remaining(TIMER_TRAPS)
    isRemaining = Timer.Check(TIMER_TRAPS)
    debug("isRemaining : {} - time : {}".format(isRemaining, remainingTime))
    if isRemaining and remainingTime > 0:
        log("Remaining time before picking up the traps: {}".format(round(remainingTime / 1000)))
    else:
        pickupTraps()
        layoutTraps()


def layoutTraps():
    global lastTrapCount
    Player = API.Player
    trapCount = getCountFromContainerFromItemId(IN_BAG_EMPTY_TRAP_ID, PLAYER_BAG.Serial)
    minCount = 0
    if not isUsingGalleon:
        minCount = min(maxTrapCount, trapCount, MAX_ROW_BOAT_TRAP_COUNT)
    if isUsingGalleon:
        getTrapsFromHold(getCountFromContainerFromItemId(IN_BAG_EMPTY_TRAP_ID, PLAYER_BAG.Serial))
        trapCount = getCountFromContainerFromItemId(IN_BAG_EMPTY_TRAP_ID, PLAYER_BAG.Serial)
        #minCount = min(maxTrapCount, trapCount, MAX_GALLEON_TRAP_COUNT)
        minCount = min(maxTrapCount, trapCount)
    r = range(minCount - 1)
    if r == 0:
        return
    if not isUsingGalleon:
        for i in r:
            trap = API.FindType(IN_BAG_EMPTY_TRAP_ID, PLAYER_BAG)
            API.UseObject(trap.Serial)
            API.WaitForTarget(timeout=1)
            API.Target(Player.X + TRAP_COORDS[i][0], Player.Y + TRAP_COORDS[i][1], -5)
            API.Pause(1000)
            #Timer.Create(TIMER_TRAPS, round(beforePickingTrapsTimer))
    if isUsingGalleon:
        startTime = time.time()
        startX = Player.X
        startY = Player.Y
        lastTrapCount = minCount
        for i in r:
            log("Step: {} of: {}".format(i, minCount))
            trap = API.FindType(IN_BAG_EMPTY_TRAP_ID, PLAYER_BAG)
            API.UseObject(trap.Serial)
            API.WaitForTarget(timeout=1)
            API.Target(Player.X + 2, Player.Y - 1 ,-5)
            API.Pause(500)
            for j in range(GALLEON_TRAP_STEP_COUNT):
                API.Msg( 'Forward one')
                API.Pause(MOVING_BOAT_DELAY)
            API.Pause(1000)
        API.Msg( 'slow back')
        checkOriginalPosition(startX, startY)
        API.Msg( 'stop')
        elapsedTimeMs = int((time.time() - startTime) * 1000)
        calculatedTimer = round(beforePickingTrapsTimer - elapsedTimeMs - 20)
        if calculatedTimer <= 0:
            calculatedTimer = 1000
        log("Timer: {}".format(calculatedTimer))
        #Timer.Create(TIMER_TRAPS, calculatedTimer)


def getCountFromContainerFromItemName(item, pattern, containerSerial):
    totalCount = 0
    items = API.FindTypeAll(item.Graphic, containerSerial)
    for item in items:
        isMatching = isNameMatching(item, pattern)
        if isMatching:
            count = getItemCount(item)
            totalCount += count
    return totalCount

def getCountFromContainerFromItemId(itemId, containerSerial):
    totalCount = 0
    items = API.FindTypeAll(itemId, containerSerial)
    for item in items:
        count = getItemCount(item)
        totalCount += count
    return totalCount


def getTrapsFromHold(trapCount):
    # trapToGetCount = min(maxTrapCount, MAX_GALLEON_TRAP_COUNT) - trapCount
    trapToGetCount = maxTrapCount - trapCount
    log("Trap to get from cargo hold: {}".format(trapToGetCount))
    if trapToGetCount <= 0:
        return
    cargoHold = API.FindItem(cargoHoldSerial)
    if cargoHold:
        API.UseObject(cargoHold)
        for item in API.ItemsInContainer(cargoHold):
            if item.Graphic == IN_BAG_EMPTY_TRAP_ID:
                drag(item.Serial, PLAYER_BAG, trapToGetCount)

useFishing()