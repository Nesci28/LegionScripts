import API
import json

f = open("C:\Games\Taz_BleedingEdge\TazUO-Launcher.win-x64\TazUO\LegionScripts\spelldef.json")
spells = json.load(f)

runebookSerials = {
    "Mixci": 0x4763E494,
    "Maxci": 0x46F215D1,
    "Fexci": 0x45E28818,
}

npcSerials = [
    0x00B1F1B5, # Tailor
    0x0038B183, # Smith
    0x00AE6D87, # Alchemist
    0x00B761E2, # Scribe
    0x00ADCE04, # Tinker
    0x00575BA8, # Carpenter
    # 0x0050753F, # Cook
    # 0x00B5E49E, # Bowyer
]


def isSpellFizzled(spellName):
    s = None
    for spell in spells:
        if spell["Name"].lower() == spellName.lower():
            s = spell
            break
    if not s:
        raise Exception(f"Invalid spellName: {spellName}!")
    castTime = getFcDelay(1.5 + 3)
    API.ClearJournal()
    iterations = int(castTime / 0.1)
    for _ in range(iterations):
        if API.InJournalAny([
            "You lost your concentration.",
            "Your spell fizzles.",
            "You can't cast that spell right now.",
            "You fail to cast"
        ]):
            API.SysMsg("Spell fizzled!", 33)
            return True
        API.Pause(0.1)
    return False

def recallToLocation(index, runebookItem, method):
    while not API.HasGump(89):
        API.UseObject(runebookItem)
        API.Pause(1)

    API.ClearJournal()
    if method == "magery":
        API.ReplyGump(index + 50, 89)
    else:
        API.ReplyGump(index + 74, 89)
    while isSpellFizzled("recall"):
        return recallToLocation(index, runebookItem, method)

def findRunebook(runebookSerial):
    book = API.FindItem(runebookSerial)
    if not book:
        API.SysMsg("Missing runebook")
        API.Stop()
    return book

def detectSpellType():
    magery = API.GetSkill("Magery").Value
    chivalry = API.GetSkill("Chivalry").Value

    if magery >= 40:
        return "magery"
    elif chivalry >= 40:
        return "chilvary"
    else:
        API.SysMsg("No travel skill detected. Need Magery or Chivalry!", 33)
        API.Stop()

playerName = API.Player.Name.replace("Lady ", "").replace("Lord ", "")
runebookSerial = runebookSerials[playerName]
runebook = findRunebook(runebookSerial)
if not runebook:
    API.SysMsg("Runebook not found!")
    API.Stop()

for i, npcSerial in enumerate(npcSerials):
    recallToLocation(i, runebookSerial, detectSpellType())
    npc = API.FindMobile(npcSerial)
    if not npc:
        API.SysMsg("NPC not found!")
        API.Pause(3)
        continue

    for j in range(3):
        while not API.HasGump(455):
            API.ClearJournal()
            API.ContextMenu(npcSerial, 403)
            API.Pause(1)
            isErrored = API.InJournalAny(["An offer may be"])
            if isErrored:
                break
        API.ReplyGump(1, 455)
        API.Pause(1)


