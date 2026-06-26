try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass
# API is injected by TazUO at runtime; the import above is IDE-only.
import os
import re
import time
from collections import OrderedDict

craftingSkills = OrderedDict(
    [
        (
            "Tinkering",
            {
                "tool": {"id": 0x1EB9, "buttonId": 11},
                "resource": {"amount": 500, "minAmount": 4},
                "disposeMethod": "Trash",
                "items": sorted(
                    [
                        {
                            "skill": 45.0,
                            "name": "Scissors",
                            "id": 0x0F9E,
                            "buttonId": 8,
                            "resourceAmount": 2,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 60.0,
                            "name": "Tongs",
                            "id": 0x0FBC,
                            "buttonId": 20,
                            "resourceAmount": 1,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 75.0,
                            "name": "Lockpicks",
                            "id": 0x1515,
                            "buttonId": 25,
                            "resourceAmount": 1,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 85.0,
                            "name": "Bracelet",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 3,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 90.0,
                            "name": "Spyglasses",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 4,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 100.0,
                            "name": "Rings",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 3,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                    ],
                    key=lambda x: x["skill"],
                ),
            },
        ),
        (
            "Tailoring",
            {
                "tool": {"id": 0x0F9D, "buttonId": 14},
                "resource": {"amount": 100, "minAmount": 16},
                "disposeMethod": "Salvage Bag",
                "items": sorted(
                    [
                        {
                            "skill": 35.0,
                            "name": "Short pants",
                            "id": 0x152E,
                            "buttonId": 37,
                            "resourceAmount": 6,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 41.4,
                            "name": "Fur cape",
                            "id": 0x1515,
                            "buttonId": 25,
                            "resourceAmount": 13,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 50.0,
                            "name": "Cloaks",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 14,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 54.0,
                            "name": "Fur boots",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 12,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 65.0,
                            "name": "Robes",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 16,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 72.0,
                            "name": "Kasa",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 10,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 78.0,
                            "name": "Ninja tabi",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 10,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 110,
                            "name": "Oil cloth",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 1,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 115,
                            "name": "Elven shirt",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 10,
                            "resourceId": 0x1766,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 120.0,
                            "name": "Studded hiro sode",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 8,
                            "resourceId": 0x1081,
                            "resourceHue": 0x0000,
                        },
                    ],
                    key=lambda x: x["skill"],
                ),
            },
        ),
        (
            "Blacksmithy",
            {
                "tool": {"id": 0x13E3, "buttonId": 21},
                "resource": {"amount": 500, "minAmount": 25},
                "disposeMethod": "Salvage Bag",
                "items": sorted(
                    [
                        {
                            "skill": 45.0,
                            "name": "Mace",
                            "id": 0x152E,
                            "buttonId": 37,
                            "resourceAmount": 6,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 50.0,
                            "name": "Maul",
                            "id": 0x1515,
                            "buttonId": 25,
                            "resourceAmount": 1,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 55.0,
                            "name": "Cutlass",
                            "id": 0x1515,
                            "buttonId": 25,
                            "resourceAmount": 8,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 59.5,
                            "name": "Katana",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 8,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 70.5,
                            "name": "Scimitar",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 10,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 106.4,
                            "name": "Platemail gorget",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 10,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 108.9,
                            "name": "Platemail gloves",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 12,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 116.3,
                            "name": "Platemail arms",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 18,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 118.8,
                            "name": "Platemail legs",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 20,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 120.0,
                            "name": "Platemail tunics",
                            "id": 0x1F03,
                            "buttonId": 26,
                            "resourceAmount": 25,
                            "resourceId": 0x1BF2,
                            "resourceHue": 0x0000,
                        },
                    ],
                    key=lambda x: x["skill"],
                ),
            },
        ),
        (
            "Bowcraft/Fletching",
            {
                "tool": {"id": 0x1022, "buttonId": 28},
                "resource": {"amount": 200, "minAmount": 1},
                "disposeMethod": "Trash",
                "items": sorted(
                    [
                        {
                            "skill": 35.0,
                            "name": "Shafts",
                            "id": 0x1BD4,
                            "buttonId": 2,
                            "resourceAmount": 1,
                            "resourceId": 0x1BD7,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 55.0,
                            "name": "Bows",
                            "id": 0x13B2,
                            "buttonId": 6,
                            "resourceAmount": 7,
                            "resourceId": 0x1BD7,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 60.0,
                            "name": "Fukiya Darts",
                            "id": 0x2806,
                            "buttonId": 5,
                            "resourceAmount": 1,
                            "resourceId": 0x1BD7,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 70.0,
                            "name": "Crossbows",
                            "id": 0x0F4F,
                            "buttonId": 7,
                            "resourceAmount": 7,
                            "resourceId": 0x1BD7,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 80.0,
                            "name": "Composite Bows",
                            "id": 0x26C2,
                            "buttonId": 9,
                            "resourceAmount": 7,
                            "resourceId": 0x1BD7,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 90.0,
                            "name": "Heavy Crossbows",
                            "id": 0x13FD,
                            "buttonId": 8,
                            "resourceAmount": 10,
                            "resourceId": 0x1BD7,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 100.0,
                            "name": "Repeating Crossbows",
                            "id": 0x26C3,
                            "buttonId": 10,
                            "resourceAmount": 10,
                            "resourceId": 0x1BD7,
                            "resourceHue": 0x0000,
                        },
                    ],
                    key=lambda x: x["skill"],
                ),
            },
        ),
        (
            "Cartography",
            {
                "tool": {"id": 0x0FC0, "buttonId": 29},
                "resource": {"amount": 100, "minAmount": 4},
                "disposeMethod": "Trash",
                "items": sorted(
                    [
                        {
                            "skill": 50.0,
                            "name": "Local map",
                            "id": 0x14EB,
                            "buttonId": 1,
                            "resourceAmount": 1,
                            "resourceId": 0x0EF3,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 65.0,
                            "name": "City map",
                            "id": 0x14EB,
                            "buttonId": 2,
                            "resourceAmount": 1,
                            "resourceId": 0x0EF3,
                            "resourceHue": 0x0000,
                        },
                        {
                            "skill": 99.5,
                            "name": "World map",
                            "id": 0x14EB,
                            "buttonId": 4,
                            "resourceAmount": 1,
                            "resourceId": 0x0EF3,
                            "resourceHue": 0x0000,
                        },
                    ],
                    key=lambda x: x["skill"],
                ),
            },
        ),
    ]
)

skillNameLabels = []
skillNumberLabels = []
itemLabel = None
statusLabel = None
TOOL_BUFFER_COUNT = 3
TINKER_TOOL_IDS = [0x1EB9, 0x1EB8]

try:
    CRAFTER_DEBUG_LOG = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Crafter.debug.log",
    )
