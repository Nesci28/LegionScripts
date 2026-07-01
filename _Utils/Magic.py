import json
import time
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util

importlib.reload(Util)

CAST_POLL_SECONDS = 0.025
CAST_RETRY_PAUSE_SECONDS = 0.05
TARGET_GRACE_SECONDS = 0.05
SERVER_RESPONSE_CHECK_SECONDS = 0.05

with open(LegionPath.createPath("_Jsons/spell-def-magic.json")) as f:
    SPELLS = json.load(f)


class Magic:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Magic, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.recallMethod = self._getRecallMethod()
        self._lastCastTime = 0

    @staticmethod
    def _now():
        return time.time()

    @staticmethod
    def regenMana(manaRequired):
        targetMana = min(manaRequired, API.Player.ManaMax)
        if API.Player.Mana >= targetMana:
            return
        lastAttempt = 0
        while API.Player.Mana < targetMana:
            if not API.BuffExists("Actively Meditating"):
                now = time.time()
                if now - lastAttempt >= 11:
                    API.UseSkill("Meditation")
                    lastAttempt = now
            API.Pause(0.1)

    @staticmethod
    def getFcDelay(castingTime):
        fc = getattr(API.Player, "FasterCasting", 0)
        return max(castingTime - (fc * 0.25), 0)

    @staticmethod
    def getFcrDelay():
        fcr = getattr(API.Player, "FasterCastRecovery", 0)
        return max(1.5 - (fcr * 0.25), 0)

    @staticmethod
    def getManaCost(baseCost):
        lmc = getattr(API.Player, "LowerManaCost", 0)
        return max(1, round(baseCost * (1 - lmc / 100.0)))

    def findSpellDef(self, spellName):
        for spell in SPELLS:
            if spell["name"].lower() == spellName.lower():
                return spell
        return None

    def hasSpell(self, spellName):
        API.ClearJournal()
        API.CastSpell(spellName)
        API.Pause(0.1)
        return not self._checkNoSpell()

    def cast(self, spellName, maxTries=3, castTime=None):
        spellDef = self.findSpellDef(spellName)
        if not spellDef:
            API.SysMsg(f"Invalid spell name: {spellName}", 33)
            return False

        manaNeeded = self.getManaCost(spellDef["manaCost"])
        effectiveCastTime = castTime
        if effectiveCastTime is None:
            effectiveCastTime = self.getFcDelay(spellDef["castTime"])
        effectiveCastTime = max(effectiveCastTime, 0)

        for _ in range(maxTries):
            API.ClearJournal()
            if API.Player.Mana < manaNeeded:
                self.regenMana(manaNeeded)
            castStart = self._now()
            self._lastCastTime = castStart
            API.CastSpell(spellName)
            retry = False

            if spellDef["hasTarget"]:
                while self._now() - castStart < effectiveCastTime:
                    if Util.Util.isTargeting():
                        return True
                    if self._checkNoSpell():
                        API.SysMsg(f"You do not have that spell: {spellName}", 33)
                        return False
                    if self._checkFizzleJournal():
                        API.SysMsg(f"Spell fizzled: {spellName}", 33)
                        retry = True
                        break
                    if self._checkManaFailureJournal():
                        API.SysMsg("Not enough mana, retrying", 33)
                        self.regenMana(manaNeeded)
                        retry = True
                        break
                    if self._checkRecoveredJournal():
                        retry = True
                        break
                    API.Pause(CAST_POLL_SECONDS)
                if Util.Util.isTargeting():
                    return True
                if Util.Util.isTargeting(TARGET_GRACE_SECONDS):
                    return True
                if not retry:
                    API.SysMsg(f"No target cursor for: {spellName}", 33)
                    return False
            elif not retry:
                responseDelay = min(SERVER_RESPONSE_CHECK_SECONDS, effectiveCastTime)
                if responseDelay > 0:
                    API.Pause(responseDelay)
                if self._checkNoSpell():
                    API.SysMsg(f"You do not have that spell: {spellName}", 33)
                    return False
                if self._checkFizzleJournal():
                    API.SysMsg(f"Spell fizzled: {spellName}", 33)
                    retry = True
                elif self._checkManaFailureJournal():
                    API.SysMsg("Not enough mana, retrying", 33)
                    self.regenMana(manaNeeded)
                    retry = True
                elif self._checkRecoveredJournal():
                    retry = True
                if not retry:
                    remainingCast = castStart + effectiveCastTime - self._now()
                    if remainingCast > 0:
                        API.Pause(remainingCast)
                    if self._checkFizzleJournal():
                        API.SysMsg(f"Spell fizzled: {spellName}", 33)
                        retry = True
                    elif self._checkManaFailureJournal():
                        API.SysMsg("Not enough mana, retrying", 33)
                        self.regenMana(manaNeeded)
                        retry = True
                    elif self._checkRecoveredJournal():
                        retry = True
                if retry:
                    API.Pause(CAST_RETRY_PAUSE_SECONDS)
                    continue
                return True
            API.Pause(CAST_RETRY_PAUSE_SECONDS)
        return False

    def healCure(self, greaterHealOffset=20, healOffset=10):
        player = API.Player
        skills = {s: API.GetSkill(s).Value for s in ["Magery", "Chivalry", "Spellweaving", "Spirit Speak"]}
        while API.BuffExists("Poisoned"):
            if skills["Magery"] >= 30 and self.cast("Cure"):
                pass
            elif skills["Chivalry"] >= 30 and self.cast("Remove Curse"):
                pass
            elif skills["Spellweaving"] >= 24 and self.cast("Essence of Wind"):
                pass
            else:
                break
            if API.WaitForTarget("any", 3):
                API.TargetSelf()
        while player.Hits < player.HitsMax - greaterHealOffset:
            if skills["Magery"] >= 50 and self.cast("Greater Heal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Magery"] >= 30 and self.cast("Heal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Chivalry"] >= 30 and self.cast("Close Wounds"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Spirit Speak"] >= 30:
                API.UseSkill("Spirit Speak")
                API.Pause(7)
                continue
            elif skills["Spellweaving"] >= 24 and not API.BuffExists("Gift of Renewal") and self.cast("Gift of Renewal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            else:
                bandage = API.FindType(0x0E21, API.Backpack)
                if bandage:
                    API.UseObject(bandage)
                    if API.WaitForTarget("any", 3):
                        API.TargetSelf()
                        API.Pause(7)
                break
        while player.Hits < player.HitsMax - healOffset:
            if skills["Magery"] >= 30 and self.cast("Heal"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Chivalry"] >= 30 and self.cast("Close Wounds"):
                API.WaitForTarget("any", 3)
                API.TargetSelf()
            elif skills["Spirit Speak"] >= 30:
                API.UseSkill("Spirit Speak")
                API.Pause(7)
            else:
                break

    def recallToLocation(self, index, runebookItem):
        API.UseObject(runebookItem)
        API.Pause(1)
        if not API.HasGump(89):
            API.SysMsg("Runebook's gump did not open", 33)
            return
        API.ClearJournal()
        method = self._getRecallMethod()
        if method == "magery":
            API.ReplyGump(index + 50, 89)
        elif method == "chivalry":
            API.ReplyGump(index + 74, 89)
        else:
            API.SysMsg("No recall method available", 33)
            return
        # Retry if fizzled
        start = self._now()
        while self._now() - start < 4:
            if self._checkFizzleJournal():
                self.recallToLocation(index, runebookItem)
                break
            if not API.HasGump(89):
                break
            API.Pause(0.1)

    def _checkRecoveredJournal(self):
        return API.InJournalAny(["You have not yet recovered from casting a spell."])

    def _checkAlreadyCastingJournal(self):
        return API.InJournalAny([
            "You are already casting a spell.",
            "You must wait before casting another spell.",
        ])

    def _checkNoSpell(self):
        return API.InJournalAny([
            "You do not have that spell!",
            "You have not learned that spell"
        ])

    def _checkFizzleJournal(self):
        return API.InJournalAny([
            "You lost your concentration.",
            "Your spell fizzles.",
            "You can't cast that spell right now.",
            "You fail to cast",
            "Something is blocking the location.",
        ])

    def _checkManaFailureJournal(self):
        return API.InJournalAny(["You don't have enough mana"])

    def _getRecallMethod(self):
        magery = API.GetSkill("Magery").Value
        chivalry = API.GetSkill("Chivalry").Value
        if magery >= 40:
            return "magery"
        elif chivalry >= 40:
            return "chivalry"
        return None

    def _waitForRecovery(self, timeout=2.0):
        start = self._now()
        while self._now() - start < timeout:
            if not self._checkRecoveredJournal():
                return True
            API.Pause(0.05)
        return False
