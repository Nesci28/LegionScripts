import API
import time
from math import ceil

def truncateDecimal(n1, d):
    n = str(n1)
    return n if "." not in n else n[:n.find(".") + d + 1]



spellQueues = {
    "Magery": [
        {"skill": 45, "spell": "Fireball", "manaCost": 9, "castingTime": 1},
        {"skill": 55, "spell": "Lightning", "manaCost": 11, "castingTime": 1.25},
        {"skill": 65, "spell": "Paralyze", "manaCost": 14, "castingTime": 1.5},
        {"skill": 75, "spell": "Reveal", "manaCost": 20, "castingTime": 1.75},
        {"skill": 90, "spell": "Flamestrike", "manaCost": 40, "castingTime": 2},
        {"skill": 120, "spell": "Earthquake", "manaCost": 50, "castingTime": 2.25},
    ],
    "Mysticism": [
        {"skill": 60, "spell": "Stone Form", "manaCost": 11, "castingTime": 1.25},
        {"skill": 80, "spell": "Cleansing Winds", "manaCost": 20, "castingTime": 1.75},
        {"skill": 95, "spell": "Hail Storm", "manaCost": 50, "castingTime": 2},
        {"skill": 120, "spell": "Nether Cyclone", "manaCost": 50, "castingTime": 2.25},
    ],
    "Necromancy": [
        {"skill": 50, "spell": "Pain Spike", "manaCost": 5, "castingTime": 0.75},
        {"skill": 70, "spell": "Horrific Beast", "manaCost": 11, "castingTime": 1.75},
        {"skill": 90, "spell": "Wither", "manaCost": 23, "castingTime": 1},
        {"skill": 95, "spell": "Lich Form", "manaCost": 25, "castingTime": 1.75},
        {"skill": 120, "spell": "Vampiric Embrace", "manaCost": 25, "castingTime": 1.75},
    ],
    "Chivalry": [
        {"skill": 45, "spell": "Consecrate Weapon", "manaCost": 10, "castingTime": 0.75},
        {"skill": 60, "spell": "Divine Fury", "manaCost": 15, "castingTime": 1.25},
        {"skill": 70, "spell": "Enemy of One", "manaCost": 20, "castingTime": 0.75},
        {"skill": 90, "spell": "Holy Light", "manaCost": 10, "castingTime": 1},
        {"skill": 120, "spell": "Noble Sacrifice", "manaCost": 20, "castingTime": 1.75},
    ],
    "Spellweaving": [
        {"skill": 20, "spell": "Arcane Circle", "manaCost": 24, "castingTime": 1},
        {"skill": 33, "spell": "Immolating Weapon", "manaCost": 32, "castingTime": 1},
        {"skill": 52, "spell": "Reaper Form", "manaCost": 34, "castingTime": 2.5},
        {"skill": 74, "spell": "Essence of Wind", "manaCost": 40, "castingTime": 3},
        {"skill": 90, "spell": "Wildfire", "manaCost": 50, "castingTime": 2.5},
        {"skill": 120, "spell": "Word of Death", "manaCost": 50, "castingTime": 3.5},
    ],
}

schoolKeys = list(spellQueues.keys())

def autoHeal():
    player = API.Player
    if player.Hits >= ceil(player.HitsMax / 3):
        return

    skills = {s: API.GetSkill(s).Value for s in ["Magery", "Chivalry", "Spellweaving", "Spirit Speak"]}

    if skills["Magery"] >= 50:
        API.CastSpell("Greater Heal")
    elif skills["Magery"] >= 30:
        API.CastSpell("Heal")
    elif skills["Chivalry"] >= 30:
        API.CastSpell("Close Wounds")
    elif skills["Spirit Speak"] >= 30:
        API.UseSkill("Spirit Speak")
        API.Pause(7)
        return
    elif skills["Spellweaving"] >= 24 and not API.BuffExists("Gift of Renewal"):
        API.CastSpell("Gift of Renewal")
    else:
        bandage = API.FindType(0x0E21, API.Backpack)
        if bandage:
            API.UseObject(bandage.Serial)
            if API.WaitForTarget("any", 3):
                API.TargetSelf()
                API.Pause(7)
            return

    if API.WaitForTarget("any", 3):
        API.TargetSelf()
        API.Pause(4)

def regenMana(manaRequired):
    if API.Player.Mana >= manaRequired:
        return 0
    lastAttempt = 0
    while API.Player.Mana < API.Player.ManaMax:
        if not API.BuffExists("Actively Meditating"):
            now = time.time()
            if now - lastAttempt >= 11:
                API.UseSkill("Meditation")
                lastAttempt = now
        API.Pause(0.1)

def getFcDelay(castingTime):
    fc = getattr(API.Player, "FasterCasting", 0)
    return castingTime - (fc * 0.25)

def getFcrDelay():
    fcr = getattr(API.Player, "FasterCastRecovery", 0)
    return max(1.5 - (fcr * 0.25), 0)

def findItemWithProp(prop):
    for item in API.ItemsInContainer(API.Backpack):
        if prop in API.ItemNameAndProps(item.Serial).split("\n"):
            return item

def hasWeapon():
    return API.FindLayer("OneHanded") or API.FindLayer("TwoHanded")


            

