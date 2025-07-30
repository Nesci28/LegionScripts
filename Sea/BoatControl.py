import API
import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
import Gump

importlib.reload(Gump)

# Map compact button labels to full command names
buttonCommands = {
    "Start Tracking": "Start Tracking",
    "Stop Tracking": "Stop Tracking",
    "Stop": "Stop",
    "F": "Forward",
    "B": "Back",
    "L": "Left",
    "R": "Right",
    "FL": "Forward Left",
    "FR": "Forward Right",
    "BL": "Backward Left",
    "BR": "Backward Right"
}

# How directions shift based on player facing
directionMap = {
    "North": {
        "Forward": "Forward Left", "Forward Right": "Forward", "Forward Left": "Left",
        "Right": "Forward Right", "Left": "Back Left",
        "Back Right": "Right", "Back": "Back Right", "Back Left": "Back"
    },
    "South": {
        "Forward": "Back Right", "Forward Right": "Back", "Forward Left": "Right",
        "Right": "Back Left", "Left": "Forward Right",
        "Back": "Forward Left", "Back Right": "Left", "Back Left": "Forward"
    },
    "West": {
        "Forward": "Forward Right", "Forward Right": "Right", "Forward Left": "Forward",
        "Right": "Back Right", "Left": "Forward Left",
        "Back": "Back Left", "Back Right": "Back", "Back Left": "Left"
    },
    "East": {
        "Forward": "Back Left", "Forward Right": "Left", "Forward Left": "Back",
        "Right": "Forward Left", "Left": "Back Right",
        "Back": "Forward Right", "Back Right": "Forward", "Back Left": "Right"
    }
}

def getButtonGraphic(label):
    buttonGraphics = {
        "FL": [4010, 4010],
        "F": [4011, 4011],
        "FR": [4012, 4012],
        "L": [4013, 4013],
        "Stop": [4014, 4014],
        "R": [4015, 4015],
        "BL": [4016, 4016],
        "B": [4017, 4017],
        "BR": [4018, 4018],
        "Start Tracking": [4010, 4009], # Done
        "Stop Tracking": [4020, 4021] # Done
    }
    gumpId = buttonGraphics.get(label, 9722)
    return gumpId

def showAndHandleShipGump():
    width = 320
    height = 250

    gump = Gump.Gump(width, height)
    g = gump.init()

    # Layout
    buttons = []
    startX = 15
    startY = 15
    btnSize = 34
    colGap = 90
    rowGap = 34

    layoutMap = {
        0: ["FL", "F", "FR"],
        1: ["L", "Stop", "R"],
        2: ["BL", "B", "BR"],
    }

    for rowIdx, rowLabels in layoutMap.items():
        for colIdx, label in enumerate(rowLabels):
            x = startX + colIdx * colGap
            y = startY + rowIdx * rowGap
            gumpId = getButtonGraphic(label)
            btn = API.CreateGumpButton("", 0, gumpId[0], gumpId[1], gumpId[1])
            API.SysMsg(f"x: {x}")
            API.SysMsg(f"y: {y}")
            btn.SetX(x)
            btn.SetY(y)
            g.Add(btn)
            buttons.append((btn, label))
            # text = API.CreateGumpLabel(label)
            # text.SetX(x + btnSize + 4)
            # text.SetY(y + 9)
            # g.Add(text)
    API.AddGump(g)

    x = 50
    y = 115
    for i, cmd in enumerate(["Start Tracking", "Stop Tracking"]):
        gumpId = getButtonGraphic(cmd)
        btn = API.CreateGumpButton("", 0, gumpId[0], gumpId[1], gumpId[1])
        btn.SetX(x + (100 * i))
        btn.SetY(y)
        g.Add(btn)
        # text = API.CreateGumpLabel(label)
        # text.SetX(45 + btnSize + 4)
        # text.SetY(105 + 9)
        # g.Add(text)

    while True:
        for btn, label in buttons:
            if btn.IsClicked:
                direction = API.Player.Direction
                fullCommand = buttonCommands.get(label)

                if fullCommand:
                    translated = directionMap.get(direction, {}).get(fullCommand, fullCommand)
                    API.Msg(translated)

        API.Pause(0.1)

showAndHandleShipGump()
