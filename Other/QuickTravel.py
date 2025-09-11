import API
import importlib
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util
import Gump
import Magic

importlib.reload(Util)
importlib.reload(Gump)
importlib.reload(Magic)

from Gump import Gump
from Util import Util
from Magic import Magic


class QuickTravel:
    configs = {
        "Nescira": {
            "runebookSerial": 0x4090422B,
            "house": 14,
            "bank": 1,
            "moongate": 0,
            "library": 3,
        },
        "Mixci": {
            "runebookSerial": 0x4771D62C,
            "house": 15,
            "bank": 13,
            "moongate": 14,
            "library": 2,
        },
        "Maxci": {
            "runebookSerial": 0x466479BC,
            "house": 4,
            "bank": 2,
            "moongate": 1,
            "library": 3,
        },
        "Fexci": {
            "runebookSerial": 0x467468CC,
            "house": 15,
            "bank": 0,
            "moongate": 1,
            "library": 3,
        },
        "Jean": {
            "runebookSerial": 0x41FC85FA,
            "house": 4,
            "bank": 2,
            "moongate": 1,
            "library": 3,
        },
        "Dexci": {
            "runebookSerial": 0x468AD8F3,
            "house": 14,
            "bank": 2,
            "moongate": 1,
            "library": 3,
        },
    }

    def __init__(self):
        self.config = None
        self.gump = None
        self.magic = Magic()
        self._running = True
        self._initialized = False

    def main(self):
        try:
            playerName = Util.getPlayerName()
            if playerName not in self.configs:
                API.SysMsg("No config found for this character.", 33)
                self._running = False
                return

            self.config = self.configs[playerName]
            self._findRunebook()
            self._showGump()
            self.gump.create()
            self._initialized = True

        except Exception as e:
            API.SysMsg(f"QuickTravel error: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def _findRunebook(self):
        Util.openContainer(API.Backpack)
        book = API.FindItem(self.config["runebookSerial"])
        if not book:
            raise Exception("Missing runebook")
        return book

    def _recallTo(self, runeIndex):
        runebook = self._findRunebook()
        self.magic.recallToLocation(runeIndex, runebook)

    def _openRunebook(self):
        runebook = self._findRunebook()
        API.UseObject(runebook)

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            for subGump in self.gump.subGumps:
                subGump.destroy()
            self.gump.destroy()
            self.gump = None
        API.SysMsg("QuickTravel cleanup done.", 66)
        API.Stop()

    def _showGump(self):
        width, height = 200, 140
        g = Gump(width, height, self._onClose)
        self.gump = g
        y = 10

        for locationName in ["house", "bank", "moongate", "library"]:
            label = locationName.capitalize()
            runeIndex = self.config[locationName]
            g.addButton(
                label,
                20,
                y,
                "radioGreen",
                g.onClick(
                    lambda idx=runeIndex: self._recallTo(idx),
                    f"Recalling to: {label}",
                    "Ready",
                ),
            )
            y += 20

        g.addButton(
            "Open Runebook",
            20,
            y,
            "radioRed",
            g.onClick(self._openRunebook, "Opening runebook", "Ready"),
        )

    def _isRunning(self):
        return self._running

    def tick(self):
        Util.openContainer(API.Backpack)
        if API.HasGump(999139):
            API.CloseGump(999139)
        if not self._running:
            return False
        if self.gump:
            self.gump.tick()
            self.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True


qt = QuickTravel()
qt.main()
while qt._isRunning():
    qt.gump.tick()
    qt.gump.tickSubGumps()
    qt.tick()
    API.Pause(0.1)
