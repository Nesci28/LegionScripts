import API

animalSerial = API.RequestTarget()

while True:
    API.PreTarget(animalSerial, "neutral")
    API.UseSkill("Animal Lore")
    while not API.HasGump(475):
        API.Pause(0.1)
    API.CloseGump(475)
    API.Pause(2)