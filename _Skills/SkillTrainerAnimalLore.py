from Util import Util


class AnimalLore:
    skillName = "Animal Lore"

    @staticmethod
    def validate(skillCap=None):
        return []

    def __init__(self, skillCap, label=None, skillLevelLabel=None):
        self.skillCap = skillCap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        API.SetSkillLock(self.skillName, "up")
        API.SysMsg("Target an animal for Animal Lore training.", 66)
        self.animalSerial = API.RequestTarget(30)
        if not self.animalSerial:
            API.SysMsg("Animal Lore - No target selected.", 33)
            API.Stop()

    def trainOnce(self):
        API.PreTarget(self.animalSerial, "neutral")
        API.UseSkill(self.skillName)
        waited = 0
        while not API.HasGump(475) and waited < 5:
            API.Pause(0.1)
            waited += 0.1
        if API.HasGump(475):
            API.CloseGump(475)
        API.Pause(2)

    def train(self, calculateSkillLabels=None):
        while Util.getSkillInfo(self.skillName)["value"] < self.skillCap:
            self.trainOnce()
            if calculateSkillLabels:
                calculateSkillLabels()
