class Animal:
    def __init__(self, name, mobileID, color, minTamingSkill, maxTamingSkill, packType, killingSpell):
        self.name = name
        self.mobileID = mobileID
        self.color = color
        self.minTamingSkill = minTamingSkill
        self.maxTamingSkill = maxTamingSkill
        self.packType = packType
        self.killinSpell = killingSpell

    @staticmethod
    def rename(animal, name):
        API.Rename(animal.Serial, name)
        API.Pause(0.1)

    @staticmethod
    def release(animal):
        API.ContextMenu(animal.Serial, 138)
        while not API.HasGump(601):
            API.Pause(0.1)
        API.ReplyGump(2, 601)

    def kill(self, animalSerial):
        animal = API.FindMobile(animalSerial)
        while animal and animal.Hits > 0 and not animal.IsDead:
            API.CastSpell(self.killinSpell)
            API.WaitForTarget("harmful")
            API.Target(animalSerial)
            while API.Player.IsCasting or API.Player.IsRecovering:
                API.Pause(0.05)
            animal = API.FindMobile(animal.Serial)