import API
import re
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


def getSkill(skillName):
    skill = API.GetSkill(skillName)
    if not skill:
        raise Exception(f"{skillName} - API.GetSkill returned None.")
    return skill


def getContents(findTypeReturn):
    if not findTypeReturn:
        return {"items": None, "stones": None}
    props = API.ItemNameAndProps(findTypeReturn.Serial, True).split("\n")
    for prop in props:
        if "Contents" in prop:
            match = re.search(
                r"Contents:\s*(\d+)/\d+\s+Items,\s*(\d+)/\d+\s+Stones", prop
            )
            if match:
                result = {"items": float(match.group(1)), "stones": float(match.group(2))}
            else:
                result = {"items": None, "stones": None}
            return result


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
            stopCrafting("Missing resources")
        if not moveItem(
            getattr(resourceInChest, "Serial", resourceInChest),
            API.Backpack,
            resourceAmount - amountInBackpack,
        ):
            stopCrafting("Could not move resources")


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
            trashContents = getContents(trash)
            if trashContents["items"] is None:
                API.SysMsg("Trash barrel contents unknown; keeping crafted item.", 33)
                continue
            while trashContents["items"] == 125:
                API.Pause(1)
                trashContents = getContents(trash)
                if trashContents["items"] is None:
                    API.SysMsg("Trash barrel contents unknown; keeping crafted item.", 33)
                    break
            if trashContents["items"] == 125 or trashContents["items"] is None:
                continue
            moveItem(i.Serial, trash.Serial)
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