def trainSchool(schoolName, skillCap, label, skillLabel, spellLabel, runningLabel):
    skill = API.GetSkill(schoolName).Value
    queue = spellQueues[schoolName]

    while skill < skillCap:
        label.Hue = skillLabel.Hue = 88
        skillLabel.Text = truncateDecimal(skill, 1)
        autoHeal()

        for entry in queue:
            if skill < entry["skill"]:
                spellLabel.Text = entry["spell"]

                # isWearingWeapon = hasWeapon()
                # if entry["spell"] == "Immolating Weapon" and not isWearingWeapon:
                #     item = findItemWithProp("Spell Channeling")
                #     # API.EquipItem(item)
                # elif entry["spell"] == "Consecrate Weapon" and not isWearingWeapon:
                #     item = findItemWithProp("One-handed Weapon") or findItemWithProp("Two-handed Weapon")
                #     # API.EquipItem(item)
                # elif isWearingWeapon:
                #     API.ClearLeftHand()
                #     API.ClearRightHand()

                castTime = getFcDelay(entry["castingTime"])
                recoverTime = getFcrDelay()
                totalPause = castTime + recoverTime

                lmc = API.Player.LowerManaCost
                manaCost = ceil(entry["manaCost"] * (1 - lmc / 100))

                regenMana(manaCost)
                checkIfGearBroken(label, skillLabel, spellLabel, runningLabel)

                API.CastSpell(entry["spell"])
                if API.WaitForTarget("any", castTime + 2):
                    if entry["skill"] == "Magery":
                        spellbook = API.FindType(0x0EFA, API.Backpack)
                        API.Target(spellbook.Serial if spellbook else API.Player.Serial)
                    else:
                        API.TargetSelf()

                startTime = time.time()

                skill = API.GetSkill(schoolName).Value
                skillLabel.Text = truncateDecimal(skill, 1)

                regenMana(manaCost)
                checkIfGearBroken(label, skillLabel, spellLabel, runningLabel)

                regenTimer = time.time() - startTime

                if regenTimer < totalPause:
                    API.Pause(totalPause - regenTimer)

                break

    label.Hue = skillLabel.Hue = 996

def showTrainingGump():
    height = 100 + 40 * len(schoolKeys)
    width = 300
    gump = API.CreateGump(True, True)
    gump.SetWidth(width)
    gump.SetHeight(height)
    gump.CenterXInViewPort()
    gump.CenterYInViewPort()

    def addBorder(x, y, w, h):
        b = API.CreateGumpColorBox(1, "#a86b32")
        b.SetX(x); b.SetY(y); b.SetWidth(w); b.SetHeight(h)
        gump.Add(b)

    addBorder(-5, -5, width, 5)                   # Top
    addBorder(-5, height - 10, width, 5)          # Bottom
    addBorder(-5, -5, 5, height)                  # Left
    addBorder(width - 10, -5, 5, height)          # Right

    bg = API.CreateGumpColorBox(0.75, "#000000")
    bg.SetWidth(width - 10)
    bg.SetHeight(height - 10)
    gump.Add(bg)

    label = API.CreateGumpLabel("Select Spell School & Target Skill:")
    label.SetX(10); label.SetY(10)
    gump.Add(label)

    schoolInputs, y = [], 40
    for school in schoolKeys:
        lbl = API.CreateGumpLabel(school)
        lbl.SetX(10); lbl.SetY(y)
        gump.Add(lbl)

        textBox = API.CreateGumpTextBox("0", 60, 24, False)
        textBox.SetX(100); textBox.SetY(y)
        gump.Add(textBox)

        skillLbl = API.CreateGumpLabel(truncateDecimal(API.GetSkill(school).Value, 1))
        skillLbl.SetX(170); skillLbl.SetY(y)
        gump.Add(skillLbl)

        schoolInputs.append((school, textBox, lbl, skillLbl))
        y += 40

    startBtn = API.CreateGumpButton("", 996, 9722, 9721, 9721)
    startBtn.SetX(10); startBtn.SetY(y)
    gump.Add(startBtn)

    startLabel = API.CreateGumpLabel("Start")
    startLabel.SetX(40); startLabel.SetY(y)
    gump.Add(startLabel)

    spellLabel = API.CreateGumpLabel("")
    spellLabel.SetX(170); spellLabel.SetY(y)
    gump.Add(spellLabel)

    API.AddGump(gump)

    while True:
        API.Pause(0.1)
        if startBtn.IsClicked:
            startBtn.SetWidth(0); startBtn.SetHeight(0)
            startLabel.Text = "Running"; startLabel.Hue = 88

            API.ClearRightHand(); API.ClearLeftHand()

            for school, box, lbl, skillLbl in schoolInputs:
                try:
                    val = float(box.Text)
                    if val < 0 or val > API.GetSkill(school).Cap:
                        API.SysMsg("Invalid inputs")
                        return
                    if val and school == "Chivalry" and not (findItemWithProp("One-handed Weapon") or findItemWithProp("Two-handed Weapon")):
                        API.SysMsg("Missing weapon for Chivalry")
                        return
                    if val and school == "Spellweaving":
                        if not any("Spell Channeling" in API.ItemNameAndProps(i.Serial).split("\n") for i in API.ItemsInContainer(API.Backpack)):
                            API.SysMsg("Missing Spell Channeling weapon for Spellweaving")
                            return
                except:
                    return

            for school, box, lbl, skillLbl in schoolInputs:
                    val = float(box.Text)
                    if val != 0:
                        trainSchool(school, val, lbl, skillLbl, spellLabel, startLabel)
            return

showTrainingGump()
