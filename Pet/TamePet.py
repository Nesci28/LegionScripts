import API
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Math

importlib.reload(Math)

class TamingScript:
    tamingDelay = 10
    checkInterval = 0.5
    maxTamingAttempts = 10

    def __init__(self):
        self.petSerial = None
        self.pet = None

    def isAngry(self):
        return API.InJournalAny(["You seem to anger the beast!"])

    def isTooFar(self):
        return API.InJournalAny(["It's too far away."])

    def waitForPetInRange(self, maxRange=3):
        while not API.HasTarget():
            distance = Math.Math.distanceBetween(API.Player, self.pet)
            if distance <= maxRange:
                break
            API.Pause(self.checkInterval)

    def attemptTame(self):
        API.ClearJournal()
        API.UseSkill("Animal Taming")
        API.WaitForTarget()
        API.Target(self.petSerial)

    def run(self):
        API.SysMsg("Select the wild pet to tame", 34)
        self.petSerial = API.RequestTarget()
        self.pet = API.FindMobile(self.petSerial)
        attempts = 0
        while attempts < self.maxTamingAttempts:
            self.waitForPetInRange()
            API.ClearJournal()
            self.attemptTame()
            API.Pause(0.5)

            if not self.isAngry() and not self.isTooFar():
                API.Pause(self.tamingDelay)
                attempts += 1

        else:
            API.SysMsg("Too many attempts. Stopping.", 38)


TamingScript().run()
