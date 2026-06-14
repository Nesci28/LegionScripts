from Util import Util


class Lockpicking:
    skillName = "Lockpicking"
    lockpickGraphic = 0x14FB
    chestGraphics = [0x09A8, 0x0E80]

    @staticmethod
    def _findLockpicks():
        return API.FindType(Lockpicking.lockpickGraphic, API.Backpack)

    @staticmethod
    def _findChests():
        chests = []
        for chestGraphic in Lockpicking.chestGraphics:
            chests.extend(API.FindTypeAll(chestGraphic, 4294967295, 2))
        return chests

    @staticmethod
    def validate(skillCap=None):
        errors = []
        if not Lockpicking._findLockpicks():
            errors.append("Lockpicking - Missing lockpicks.")
        if not Lockpicking._findChests():
            errors.append("Lockpicking - No training chests found within 2 tiles.")
        return errors

    def __init__(self, skillCap, label=None, skillLevelLabel=None):
        self.skillCap = skillCap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        API.SetSkillLock(self.skillName, "up")

    def _isUnlocked(self):
        return API.InJournal("The lock quickly yields to your skill.") or API.InJournal(
            "This does not appear to be locked."
        )

    def trainOnce(self):
        lockpicks = self._findLockpicks()
        if not lockpicks:
            API.SysMsg("Lockpicking - Missing lockpicks.", 33)
            API.Stop()
            return False

        attempted = False
        for chest in self._findChests():
            API.ClearJournal()
            while not self._isUnlocked():
                attempted = True
                API.UseObject(lockpicks.Serial)
                API.WaitForTarget("any", 3)
                API.Target(chest.Serial)
                API.Pause(1)
        return attempted

    def train(self, calculateSkillLabels=None):
        while Util.getSkillInfo(self.skillName)["value"] < self.skillCap:
            attempted = self.trainOnce()
            if calculateSkillLabels:
                calculateSkillLabels()
            if not attempted:
                API.SysMsg(
                    "Lockpicking - No locked training chests found.",
                    33,
                )
                break
