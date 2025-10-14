import API
import importlib
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump

importlib.reload(Gump)


from Gump import Gump


class Blank:
    def __init__(self):
        self._running = True
        self.gump = None

    def main(self):
        try:
            self._showGump()
        except Exception as e:
            API.SysMsg(f"Blank e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            blank.gump.tick()
            blank.gump.tickSubGumps()
        return True

    def run(self):
        pass

    def _showGump(self):
        width = 500
        height = 51
        g = Gump(width, height, self._onClose)
        self.gump = g
        y = 1

        self.gump.create()

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


blank = Blank()
blank.main()
while blank._isRunning():
    blank.tick()
    blank.run()
    API.Pause(0.1)