except Exception:
    CRAFTER_DEBUG_LOG = "Crafter.debug.log"


def _debugHex(value):
    try:
        return hex(int(value))
    except Exception:
        return str(value)


def _debugSerial(value):
    return _debugHex(getattr(value, "Serial", value))


def _debugItemSummary(item):
    if not item:
        return "None"

    serial = _debugSerial(item)
    graphic = _debugHex(getattr(item, "Graphic", None))
    hue = _debugHex(getattr(item, "Hue", None))
    amount = getattr(item, "Amount", None)
    container = _debugHex(getattr(item, "Container", None))
    return (
        f"serial={serial} graphic={graphic} hue={hue} "
        f"amount={amount} container={container}"
    )


def debugLog(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(CRAFTER_DEBUG_LOG, "a") as logFile:
            logFile.write(f"{stamp} {message}\n")
    except Exception:
        pass


def _debugNotifyLogPath():
    try:
        API.SysMsg(f"Crafter debug log: {CRAFTER_DEBUG_LOG}", 48)
    except Exception:
        pass


def _debugContainerContents(container):
    try:
        return API.Contents(getattr(container, "Serial", container))
    except Exception as e:
        return f"error={e}"


def _debugMatchingItems(label, resourceId, container, resourceHue):
    containerSerial = getattr(container, "Serial", container)
    debugLog(
        f"{label} container={_debugSerial(containerSerial)} "
        f"contents={_debugContainerContents(containerSerial)}"
    )

    for mode, hue in [("hue-match", resourceHue), ("any-hue", None)]:
        try:
            if hue is None:
                items = API.FindTypeAll(resourceId, containerSerial) or []
            else:
                items = API.FindTypeAll(resourceId, containerSerial, hue=hue) or []
            summaries = [_debugItemSummary(item) for item in items[:10]]
            debugLog(
                f"{label} {mode} findTypeAll count={len(items)} "
                f"items={summaries}"
            )
        except Exception as e:
            debugLog(f"{label} {mode} findTypeAll error={e}")

    try:
        items = API.ItemsInContainer(containerSerial, True) or []
        matches = [
            item
            for item in items
            if getattr(item, "Graphic", None) == resourceId
        ]
        summaries = [_debugItemSummary(item) for item in matches[:10]]
        debugLog(
            f"{label} recursive graphic-match count={len(matches)} "
            f"items={summaries}"
        )
    except Exception as e:
        debugLog(f"{label} recursive graphic-match error={e}")


def _debugResourceSnapshot(reason, item, resourceId, resourceHue):
    debugLog(
        f"resource snapshot reason={reason} item={item.get('name')} "
        f"resourceId={_debugHex(resourceId)} resourceHue={_debugHex(resourceHue)} "
        f"backpack={_debugSerial(API.Backpack)} chest={_debugSerial(resourceChestSerial)}"
    )
    _debugMatchingItems("backpack", resourceId, API.Backpack, resourceHue)
    _debugMatchingItems("resourceChest", resourceId, resourceChestSerial, resourceHue)


def findResource(resourceId, container, resourceHue, minamount=0):
    if resourceHue is None:
        return API.FindType(resourceId, container, minamount=minamount)
    return API.FindType(resourceId, container, hue=resourceHue, minamount=minamount)


def getSkill(skillName):
    skill = API.GetSkill(skillName)
    if not skill:
        raise Exception(f"{skillName} - API.GetSkill returned None.")
    return skill


def getContents(findTypeReturn):
    if not findTypeReturn:
        return {"items": None, "itemMax": None, "stones": None, "stoneMax": None}
    props = API.ItemNameAndProps(findTypeReturn.Serial, True).split("\n")
    for prop in props:
        if "Contents" in prop:
            match = re.search(
                r"Content[s]?:\s*(\d+)(?:/(\d+))?\s+Items,\s*(\d+)(?:/(\d+))?\s+Stones",
                prop,
            )
            if match:
                result = {
                    "items": float(match.group(1)),
                    "itemMax": float(match.group(2)) if match.group(2) else None,
                    "stones": float(match.group(3)),
                    "stoneMax": float(match.group(4)) if match.group(4) else None,
                }
            else:
                result = {
                    "items": None,
                    "itemMax": None,
                    "stones": None,
                    "stoneMax": None,
                }
            return result
    return {"items": None, "itemMax": None, "stones": None, "stoneMax": None}


def _containerFullByContents(contents):
    items = contents.get("items")
    itemMax = contents.get("itemMax")
    stones = contents.get("stones")
    stoneMax = contents.get("stoneMax")

    if items is not None and itemMax is not None and items >= itemMax:
        return True
    if stones is not None and stoneMax is not None and stones >= stoneMax:
        return True
    if items is not None and itemMax is None and items >= 125:
        return True
    return False


def _contentsText(contents):
    return (
        f"items={contents.get('items')}/{contents.get('itemMax')} "
        f"stones={contents.get('stones')}/{contents.get('stoneMax')}"
    )


def _waitForTrashBarrelSpace(trash):
    lastNotice = 0
    while True:
        trashContents = getContents(trash)
        if trashContents["items"] is None and trashContents["stones"] is None:
            debugLog("trash barrel contents unknown; attempting disposal anyway")
            return True
        if not _containerFullByContents(trashContents):
            debugLog(f"trash barrel has space {_contentsText(trashContents)}")
            return True

        now = time.time()
        if now - lastNotice >= 10:
            message = f"Trash barrel full; waiting. {_contentsText(trashContents)}"
            API.SysMsg(message, 33)
            debugLog(message)
            lastNotice = now
        API.Pause(2)


def _trashMoveBlockedByCapacity():
    messages = [
        "That container cannot hold more weight",
        "container cannot hold more weight",
        "That container is full",
        "container is full",
    ]
    try:
        return API.InJournalAny(messages, True)
    except Exception:
        for message in messages:
            try:
                if API.InJournal(message, True):
                    return True
            except Exception:
                pass
    return False


def _contentsDecreased(currentContents, previousContents):
    for key in ["items", "stones"]:
        current = currentContents.get(key)
        previous = previousContents.get(key)
        if current is not None and previous is not None and current < previous:
            return True
    return False


def _waitForTrashBarrelEmptied(trash, blockedContents, reason):
    lastNotice = 0
    while True:
        currentContents = getContents(trash)
        if _contentsDecreased(currentContents, blockedContents):
            debugLog(
                f"trash barrel changed after {reason}; "
                f"before={_contentsText(blockedContents)} "
                f"after={_contentsText(currentContents)}"
            )
            return True

        now = time.time()
        if now - lastNotice >= 10:
            message = (
                f"Trash barrel blocked by {reason}; waiting for it to empty. "
                f"{_contentsText(currentContents)}"
            )
            API.SysMsg(message, 33)
            debugLog(message)
            lastNotice = now
        API.Pause(2)


def _itemInBackpack(serial):
    try:
        item = API.FindItem(serial)
        return bool(item and getattr(item, "Container", None) == API.Backpack)
    except Exception as e:
        debugLog(f"item lookup failed after trash move serial={_debugHex(serial)} error={e}")
        return False


def _disposeTrashItem(item, trash):
    attempts = 0
    itemSerial = getattr(item, "Serial", item)
    while True:
        _waitForTrashBarrelSpace(trash)
        debugLog(f"trash dispose attempt item={_debugItemSummary(item)}")
        moved = moveItem(itemSerial, trash.Serial)
        API.Pause(0.5)
        if moved and not _itemInBackpack(itemSerial):
            debugLog(f"trash dispose succeeded item={_debugHex(itemSerial)}")
            return True

        trashContents = getContents(trash)
        blockedByCapacity = _trashMoveBlockedByCapacity()
        if blockedByCapacity or _containerFullByContents(trashContents):
            debugLog(
                f"trash dispose blocked by capacity moved={moved} "
                f"contents={_contentsText(trashContents)}"
            )
            _waitForTrashBarrelEmptied(trash, trashContents, "capacity")
            attempts = 0
            continue

        attempts += 1
        debugLog(
            f"trash dispose failed attempt={attempts} moved={moved} "
            f"contents={_contentsText(trashContents)}"
        )
        if attempts >= 5:
            stopCrafting("Could not move crafted item to trash barrel.")
            return False
        API.Pause(1)


def openContainer(container):
    serial = getattr(container, "Serial", container)
    isOpened = getattr(container, "Opened", False)
    if not isOpened:
        API.UseObject(serial)
        API.Pause(1)



def moveItem(item_serial, destination_serial, amount=0, max_retries=5):
    for attempt in range(max_retries):
        API.ClearJournal()
        API.MoveItem(item_serial, destination_serial, amount)
        API.Pause(1)

        if not API.InJournal("You must wait to perform another action."):
            return True

        API.SysMsg(f"Retrying move ({attempt + 1}/{max_retries})...", 33)
        API.Pause(1)

    API.SysMsg("Move failed after retries.", 33)
    return False


def stopCrafting(message, hue=33):
    debugLog(f"stopCrafting message={message} hue={hue}")
    if statusLabel:
        statusLabel.Text = message
        statusLabel.Hue = hue
    API.SysMsg(message, hue)
    API.Stop()
    raise Exception(message)


def closeCraftGump():
    for _ in range(10):
        if not API.HasGump(460):
            return True
        API.CloseGump(460)
        API.Pause(0.25)
    return not API.HasGump(460)


def toolWornOut(timeout=2):
    checks = max(1, int(timeout / 0.25))
    for _ in range(checks):
        if (
            API.InJournal("You have worn out your tool", True)
            or API.InJournal("You have worn out", True)
            or API.InJournal("worn out your tool", True)
            or API.InJournal("worn out", True)
        ):
            return True
        API.Pause(0.25)
    return False


def checkResource(item, craftingSkill):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    resourceId = item["resourceId"]
    resourceHue = item["resourceHue"]
    resourceMinAmount = craftingSkill["resource"]["minAmount"]
    resourceAmount = craftingSkill["resource"]["amount"]
    requiredAmount = max(resourceMinAmount, item.get("resourceAmount", resourceMinAmount))
    debugLog(
        f"checkResource start item={item.get('name')} "
        f"itemButton={item.get('buttonId')} resourceId={_debugHex(resourceId)} "
        f"resourceHue={_debugHex(resourceHue)} min={resourceMinAmount} "
        f"itemResourceAmount={item.get('resourceAmount')} required={requiredAmount} "
        f"batch={resourceAmount} backpack={_debugSerial(API.Backpack)} "
        f"chest={_debugSerial(resourceChestSerial)}"
    )

    resourceInBackpack = findResource(
        resourceId, API.Backpack, resourceHue, requiredAmount
    )
    if not resourceInBackpack:
        resourceInBackpack = findResource(resourceId, API.Backpack, resourceHue)
    amountInBackpack = 0
    if resourceInBackpack:
        amountInBackpack = resourceInBackpack.Amount
    debugLog(
        f"checkResource backpack selected={_debugItemSummary(resourceInBackpack)} "
        f"amountInBackpack={amountInBackpack}"
    )

    if amountInBackpack >= requiredAmount:
        debugLog("checkResource enough resources already in backpack")
        return

    amountNeeded = requiredAmount - amountInBackpack
    debugLog(f"checkResource chest lookup amountNeeded={amountNeeded}")
    resourceInChest = findResource(
        resourceId, resourceChestSerial, resourceHue, amountNeeded
    )
    if not resourceInChest:
        debugLog("checkResource missing: no matching stack in resource chest")
        _debugResourceSnapshot("no chest stack", item, resourceId, resourceHue)
        _debugNotifyLogPath()
        stopCrafting("Missing resources")
    debugLog(f"checkResource chest selected={_debugItemSummary(resourceInChest)}")
    amountAvailable = getattr(resourceInChest, "Amount", resourceAmount)
    amountToMove = min(resourceAmount - amountInBackpack, amountAvailable)
    debugLog(
        f"checkResource move decision amountAvailable={amountAvailable} "
        f"amountToMove={amountToMove} amountNeeded={amountNeeded}"
    )
    if amountToMove < amountNeeded:
        debugLog("checkResource missing: matching stack amount below required amount")
        _debugResourceSnapshot("stack below required", item, resourceId, resourceHue)
        _debugNotifyLogPath()
        stopCrafting("Missing resources")
    if not moveItem(
        getattr(resourceInChest, "Serial", resourceInChest),
        API.Backpack,
        amountToMove,
    ):
        debugLog("checkResource moveItem failed")
        _debugResourceSnapshot("move failed", item, resourceId, resourceHue)
        _debugNotifyLogPath()
        stopCrafting("Could not move resources")
    API.Pause(0.5)
    resourceInBackpack = findResource(
        resourceId, API.Backpack, resourceHue, requiredAmount
    )
    if not resourceInBackpack:
        debugLog("checkResource move verification failed")
        _debugResourceSnapshot("move verification failed", item, resourceId, resourceHue)
        _debugNotifyLogPath()
        stopCrafting("Could not move resources")
    debugLog("checkResource moveItem succeeded")


def checkToolsResource():
    openContainer(API.Backpack)
    openContainer(resourceChest)
    resourceId = 0x1BF2
    resourceHue = 0x0000
    resourceMinAmount = 20
    resourceAmount = 50
    resourceInBackpack = API.FindType(
        resourceId, API.Backpack, hue=resourceHue, minamount=resourceMinAmount
    )
    if not resourceInBackpack:
        resourceInBackpack = API.FindType(resourceId, API.Backpack, hue=resourceHue)
        amountInBackpack = 0
        if resourceInBackpack:
            amountInBackpack = resourceInBackpack.Amount
        resourceInChest = API.FindType(
            resourceId, resourceChestSerial, hue=resourceHue, minamount=resourceAmount
        )
        if not resourceInChest:
            stopCrafting("Missing tool resources")
        if not moveItem(
            getattr(resourceInChest, "Serial", resourceInChest),
            API.Backpack,
            resourceAmount - amountInBackpack,
        ):
            stopCrafting("Could not move tool resources")


def craft(item, craftingSkill):
    itemButtonId = item["buttonId"]
    checkTools(craftingSkill)
    useTool(craftingSkill)
    if not API.ReplyGump(itemButtonId, 460):
        stopCrafting("Could not select crafting item.")
    API.Pause(3)
    return not toolWornOut(1)


def craftWithRecovery(item, craftingSkill, maxAttempts=5):
    for _ in range(maxAttempts):
        if craft(item, craftingSkill):
            return True
        recoverWornTool(craftingSkill)
    stopCrafting("Could not craft after replacing worn tools.")


def _toolIds(craftingSkill):
    tool = craftingSkill["tool"]
    ids = tool.get("ids") or tool.get("graphics")
    if ids:
        return ids
    toolId = tool.get("id", tool.get("graphic"))
    if toolId in (0x1EB8, 0x1EB9):
        return TINKER_TOOL_IDS
    return [toolId]


def _itemsInBackpack():
    try:
        return API.ItemsInContainer(API.Backpack, True) or []
    except Exception:
        try:
            return API.ItemsInContainer(API.Backpack) or []
        except Exception:
            return []


def findTool(toolIds):
    if not isinstance(toolIds, list):
        toolIds = [toolIds]

    for toolId in toolIds:
        tool = API.FindType(toolId, API.Backpack)
        if tool:
            return tool

    for item in _itemsInBackpack():
        if getattr(item, "Graphic", None) in toolIds:
            return item

    return None


def toolCount(toolIds):
    if not isinstance(toolIds, list):
        toolIds = [toolIds]

    count = 0
    seen = set()
    for toolId in toolIds:
        for item in API.FindTypeAll(toolId, API.Backpack) or []:
            serial = getattr(item, "Serial", None)
            if serial not in seen:
                seen.add(serial)
                count += 1

    for item in _itemsInBackpack():
        serial = getattr(item, "Serial", None)
        if serial not in seen and getattr(item, "Graphic", None) in toolIds:
            seen.add(serial)
            count += 1

    return count


def _sameToolIds(left, right):
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]
    return set(left) == set(right)


