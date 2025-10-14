import API
import importlib
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump
import Util
import Math
import Magic
import Timer

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Magic)
importlib.reload(Timer)

from Gump import Gump
from Util import Util
from Math import Math
from Magic import Magic
from Timer import Timer


class Veterinary:
    def __init__(self):
        self._running = True
        self.gump = None

        self._bandageId = 0x0E21
        self._magic = Magic()
        self._petSerial = None

    def main(self):
        try:
            self._showGump()
        except Exception as e:
            API.SysMsg(f"Veterinary e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            veterinary.gump.tick()
            veterinary.gump.tickSubGumps()
        return True

    def run(self):
        if not self._petSerial:
            self._petSerial = API.RequestTarget()
        bandages = Util.findTypeWithSpecialHue(self._bandageId, API.Backpack, 1, 0)
        pet = API.FindMobile(self._petSerial)
        if not bandages or not pet:
            API.SysMsg("Pet/Bandages not found", 33)
            API.Stop()
        if Math.distanceBetween(API.Player, pet) > 1:
            API.Msg("All Follow Me")
        if Timer.exists(3, "Veterinary", 22):
            return
        if pet.HitsDiff == 0:
            API.PreTarget(self._petSerial, "harmful")
            values = Util.getSkillInfo("Veterinary")
            skillValue = values["value"]
            if skillValue < 60:
                self._magic.cast("Magic Arrow")
            if skillValue > 60 and skillValue < 80:
                self._magic.cast("Poison")
            API.Pause(2)
        if pet.HitsDiff != 0:
            Util.useObject(bandages.Serial)
            API.WaitForTarget()
            API.Target(self._petSerial)
            Timer.create(3, "Veterinary", 22) 


    def _showGump(self):
        pass
        # width = 500
        # height = 51
        # g = Gump(width, height, self._onClose, False)
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


veterinary = Veterinary()
veterinary.main()
while veterinary._isRunning():
    veterinary.tick()
    veterinary.run()
    API.Pause(0.1)
