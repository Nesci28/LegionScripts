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
        self._deadPetSerial = None

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
        if Math.distanceBetween(API.Player, pet) > 1 and not Timer.exists(3, "All follow me", 21):
            Timer.create(3, "All follow me", 21)
            API.Msg("All Follow Me")
        values = Util.getSkillInfo("Veterinary")
        skillValue = values["value"]
        if skillValue < 60 and pet.HitsDiff == 0:
            self._cast("Magic Arrow")

        if skillValue > 60 and skillValue < 79.9 and not pet.IsPoisoned:
            self._cast("poison")

        timer = 3
        if skillValue >= 80:
            timer = 5.5
        if Timer.exists(timer, "Veterinary", 22):
            return

        if skillValue >= 79.9:
            if not self._deadPetSerial:
                mobiles = API.GetAllMobiles(None, 1, [API.Notoriety.Unknown, API.Notoriety.Innocent, API.Notoriety.Ally])
                for mobile in mobiles:
                    if mobile.IsDead:
                        self._deadPetSerial = mobile.Serial
            if self._deadPetSerial:
                deadPet = API.FindMobile(self._deadPetSerial)
                if not deadPet:
                    API.SysMsg("Dead pet not found", 33)
                    API.Stop()
        if (skillValue < 60 and pet.HitsDiff != 0) or (skillValue >= 60 and skillValue < 79.9 and pet.IsPoisoned) or (skillValue > 79.9 and pet.IsDead):
            Util.useObject(bandages.Serial)
            API.WaitForTarget()
            API.Target(self._petSerial)
            timer = 3
            if skillValue >= 80:
                timer = 5.5
            Timer.create(timer, "Veterinary", 22) 

    def _cast(self, spell):
        API.PreTarget(self._petSerial, "harmful")
        self._magic.cast(spell)
        API.Pause(2)

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