def craftTool(toolIds, toolButtonId, expectedToolCount=None):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    if not isinstance(toolIds, list):
        toolIds = [toolIds]
    if expectedToolCount is None:
        expectedToolCount = toolCount(toolIds) + 1

    tool = findTool(TINKER_TOOL_IDS)
    if not tool:
        stopCrafting("No tinker tool found!", 32)
    if not closeCraftGump():
        stopCrafting("Could not close old crafting gump.")
    API.UseObject(getattr(tool, "Serial", tool))
    if not API.WaitForGump(460, 3):
        stopCrafting("Could not open tinker gump.")
    if not API.ReplyGump(toolButtonId, 460):
        return False
    API.Pause(3)
    toolWornOut(0.25)
    hasExpectedToolCount = toolCount(toolIds) >= expectedToolCount
    if not closeCraftGump():
        stopCrafting("Could not close tinker gump.")
    return hasExpectedToolCount


def ensureToolBuffer(toolIds, toolButtonId, label, requiresExistingTool=False):
    tools = toolCount(toolIds)
    if tools >= TOOL_BUFFER_COUNT:
        return False
    if requiresExistingTool and tools <= 0:
        stopCrafting(f"No {label} tool found!", 32)

    checkToolsResource()

    attempts = 0
    maxAttempts = TOOL_BUFFER_COUNT * 4
    madeTools = False
    while tools < TOOL_BUFFER_COUNT and attempts < maxAttempts:
        attempts += 1
        previousTools = toolCount(toolIds)
        if requiresExistingTool and previousTools <= 0:
            stopCrafting(f"No {label} tool found!", 32)

        craftTool(toolIds, toolButtonId, previousTools + 1)
        madeTools = True
        currentTools = toolCount(toolIds)
        if currentTools > tools:
            tools = currentTools
            continue
        if requiresExistingTool and currentTools <= 0:
            stopCrafting(f"No {label} tool found!", 32)

        tools = currentTools
        API.Pause(0.5)

    if tools < TOOL_BUFFER_COUNT:
        stopCrafting(f"Could not top up {label} tools to {TOOL_BUFFER_COUNT}.")
    return madeTools


