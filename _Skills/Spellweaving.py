import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)

import _Caster
import Util
import Math
import Magic

importlib.reload(_Caster)
from _Caster import Caster

importlib.reload(Util)
importlib.reload(Math)


class Spellweaving(Caster):
    spells = [
        {
            "skill": 20,
            "spell": "Arcane Circle",
            "manaCost": 24,
            "castingTime": 1,
        },
        {
            "skill": 33,
            "spell": "Immolating Weapon",
            "manaCost": 32,
            "castingTime": 1,
        },
        {
            "skill": 52,
            "spell": "Reaper Form",
            "manaCost": 34,
            "castingTime": 2.5,
        },
        {
            "skill": 74,
            "spell": "Essence of Wind",
            "manaCost": 40,
            "castingTime": 3,
        },
        {
            "skill": 90,
            "spell": "Wildfire",
            "manaCost": 50,
            "castingTime": 2.5,
        },
        {
            "skill": 120,
            "spell": "Word of Death",
            "manaCost": 50,
            "castingTime": 3.5,
        },
    ]

    @staticmethod
    def validate(skillCap):
        errors = []
        magic = Magic.Magic()
        API.ClearJournal()
        magic.cast("Arcane Circle")
        hasDoneArcanistQuest = API.InJournalAny(
            [
                "You must have completed the epic arcanist quest to use this ability.",
            ]
        )
        if not hasDoneArcanistQuest:
            errors.append("Spellweaving - You must complete the epic arcanist quest.")
        hasSpellValidation = Caster.validate(skillCap, Spellweaving.spells)
        if not hasSpellValidation:
            errors.append("Spellweaving - Missing spells.")
        hasOneHandedWeapon = bool(Util.Util.findItemWithProps(
            ["One-handed Weapon"]
        ))
        hasTwoHandedWeapon = bool(Util.Util.findItemWithProps(["Two-handed Weapon"]))
        hasWeapon = hasOneHandedWeapon or hasTwoHandedWeapon
        if not hasWeapon:
            errors.append("Spellweaving - Missing weapon.")
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
            "Spellweaving", skillCap, label, skillLevelLabel, spellLabel, runningLabel
        )
        self.spells = Spellweaving.spells

    def _target(self):
        API.TargetSelf()
