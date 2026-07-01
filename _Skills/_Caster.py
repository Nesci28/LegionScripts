from math import ceil
import importlib
import time
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Magic
import Util
import Math
import Timer

importlib.reload(Magic)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Timer)


MAX_BUFF_CLEAR_ATTEMPTS = 2
BUFF_CLEAR_PAUSE_SECONDS = 1.0
GEAR_CHECK_INTERVAL_SECONDS = 10.0
LABEL_UPDATE_INTERVAL_SECONDS = 1.0


class Caster:
    @staticmethod
    def validate(skillCap, spells):
        spellNames = []
        for spell in spells:
            if skillCap >= spell["skill"]:
                spellNames.append(spell["spell"])

        magic = Magic.Magic()
        for spellName in spellNames:
            hasSpell = magic.hasSpell(spellName)
            if not hasSpell:
                return False
        return True

    def __init__(
        self,
        skillName,
        skillCap=None,
        label=None,
        skillLevelLabel=None,
        spellLabel=None,
        runningLabel=None,
    ):
        self.skillName = skillName
        self.skillCap = skillCap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.spellLabel = spellLabel
        self.runningLabel = runningLabel
        self.magic = Magic.Magic()
        self.spells = []
        self._lastGearCheck = 0

    def train(self, calculareSkillLabels):
        lastLabelUpdate = 0
        skillInfo = Util.Util.getSkillInfo(self.skillName)
        while skillInfo["value"] < self.skillCap:
            self._trainer(skillInfo, self.spells)
            skillInfo = Util.Util.getSkillInfo(self.skillName)
            now = time.time()
            if (
                now - lastLabelUpdate >= LABEL_UPDATE_INTERVAL_SECONDS
                or skillInfo["value"] >= self.skillCap
            ):
                calculareSkillLabels()
                lastLabelUpdate = now

    def _trainer(self, skillInfo, spells):
        skillLevel = skillInfo["value"]
        if self.label:
            self.label.Hue = 88
        if self.skillLevelLabel:
            self.skillLevelLabel.Hue = 88
            self.skillLevelLabel.Text = Math.Math.truncateDecimal(skillLevel, 1)

        if self._needsHealCure():
            self.magic.healCure(
                ceil(API.Player.HitsMax / 3) * 2, API.Player.HitsMax - 1
            )

        castInfo = self._getCastingInfo(skillLevel, spells)
        spellName, castTime, recoverTime, nextSpell = (
            castInfo["spellName"],
            castInfo["castTime"],
            castInfo["recoverTime"],
            castInfo["nextSpell"],
        )

        self._preCast(skillInfo, spellName, nextSpell)

        if castTime > 0:
            Timer.Timer.create(castTime, f"Casting {spellName}", 88)

        castSuccess = self.magic.cast(spellName, castTime=castTime)
        castStart = getattr(self.magic, "_lastCastTime", time.time())
        hasTargetCursor = Util.Util.isTargeting()

        # No-target spells still return success; only target when the server asks.
        if castSuccess and hasTargetCursor:
            self._target()

        if recoverTime > 0:
            Timer.Timer.create(recoverTime, f"Recovering {spellName}", 906)

        recoveryDeadline = castStart + castTime + recoverTime
        self._afterCast(skillInfo, spellName, nextSpell, recoveryDeadline)
        remainingRecovery = recoveryDeadline - time.time()
        if remainingRecovery > 0:
            API.Pause(remainingRecovery)

        self._checkIfGearBrokenThrottled()

        self._postCast(skillInfo, spellName, nextSpell)

    def _postCast(self, skillInfo, spellName, nextSpell):
        self._transform(skillInfo, spellName, nextSpell)

    def _afterCast(self, skillInfo, spellName, nextSpell, recoveryDeadline=None):
        pass

    def _needsHealCure(self):
        return API.BuffExists("Poisoned") or API.Player.Hits < API.Player.HitsMax / 3

    def _transform(self, skillInfo, spellName, nextSpell):
        currentSkillLevel = skillInfo["value"]
        nextSpellSkill = None
        if nextSpell:
            nextSpellSkill = nextSpell["skill"]

        shouldClearBuff = (not nextSpell and currentSkillLevel == self.skillCap) or (
            currentSkillLevel == nextSpellSkill
        )
        if shouldClearBuff:
            self._clearTrainingBuff(spellName)

    def _clearTrainingBuff(self, spellName):
        attempts = 0
        while API.BuffExists(spellName) and attempts < MAX_BUFF_CLEAR_ATTEMPTS:
            API.CastSpell(spellName)
            attempts += 1
            API.Pause(BUFF_CLEAR_PAUSE_SECONDS)

    def _preCast(self, skillInfo, spellName, nextSpell):
        self._transform(skillInfo, spellName, nextSpell)

    def _target(self):
        raise NotImplementedError("Override method implement targeting logic")

    def _getCastingInfo(self, skillLevel, entries):
        for i, entry in enumerate(entries):
            if skillLevel < entry["skill"]:
                spellName = entry["spell"]
                if self.spellLabel:
                    self.spellLabel.Text = spellName

                castTime = Magic.Magic.getFcDelay(entry["castingTime"])
                recoverTime = Magic.Magic.getFcrDelay()

                self._checkIfGearBrokenThrottled()
                nextSpell = None
                if i + 1 < len(entries):
                    nextSpell = entries[i + 1]

                return {
                    "spellName": spellName,
                    "castTime": castTime,
                    "recoverTime": recoverTime,
                    "nextSpell": nextSpell,
                }

        raise ValueError("No matching spell entry found current skill level")

    def _checkIfGearBroken(self):
        if Util.Util.checkIfGearBroken():
            if self.label:
                self.label.Hue = 33
            if self.skillLevelLabel:
                self.skillLevelLabel.Hue = 33
            if self.spellLabel:
                self.spellLabel.Text = "Repair gear!"
                self.spellLabel.Hue = 33
            if self.runningLabel:
                self.runningLabel.Text = "Stopped"
                self.runningLabel.Hue = 33
            API.SysMsg("Repair your gear!", 33)
            API.Stop()

    def _checkIfGearBrokenThrottled(self):
        now = time.time()
        if now - self._lastGearCheck < GEAR_CHECK_INTERVAL_SECONDS:
            return
        self._lastGearCheck = now
        self._checkIfGearBroken()
