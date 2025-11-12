import API
import importlib
import traceback
from collections import deque
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump
import Util
import Python

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Python)

from Gump import Gump
from Util import Util
from Python import Python


class ResourceGrabber:
    CHEST_SERIAL = 0x41C617E5
    CLOTH_AMOUNT = 200
    LEATHER_AMOUNT = 200
    GEM_AMOUNT = 100
    INGOTS_AMOUNT = 200
    BOARDS_AMOUNT = 200
    IMBUING_AMOUNT = 100

    ingots = {
        "iron": {
            "graphic": 0x1BF2,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "dullCopper": {
            "graphic": 0x1BF2,
            "hue": 2419,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "shadow": {
            "graphic": 0x1BF2,
            "hue": 2406,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "copper": {
            "graphic": 0x1BF2,
            "hue": 2413,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "bronze": {
            "graphic": 0x1BF2,
            "hue": 2418,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "golden": {
            "graphic": 0x1BF2,
            "hue": 2213,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "agapite": {
            "graphic": 0x1BF2,
            "hue": 2425,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "verite": {
            "graphic": 0x1BF2,
            "hue": 2207,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
        "valorite": {
            "graphic": 0x1BF2,
            "hue": 2219,
            "countLabel": None,
            "grabButton": None,
            "amount": INGOTS_AMOUNT,
        },
    }
    cloths = {
        "cloth": {
            "graphic": 0x1766,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": CLOTH_AMOUNT,
        }
    }
    leathers = {
        "leather": {
            "graphic": 0x1081,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": LEATHER_AMOUNT,
        },
        "spined": {
            "graphic": 0x1081,
            "hue": 2220,
            "countLabel": None,
            "grabButton": None,
            "amount": LEATHER_AMOUNT,
        },
        "horned": {
            "graphic": 0x1081,
            "hue": 2117,
            "countLabel": None,
            "grabButton": None,
            "amount": LEATHER_AMOUNT,
        },
        "barbed": {
            "graphic": 0x1081,
            "hue": 2129,
            "countLabel": None,
            "grabButton": None,
            "amount": LEATHER_AMOUNT,
        },
    }
    gems = {
        "amber": {
            "graphic": 0x0F25,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "citrine": {
            "graphic": 0x0F15,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "ruby": {
            "graphic": 0x0F13,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "tourmaline": {
            "graphic": 0x0F18,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "amethyst": {
            "graphic": 0x0F16,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "emerald": {
            "graphic": 0x0F10,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "sapphire": {
            "graphic": 0x0F11,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "starSapphire": {
            "graphic": 0x0F0F,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
        "diamond": {
            "graphic": 0x0F26,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": GEM_AMOUNT,
        },
    }
    imbuingMaterials = {
        "relicFragment": {
            "graphic": 0x2DB3,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": IMBUING_AMOUNT,
        },
        "magicalResidue": {
            "graphic": 0x2DB1,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": IMBUING_AMOUNT,
        },
        "enchantedEssence": {
            "graphic": 0x2DB2,
            "hue": 0,
            "countLabel": None,
            "grabButton": None,
            "amount": IMBUING_AMOUNT,
        },
    }

    def __init__(self):
        self._running = True
        self.gump = None
        self._queue = deque()
        self._isProcessing = False
        self._isShowned = False

    def main(self):
        try:
            self._showGump()
        except Exception as e:
            API.SysMsg(f"ResourceGrabber e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            resourceGrabber.gump.tick()
            resourceGrabber.gump.tickSubGumps()
            container = API.FindItem(self.CHEST_SERIAL)
            if container and container.Opened:
                self._update()
                self._isShowned = True
            else:
                self.gump.hide()
                self._isShowned = False
        return True

    def _update(self):
        if not self._isShowned:
            self.gump.show()

    def run(self):
        if self._isProcessing or not self._queue:
            return

        item = self._queue.popleft()
        self._isProcessing = True

        Util.moveItem(item["serial"], API.Backpack, item["amount"])
        self._isProcessing = False

    def _showGump(self):
        xSpaceButton = 32
        xSpaceLabel = 115
        xSpaceCol = 200

        width = 1 + (xSpaceCol * 5)
        height = 218
        g = Gump(width, height, self._onClose, False)
        self.gump = g

        y = 1
        x = 1

        for ingot in self.ingots:
            i = self.ingots[ingot]
            i["grabButton"] = self.gump.addButton(
                "", x, y, "grab", self.gump.onClick(lambda ingot=i: self._grab(ingot))
            )
            x += xSpaceButton
            self.gump.addLabel(Python.camelToSpace(ingot), x, y)
            x += xSpaceLabel
            items = Util.findTypeAll(self.CHEST_SERIAL, i["graphic"], i["hue"])
            count = 0
            for item in items:
                count += item.Amount
            i["countLabel"] = self.gump.addLabel(str(count), x, y)
            y += 23
            x = 1

        x = x + xSpaceCol
        y = 1
        for cloth in self.cloths:
            i = self.cloths[cloth]
            i["grabButton"] = self.gump.addButton(
                "", x, y, "grab", self.gump.onClick(lambda cloth=i: self._grab(cloth))
            )
            x += xSpaceButton
            self.gump.addLabel(Python.camelToSpace(cloth), x, y)
            x += xSpaceLabel
            items = Util.findTypeAll(self.CHEST_SERIAL, i["graphic"], i["hue"])
            count = 0
            for item in items:
                count += item.Amount
            i["countLabel"] = self.gump.addLabel(str(count), x, y)
            y += 23
            x = x - xSpaceButton - xSpaceLabel

        x = x + xSpaceCol
        y = 1
        for leather in self.leathers:
            i = self.leathers[leather]
            i["grabButton"] = self.gump.addButton(
                "",
                x,
                y,
                "grab",
                self.gump.onClick(lambda leather=i: self._grab(leather)),
            )
            x += xSpaceButton
            self.gump.addLabel(Python.camelToSpace(leather), x, y)
            x += xSpaceLabel
            items = Util.findTypeAll(self.CHEST_SERIAL, i["graphic"], i["hue"])
            count = 0
            for item in items:
                count += item.Amount
            i["countLabel"] = self.gump.addLabel(str(count), x, y)
            y += 23
            x = x - xSpaceButton - xSpaceLabel

        x = x + xSpaceCol
        y = 1
        for gem in self.gems:
            i = self.gems[gem]
            i["grabButton"] = self.gump.addButton(
                "", x, y, "grab", self.gump.onClick(lambda gem=i: self._grab(gem))
            )
            x += xSpaceButton
            self.gump.addLabel(Python.camelToSpace(gem), x, y)
            x += xSpaceLabel
            items = Util.findTypeAll(self.CHEST_SERIAL, i["graphic"], i["hue"])
            count = 0
            for item in items:
                count += item.Amount
            i["countLabel"] = self.gump.addLabel(str(count), x, y)
            y += 23
            x = x - xSpaceButton - xSpaceLabel

        x = x + xSpaceCol
        y = 1
        for imbuingMaterial in self.imbuingMaterials:
            i = self.imbuingMaterials[imbuingMaterial]
            i["grabButton"] = self.gump.addButton(
                "",
                x,
                y,
                "grab",
                self.gump.onClick(
                    lambda imbuingMaterial=i: self._grab(imbuingMaterial)
                ),
            )
            x += xSpaceButton
            self.gump.addLabel(Python.camelToSpace(imbuingMaterial), x, y)
            x += xSpaceLabel
            items = Util.findTypeAll(self.CHEST_SERIAL, i["graphic"], i["hue"])
            count = 0
            for item in items:
                count += item.Amount
            i["countLabel"] = self.gump.addLabel(str(count), x, y)
            y += 23
            x = x - xSpaceButton - xSpaceLabel

        self.gump.create()

    def _grab(self, material):
        totalAmount = material["amount"]
        items = Util.findTypeAll(self.CHEST_SERIAL, material["graphic"])
        for item in items:
            if item.Amount > totalAmount:
                self._queue.append({"serial": item.Serial, "amount": totalAmount})
                break
            else:
                totalAmount -= item.Amount
                self._queue.append({"serial": item.Serial, "amount": item.Amount})

    def _isRunning(self):
        return self._running

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            for subGump in self.gump.subGumps:
                subGump.destroy()
            self.gump.destroy()
            self.gump = None
        API.Stop()


resourceGrabber = ResourceGrabber()
resourceGrabber.main()
while resourceGrabber._isRunning():
    resourceGrabber.tick()
    resourceGrabber.run()
    API.Pause(0.1)
