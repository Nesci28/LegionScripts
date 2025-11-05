import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster
import Util

importlib.reload(_Caster)
importlib.reload(Util)

from _Caster import Caster
from Util import Util


class Bushido(Caster):
    spells = [
        {
            "skill": 60,
            "spell": "Confidence",
            "manaCost": 10,
            "castingTime": 2,
            "isTransforming": False,
        },
        {
            "skill": 75,
            "spell": "Counter Attack",
            "manaCost": 5,
            "castingTime": 2,
        },
        {
            "skill": 105,
            "spell": "Evasion",
            "manaCost": 10,
            "castingTime": 2,
        },
        {
            "skill": 120,
            "spell": "Momentum Strike",
            "manaCost": 10,
            "castingTime": 2,
        },
    ]
    combatSkills = ["Archery", "Fencing", "Mace Fighting", "Swordsmanship", "Throwing"]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, Bushido.spells)
        if not hasSpellValidation:
            errors.append("Bushido - Missing spells.")
        hasCombatSkillOver75 = False
        combatSkillOver75 = None
        for combatSkill in Bushido.combatSkills:
            values = Util.getSkillInfo(combatSkill)
            if values["value"] > 75:
                hasCombatSkillOver75 = True
                combatSkillOver75 = combatSkill
                break
        if not hasCombatSkillOver75:
            errors.append("Bushido - You need a combat skill over 75.")
        oneHandedProps = ["One-handed Weapon"]
        if combatSkillOver75:
            oneHandedProps.append(combatSkillOver75)
        hasOneHandedWeapon = bool(Util.findItemWithProps(oneHandedProps))
        twoHandedProps = ["Two-handed Weapon"]
        if combatSkillOver75:
            twoHandedProps.append(combatSkillOver75)
        hasTwoHandedWeapon = bool(Util.findItemWithProps(twoHandedProps))
        hasWeapon = hasOneHandedWeapon or hasTwoHandedWeapon
        if not hasWeapon:
            errors.append("Bushido - Missing weapon.")
        return errors

    def __init__(
        self,
        skillCap,
        label=None,
        skillLevelLabel=None,
        spellLabel=None,
        runningLabel=None,
    ):
        super().__init__(
            "Bushido", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = Bushido.spells
        oneHandedWeapon = Util.findItemWithProps(["One-handed Weapon"])
        if oneHandedWeapon:
            self.weapon = oneHandedWeapon
        twoHandedWeapon = Util.findItemWithProps(["Two-handed Weapon"])
        if not oneHandedWeapon and twoHandedWeapon:
            self.weapon = twoHandedWeapon

    def _preCast(self, skillInfo, spellName, nextSpell):
        super()._preCast(skillInfo, spellName, nextSpell)
        isWearingWeapon = Util.isWearingWeapon()
        if not isWearingWeapon:
            API.EquipItem(self.weapon.Serial)

    def _target(self):
        API.TargetSelf()