def checkTools(craftingSkill):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    toolIds = _toolIds(craftingSkill)
    toolButtonId = craftingSkill["tool"]["buttonId"]

    restocked = ensureToolBuffer(TINKER_TOOL_IDS, 11, "tinker", True)
    if not _sameToolIds(toolIds, TINKER_TOOL_IDS):
        restocked = ensureToolBuffer(toolIds, toolButtonId, "crafting") or restocked
    return restocked


def useTool(craftingSkill):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    tool = findTool(_toolIds(craftingSkill))
    if not tool:
        stopCrafting("No tool found!", 32)
    if not closeCraftGump():
        stopCrafting("Could not close old crafting gump.")
    API.UseObject(getattr(tool, "Serial", tool))
    if not API.WaitForGump(460, 3):
        stopCrafting("Could not open crafting gump.")


def recoverWornTool(craftingSkill):
    checkTools(craftingSkill)
    useTool(craftingSkill)


def makeLast(item, craftingSkill, skillName, skillTarget):
    skillLevel = getSkill(skillName)
    itemSkillLevel = item["skill"]

    useTool(craftingSkill)

    while (
        skillLevel.Value < itemSkillLevel
        and skillLevel.Value < skillTarget
        and skillLevel.Value != skillLevel.Cap
    ):
        skillLevel = getSkill(skillName)
        checkResource(item, craftingSkill)
        if checkTools(craftingSkill):
            craftWithRecovery(item, craftingSkill)
            skillLevel = getSkill(skillName)
            updateGump(item, skillName)
            disposeItem(item, craftingSkill)
            continue
        if not API.HasGump(460):
            if toolWornOut(0.25):
                recoverWornTool(craftingSkill)
            else:
                useTool(craftingSkill)
        if not API.ReplyGump(1999, 460):
            if toolWornOut(1):
                recoverWornTool(craftingSkill)
            else:
                useTool(craftingSkill)
            continue
        if toolWornOut(1):
            recoverWornTool(craftingSkill)
            craftWithRecovery(item, craftingSkill)
            skillLevel = getSkill(skillName)
            updateGump(item, skillName)
            disposeItem(item, craftingSkill)
            continue
        API.Pause(0.5)
        updateGump(item, skillName)
        disposeItem(item, craftingSkill)


