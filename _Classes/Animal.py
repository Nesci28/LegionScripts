class Animal:
    def __init__(self, name, mobileID, color, minTamingSkill, maxTamingSkill, packType):
        self.name = name
        self.mobileID = mobileID
        self.color = color
        self.minTamingSkill = minTamingSkill
        self.maxTamingSkill = maxTamingSkill
        self.packType = packType

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

    @staticmethod
    def kill(magic, animal, spellToKill):
        API.PreTarget(animal.Serial, "Harmful")
        magic.cast(spellToKill)