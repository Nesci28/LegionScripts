import importlib
import sys

sys.path.append(
    r"C:\\Games\\Taz_BleedingEdge\\TazUO-Launcher.win-x64\\TazUO\\LegionScripts\\_Utils"
)

import _Caster
import Util
import Math

importlib.reload(_Caster)
from _Caster import Caster

importlib.reload(Util)
importlib.reload(Math)


class Chivalry(Caster):
    spells = [
        {
            "skill": 45,
            "spell": "Consecrate Weapon",
            "manaCost": 10,
            "castingTime": 0.75,
        },
        {
            "skill": 60,
            "spell": "Divine Fury",
            "manaCost": 15,
            "castingTime": 1.25,
        },
        {
            "skill": 70,
            "spell": "Enemy of One",
            "manaCost": 20,
            "castingTime": 0.75,
        },
        {
            "skill": 90,
            "spell": "Holy Light",
            "manaCost": 10,
            "castingTime": 1,
        },
        {
            "skill": 120,
            "spell": "Noble Sacrifice",
            "manaCost": 20,
            "castingTime": 1.75,
        },
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, Chivalry.spells)
        if not hasSpellValidation:
            errors.append("Chivalry - Missing spells.")
        hasOneHandedWeapon = bool(Util.Util.findItemWithProps(
            ["One-handed Weapon"]
        ))
        hasTwoHandedWeapon = bool(Util.Util.findItemWithProps(["Two-handed Weapon"]))
        hasWeapon = hasOneHandedWeapon or hasTwoHandedWeapon
        if not hasWeapon:
            errors.append("Chivalry - Missing weapon.")
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
            "Chivalry", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = Chivalry.spells
        oneHandedWeapon = Util.Util.findItemWithProps(
            ["One-handed Weapon"]
        )
        if oneHandedWeapon:
            self.weapon = oneHandedWeapon
        twoHandedWeapon = Util.Util.findItemWithProps(["Two-handed Weapon"])
        if not oneHandedWeapon and twoHandedWeapon:
            self.weapon = twoHandedWeapon

    def _preCast(self, skillInfo, spellName, nextSpell):
        super()._preCast(skillInfo, spellName, nextSpell)
        isWearingWeapon = Util.Util.isWearingWeapon()
        if not isWearingWeapon:
            API.EquipItem(self.weapon.Serial)

    def _target(self):
        API.TargetSelf()