def disposeItem(item, craftingSkill):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    itemId = item["id"]
    method = craftingSkill["disposeMethod"]
    items = API.FindTypeAll(itemId, API.Backpack)
    for i in items:
        if method == "Trash":
            trash = API.FindType(0x0E77, 4294967295, 2)
            if not trash:
                API.SysMsg("Trash barrel not found; keeping crafted item.", 33)
                continue
            _disposeTrashItem(i, trash)
        if method == "Salvage Bag":
            salvageBag = API.FindType(0x0E76, API.Backpack, hue=0x024E)
            if not salvageBag:
                API.SysMsg("Salvage bag not found; keeping crafted item.", 33)
                continue
            moveItem(i.Serial, salvageBag.Serial)
            contents = API.Contents(salvageBag.Serial)
            if len(contents) > 10:
                API.SysMsg("Salvage now!!!")


def updateGump(item, skillName):
    itemName = item["name"]
    for i, cs in enumerate(craftingSkills):
        if cs == skillName:
            skillLabelIndex = i
    skillNumberLabels[skillLabelIndex].Text = truncateDecimal(
        getSkill(skillName).Value, 1
    )
    skillNumberLabels[skillLabelIndex].Hue = 88
    skillNameLabels[skillLabelIndex].Hue = 88
    itemLabel.Text = itemName


