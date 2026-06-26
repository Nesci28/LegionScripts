import importlib

from LegionPath import LegionPath

LegionPath.addSubdirs()

import _Caster
import Math
import Util

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
    def _currentWeapon():
        return API.FindLayer("OneHanded") or API.FindLayer("TwoHanded")

    @staticmethod
    def _findWeapon():
        return (
            Chivalry._currentWeapon()
            or Util.Util.findItemWithProps(["One-handed Weapon"])
            or Util.Util.findItemWithProps(["Two-handed Weapon"])
        )

    @staticmethod
    def validate(skillCap):
        errors = []
        hasSpellValidation = Caster.validate(skillCap, Chivalry.spells)
        if not hasSpellValidation:
            errors.append("Chivalry - Missing spells.")

        hasWeapon = bool(Chivalry._findWeapon())
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
        self.weapon = Chivalry._findWeapon()
        self._ensureWeaponEquipped()

    def _ensureWeaponEquipped(self):
        if not self.weapon:
            return

        currentWeapon = Chivalry._currentWeapon()
        if currentWeapon and currentWeapon.Serial == self.weapon.Serial:
            return

        API.EquipItem(self.weapon.Serial)
        API.Pause(0.25)

    def _preCast(self, skillInfo, spellName, nextSpell):
        super()._preCast(skillInfo, spellName, nextSpell)
        self._ensureWeaponEquipped()

    def _target(self):
        # Chivalry training spells are all no-target spells in this script.
        return
