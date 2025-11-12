import math
import importlib
import time
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Magic
import Util
import Math

importlib.reload(Magic)
importlib.reload(Util)
importlib.reload(Math)

from Magic import Magic
from Util import Util
from Math import Math


class Caster:
    @staticmethod
    def validate(skillCap, spells):
        spellNames = []
        for spell in spells:
            skill = spell["skill"]
            if skillCap >= skill:
                spellNames.append(spell["spell"])

        magic = Magic()
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
        self.magic = Magic()
        self.spells = []

    def train(self, calculareSkillLabels):
        skillInfo = Util.getSkillInfo(self.skillName)
        while skillInfo["value"] < self.skillCap:
            self._trainer(skillInfo, self.spells)
            skillInfo = Util.getSkillInfo(self.skillName)
            calculareSkillLabels()

    def _trainer(self, skillInfo, spells):
        skillLevel = skillInfo["value"]
        if self.label:
            self.label.Hue = 88
        if self.skillLevelLabel:
            self.skillLevelLabel.Hue = 88
            self.skillLevelLabel.Text = Math.truncateDecimal(skillLevel, 1)

        self.magic.healCure(math.ceil(API.Player.HitsMax / 3) * 2, API.Player.HitsMax - 1)

        castInfo = self._getCastingInfo(skillLevel, spells)
        manaCost, spellName, totalPause, nextSpell = (
            castInfo["manaCost"],
            castInfo["spellName"],
            castInfo["totalPause"],
            castInfo["nextSpell"],
        )

        self._preCast(skillInfo, spellName, nextSpell)
        Magic.regenMana(manaCost)

        startMana = API.Player.Mana
        startTime = time.time()

        self.magic.cast(spellName)
        self._target()

        API.Pause(Magic.getFcrDelay())

        Magic.regenMana(manaCost)
        self._checkIfGearBroken()

        regenDuration = time.time() - startTime
        manaSpent = startMana - API.Player.Mana

        if manaSpent > 0 and regenDuration < totalPause:
            API.Pause(totalPause - regenDuration)

        self._postCast(skillInfo, spellName, nextSpell)

    def _postCast(self, skillInfo, spellName, nextSpell):
        self._transform(skillInfo, spellName, nextSpell)

    def _transform(self, skillInfo, spellName, nextSpell):
        currentSkillLevel = skillInfo["value"]
        nextSpellSkill = None
        if nextSpell:
            nextSpellSkill = nextSpell["skill"]
        if not nextSpell and currentSkillLevel == self.skillCap:
            while API.BuffExists(spellName):
                API.CastSpell(spellName)
        if currentSkillLevel == nextSpellSkill:
            while API.BuffExists(spellName):
                API.CastSpell(spellName)

    def _preCast(self, skillInfo, spellName, nextSpell):
        self._transform(skillInfo, spellName, nextSpell)

    def _target(self):
        raise NotImplementedError("Override this method to implement targeting logic")

    def _getCastingInfo(self, skillLevel, entries):
        for i, entry in enumerate(entries):
            if skillLevel < entry["skill"]:
                spellName = entry["spell"]
                if self.spellLabel:
                    self.spellLabel.Text = spellName

                castTime = Magic.getFcDelay(entry["castingTime"])
                recoverTime = Magic.getFcrDelay()
                totalPause = castTime + recoverTime

                lmc = API.Player.LowerManaCost
                manaCost = math.ceil(entry["manaCost"] * (1 - lmc / 100))

                self._checkIfGearBroken()
                nextSpell = None
                try:
                    if entries[i + 1]:
                        nextSpell = entries[i + 1]
                except:
                    pass

                return {
                    "spellName": spellName,
                    "totalPause": totalPause,
                    "manaCost": manaCost,
                    "nextSpell": nextSpell,
                }

        raise ValueError("No matching spell entry found for current skill level")

    def _checkIfGearBroken(self):
        if Util.checkIfGearBroken():
            if self.label:
                self.label.Hue = 33
            if self.skillLevelLabel:
                self.skillLevelLabel.Hue = 33
            if self.spellLabel:
                self.spellLabel.Text = "Repair your gear!"
                self.spellLabel.Hue = 33
            if self.runningLabel:
                self.runningLabel.Text = "Stopped"
                self.runningLabel.Hue = 33

            API.SysMsg("Repair your gear!", 33)
            API.Stop()