def makeFirst(item, skillName, skillTarget=None):
    craftingSkill = craftingSkills[skillName]
    targetSkill = item["skill"]
    if skillTarget is not None:
        targetSkill = min(float(targetSkill), float(skillTarget))
    debugLog(
        f"makeFirst skill={skillName} item={item.get('name')} "
        f"itemTarget={item.get('skill')} runTarget={skillTarget} "
        f"effectiveTarget={targetSkill}"
    )
    statusLabel.Text = "Crafting..."

    disposeItem(item, craftingSkill)
    checkResource(item, craftingSkill)
    checkTools(craftingSkill)

    craftWithRecovery(item, craftingSkill)
    updateGump(item, skillName)
    makeLast(item, craftingSkill, skillName, targetSkill)
    API.Pause(0.1)


def trainCraftingSkill(skillName, targetSkill):
    craftingSkill = craftingSkills[skillName]
    items = craftingSkill["items"]
    targetSkillValue = float(targetSkill)
    currentSkillLevel = getSkill(skillName).Value
    debugLog(
        "----- trainCraftingSkill start "
        f"skill={skillName} current={currentSkillLevel} target={targetSkillValue} "
        f"resourceChest={_debugSerial(resourceChestSerial)} "
        f"resourceChestObj={_debugItemSummary(resourceChest)}"
    )
    while float(currentSkillLevel) < targetSkillValue:
        currentItem = items[-1] if items else None
        for item in items:
            itemSkillLevel = item["skill"]
            if currentSkillLevel < itemSkillLevel:
                currentItem = item
                break
        if not currentItem:
            raise Exception(f"{skillName} - No crafting item configured.")
        makeFirst(currentItem, skillName, targetSkillValue)
        currentSkillLevel = getSkill(skillName).Value


