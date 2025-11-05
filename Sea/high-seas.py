import API
from math import floor
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)

# --- Global Variables ---
cannons = {
    "forwardPort": {},
    "amidshipsPort": {},
    "forwardStarboard": {},
    "amidshipsStarboard": {},
}

gumpIdConst = 888888


def getCannonInfo(gumpId):
    for info in cannons.values():
        if info.get("gumpId") == gumpId:
            return info
    raise Exception("Cannon not found for gumpId")


def getItemInBackpack(graphic):
    return API.FindType(graphic, API.Backpack)


def isCannonInState(gumpId, stateText):
    info = getCannonInfo(gumpId)
    if not API.HasGump(gumpId):
        API.UseObject(info["item"].Serial)
        API.Pause(1)
    return API.GumpContains(stateText, gumpId)


def waitForUniqueGump(item):
    startGump = API.HasGump()
    for _ in range(10):
        API.UseObject(item.Serial)
        API.Pause(1)
        if API.HasGump() != startGump:
            return API.HasGump()
    raise Exception("Unable to open unique gump for item")


# --- Main Logic ---
def setup():
    graphics = [0x4216, 0x4217, 0x4218, 0x4219]
    items = []
    for g in graphics:
        items += API.FindTypeAll(g, 4294967295, 2)

    if len(items) != 4:
        raise Exception("Must be standing in the middle of 4 cannons.")

    for item in items:
        gumpId = waitForUniqueGump(item)
        isForward = API.GumpContains("Forward")
        isPort = API.GumpContains("Port")
        position = "forward" if isForward else "amidships"
        side = "Port" if isPort else "Starboard"
        key = position + side
        cannons[key] = {"item": item, "serial": item.Serial, "gumpId": gumpId}


def reload():
    for info in cannons.values():
        for contained in API.ItemsInContainer(info["item"].Serial):
            Util.Util.moveItem(contained, API.Backpack)

    itemTypes = {"balls": 0x4224, "cords": 0x1420, "charges": 0xA2BE}
    items = {k: getItemInBackpack(v) for k, v in itemTypes.items()}
    counts = {k: floor(item.Amount / 4) for k, item in items.items()}

    for info in cannons.values():
        for kind in ["balls", "cords", "charges"]:
            Util.Util.moveItem(items[kind], info["item"], counts[kind])


def prep(gumpId):
    if API.GumpContains("PREP", gumpId):
        for _ in range(10):
            API.ReplyGump(1, gumpId)
            API.Pause(0.05)



def prepAll(side):
    for name, info in cannons.items():
        if side == "all" or side.lower() in name.lower():
            gumpId = info.get("gumpId")
            if not isCannonInState(gumpId, "FIRE"):
                prep(gumpId)
    API.SysMsg("Done Prepping")


def fireCannons(side):
    if side == "port":
        API.Msg("Fire Port Broadside")
    elif side == "starboard":
        API.Msg("Fire Starboard Broadside")
    API.Pause(2)
    prepAll(side)


# --- Gump UI ---
def sendGump():
    width = 240
    height = 120
    g = API.CreateGump(True, True)
    g.SetWidth(width)
    g.SetHeight(height)
    g.CenterXInViewPort()
    g.CenterYInViewPort()

    for x, y, w, h in [
        (-5, -5, width, 5),
        (-5, height - 10, width, 5),
        (-5, -5, 5, height),
        (width - 10, -5, 5, height),
    ]:
        border = API.CreateGumpColorBox(1, "#a86b32")
        border.SetX(x)
        border.SetY(y)
        border.SetWidth(w)
        border.SetHeight(h)
        g.Add(border)

    bg = API.CreateGumpColorBox(0.75, "#000000")
    bg.SetWidth(width - 10)
    bg.SetHeight(height - 10)
    g.Add(bg)

    buttonRows = [
        [("Left", fireCannons, "port"), ("Right (NPC)", fireCannons, "starboard")],
        [("Reload", reload, None), ("Prep", prepAll, "all")],
    ]

    yOffset = 10
    buttons = []

    for i, row in enumerate(buttonRows):
        y = yOffset + (45 * i)
        for j, (label, action, arg) in enumerate(row):
            x = 20 + (75 * j)
            btn = API.CreateGumpButton("", 996, 9722, 9721, 9721)
            btn.SetX(x)
            btn.SetY(y)
            g.Add(btn)
            buttons.append((btn, action, arg))

            lbl = API.CreateGumpLabel(label)
            lbl.SetX(x + 30)
            lbl.SetY(y)
            g.Add(lbl)

    statusLabel = API.CreateGumpLabel("")
    statusLabel.SetX(20)
    statusLabel.SetY(height - 30)
    g.Add(statusLabel)

    API.AddGump(g)

    while True:
        API.Pause(0.1)
        for btn, action, arg in buttons:
            if btn.IsClicked:
                statusLabel.Text = f"Running: {label}"
                try:
                    action(arg) if arg else action()
                except Exception as e:
                    API.SysMsg(f"Error: {str(e)}", 33)
                statusLabel.Text = ""  # Clear after action


# --- Entry Point ---
def main():
    setup()
    sendGump()


main()
