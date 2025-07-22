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


def getContents(findTypeReturn):
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
    isOpened = container.Opened
    if not isOpened:
        API.UseObject(container.Serial)
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
            statusLabel.Text = "Missing resources"
            statusLabel.Hue = 33
            API.Stop()
        moveItem(resourceInChest, API.Backpack, resourceAmount - amountInBackpack)


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
            statusLabel.Text = "Missing resources"
            statusLabel.Hue = 33
            API.Stop()
        moveItem(resourceInChest, API.Backpack, resourceAmount - amountInBackpack)


def craft(item, craftingSkill):
    itemButtonId = item["buttonId"]
    useTool(craftingSkill)
    API.ReplyGump(itemButtonId, 460)
    API.Pause(3)


def craftTool(toolId, toolButtonId):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    tool = API.FindType(toolId, API.Backpack)
    if not tool:
        statusLabel.Text = "No tool found!"
        statusLabel.Hue = 32
        API.Stop()
    API.UseObject(tool)
    API.Pause(1)
    API.ReplyGump(toolButtonId, 460)
    API.Pause(3)


def checkTools(craftingSkill):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    toolId = craftingSkill["tool"]["id"]
    toolButtonId = craftingSkill["tool"]["buttonId"]

    checkToolsResource()

    tinkerTools = len(API.FindTypeAll(0x1EB9, API.Backpack))
    while tinkerTools < 3:
        craftTool(0x1EB9, 11)
        tinkerTools = len(API.FindTypeAll(0x1EB9, API.Backpack))

    tools = len(API.FindTypeAll(toolId, API.Backpack))
    while tools < 3:
        craftTool(0x1EB9, toolButtonId)
        tools = len(API.FindTypeAll(toolId, API.Backpack))


def useTool(craftingSkill):
    openContainer(API.Backpack)
    openContainer(resourceChest)
    toolId = craftingSkill["tool"]["id"]
    tool = API.FindType(toolId, API.Backpack)
    if not tool:
        statusLabel.Text = "No tool found!"
        statusLabel.Hue = 32
        API.Stop()
    API.UseObject(tool)
    API.Pause(1)


def makeLast(item, craftingSkill, skillName, skillTarget):
    skillLevel = API.GetSkill(skillName)
    itemSkillLevel = item["skill"]

    useTool(craftingSkill)

    while (
        skillLevel.Value < itemSkillLevel
        and skillLevel.Value < skillTarget
        and skillLevel.Value != skillLevel.Cap
    ):
        skillLevel = API.GetSkill(skillName)
        checkResource(item, craftingSkill)
        API.ReplyGump(1999, 460)
        API.Pause(0.5)
        updateGump(item, skillName)

        if API.InJournal("You have worn out"):
            API.ClearJournal()
            checkTools(craftingSkill)
            useTool(craftingSkill)
            craft(item, craftingSkill)

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
            trashContents = getContents(trash)
            while trashContents["items"] == 125:
                API.Pause(1)
                trashContents = getContents(trash)
            moveItem(i.Serial, trash.Serial)
        if method == "Salvage Bag":
            salvageBag = API.FindType(0x0E76, API.Backpack, hue=0x024E)
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
        API.GetSkill(skillName).Value, 1
    )
    skillNumberLabels[skillLabelIndex].Hue = 88
    skillNameLabels[skillLabelIndex].Hue = 88
    itemLabel.Text = itemName


def makeFirst(item, skillName):
    craftingSkill = craftingSkills[skillName]
    targetSkill = item["skill"]
    statusLabel.Text = "Crafting..."

    disposeItem(item, craftingSkill)
    checkResource(item, craftingSkill)
    checkTools(craftingSkill)

    craft(item, craftingSkill)
    updateGump(item, skillName)
    makeLast(item, craftingSkill, skillName, targetSkill)
    API.Pause(0.1)


def trainCraftingSkill(skillName, targetSkill):
    craftingSkill = craftingSkills[skillName]
    items = craftingSkill["items"]
    currentSkillLevel = API.GetSkill(skillName).Value
    while float(currentSkillLevel) < float(targetSkill):
        currentSkillLevel = API.GetSkill(skillName).Value
        currentItem = None
        for item in items:
            itemSkillLevel = item["skill"]
            if currentSkillLevel < itemSkillLevel:
                currentItem = item
                break
        makeFirst(currentItem, skillName)


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
            truncateDecimal(API.GetSkill(key).Value, 1)
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

            tinkeringSkillLevel = API.GetSkill("Tinkering").Value
            for key, box in skillInputs:
                try:
                    val = float(box.Text)
                    if val < 0 or val > API.GetSkill(key).Cap:
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


openContainer(API.Backpack)
API.SysMsg("Target your resource chest", 48)
resourceChestSerial = API.RequestTarget()
resourceChest = API.FindItem(resourceChestSerial)
openContainer(resourceChest)

showCraftingGump()