def showCraftingGump():
    global statusLabel, itemLabel
    keys = list(craftingSkills.keys())
    height = 100 + 40 * len(keys)
    width = 320

    gump = API.CreateGump(True, True)
    gump.SetWidth(width)
    gump.SetHeight(height)
    gump.CenterXInViewPort()
    gump.CenterYInViewPort()

    def addBorder(x, y, w, h):
        b = API.CreateGumpColorBox(1, "#a86b32")
        b.SetX(x)
        b.SetY(y)
        b.SetWidth(w)
        b.SetHeight(h)
        gump.Add(b)

    addBorder(-5, -5, width, 5)  # Top
    addBorder(-5, height - 10, width, 5)  # Bottom
    addBorder(-5, -5, 5, height)  # Left
    addBorder(width - 10, -5, 5, height)  # Right

    bg = API.CreateGumpColorBox(0.75, "#000000")
    bg.SetWidth(width - 10)
    bg.SetHeight(height - 10)
    gump.Add(bg)

    mainLabel = API.CreateGumpLabel("Select Crafting Skills & Target:")
    mainLabel.SetX(10)
    mainLabel.SetY(10)
    gump.Add(mainLabel)

    skillInputs, y = [], 40
    for key in keys:
        skillNameLabel = API.CreateGumpLabel(key)
        skillNameLabel.SetX(10)
        skillNameLabel.SetY(y)
        gump.Add(skillNameLabel)
        skillNameLabels.append(skillNameLabel)

        textBox = API.CreateGumpTextBox("0", 60, 24, False)
        textBox.SetX(100)
        textBox.SetY(y)
        gump.Add(textBox)

        skillNumberLabel = API.CreateGumpLabel(
            truncateDecimal(getSkill(key).Value, 1)
        )
        skillNumberLabel.SetX(170)
        skillNumberLabel.SetY(y)
        gump.Add(skillNumberLabel)
        skillNumberLabels.append(skillNumberLabel)

        skillInputs.append((key, textBox))
        y += 40

    startBtn = API.CreateGumpButton("", 996, 9722, 9721, 9721)
    startBtn.SetX(10)
    startBtn.SetY(y)
    gump.Add(startBtn)

    statusLabel = API.CreateGumpLabel("Start")
    statusLabel.SetX(40)
    statusLabel.SetY(y)
    gump.Add(statusLabel)

    itemLabel = API.CreateGumpLabel("")
    itemLabel.SetX(170)
    itemLabel.SetY(y)
    gump.Add(itemLabel)

    API.AddGump(gump)

    while True:
        API.Pause(0.1)
        if startBtn.IsClicked:
            startBtn.SetWidth(0)
            startBtn.SetHeight(0)
            statusLabel.Text = "Running"
            statusLabel.Hue = 88

            tinkeringSkillLevel = getSkill("Tinkering").Value
            for key, box in skillInputs:
                try:
                    val = float(box.Text)
                    if val < 0 or val > getSkill(key).Cap:
                        msg = "Invalid inputs"
                        statusLabel.Text = msg
                        statusLabel.Hue = 33
                        return
                    if val and key == "Cartography" and val > 99.5:
                        msg = "Cartography should be <= 99.5"
                        statusLabel.Text = msg
                        statusLabel.Hue = 33
                        return
                    if key == "Tinkering" and val > tinkeringSkillLevel:
                        tinkeringSkillLevel = val
                except Exception as e:
                    API.SysMsg(str(e))
                    return

            if tinkeringSkillLevel < 50:
                statusLabel.Text = "Tinkering should be >= 50"
                statusLabel.Hue = 33
                return

            for key, box in skillInputs:
                try:
                    val = float(box.Text)
                    trainCraftingSkill(key, val)
                except:
                    continue

            statusLabel.Text = "Done"
            statusLabel.Hue = 68
            API.Stop()


if __name__ == "__main__":
    openContainer(API.Backpack)
    API.SysMsg("Target your resource chest", 48)
    resourceChestSerial = API.RequestTarget()
    resourceChest = API.FindItem(resourceChestSerial)
    openContainer(resourceChest)

    showCraftingGump()
