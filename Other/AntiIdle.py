import API
import importlib
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump
import Timer
import Magic

importlib.reload(Gump)
importlib.reload(Timer)
importlib.reload(Magic)

from Gump import Gump
from Timer import Timer
from Magic import Magic


class AntiIdle:
    def __init__(self):
        self._running = True
        self.gump = None

        self._magic = Magic()

    def main(self):
        try:
            self._showGump()
        except Exception as e:
            API.SysMsg(f"AntiIdle e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            antiIdle.gump.tick()
            antiIdle.gump.tickSubGumps()
        return True

    def run(self):
        if Timer.exists(60, "AntiIdle", 18):
            return
        API.PreTarget(API.Player.Serial, "beneficial")
        self._magic.cast("heal")
        Timer.create(60, "AntiIdle", 18)

    def _showGump(self):
        pass
        # width = 500
        # height = 51
        # g = Gump(width, height, self._onClose)
        # self.gump = g
        # y = 1

        # self.gump.create()

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


antiIdle = AntiIdle()
antiIdle.main()
while antiIdle._isRunning():
    antiIdle.tick()
    antiIdle.run()
    API.Pause(0.1)
