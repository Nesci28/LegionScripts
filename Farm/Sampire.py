try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass
# API is injected by TazUO at runtime; the import above is IDE-only.
import importlib
import time
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump
import Util
import Math
import Timer
import Magic
import Python

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Timer)
importlib.reload(Magic)
importlib.reload(Python)

from Gump import Gump
from Util import Util
from Math import Math
from Timer import Timer
from Magic import Magic
from Python import Python


class Sampire:
    options = [
        {
            "name": "Vampiric Embrace",
            "isActive": True,
            "checkbox": None,
            "isBuff": True,
        },
        {"name": "Honor", "isActive": True, "checkbox": None, "isBuff": False},
        {"name": "Onslaught", "isActive": True, "checkbox": None, "isBuff": False},
        {"name": "Consecrate Weapon", "isActive": True, "checkbox": None, "isBuff": False},
        {"name": "Lightning Strike", "isActive": False, "checkbox": None, "isBuff": False},
        {"name": "Divine Fury", "isActive": True, "checkbox": None, "isBuff": True},
        {
            "name": "Momentum Strike",
            "isActive": True,
            "checkbox": None,
            "isBuff": False,
        },
        {
            "name": "Whirlwind",
            "isActive": True,
            "checkbox": None,
            "isBuff": False,
        },
        {
            "name": "Double Strike",
            "isActive": True,
            "checkbox": None,
            "isBuff": False,
        },
        {"name": "Enemy Of One", "isActive": False, "checkbox": None, "isBuff": True},
        {"name": "Bandage Heals", "isActive": False, "checkbox": None, "isBuff": False},
        {"name": "Auto Attack", "isActive": True, "checkbox": None, "isBuff": False},
        {"name": "Meditate For Mana", "isActive": True, "checkbox": None, "isBuff": False},
    ]
    curses = [
        "Blood Oath",
    ]

    def __init__(self):
        self.magic = Magic()
        self._running = True

        self.gump = None

        self.lightningStrikeMana = 10
        self.whirlwindMana = 15
        self.doubleStrikeMana = 30
        self.vampiricEmbraceMana = 25
        self.momentumStrikeMana = 10
        self.onslaughtMana = 20
        self._settings()

        self.currentHonorSerial = None
        self.currentAggros = []
        self.currentEnemy = None
        self._lastLightningStrikeCastAttemptAt = 0

    def main(self):
        try:
            Util.openContainer(API.Backpack)
            self._showGump()
        except Exception as e:
            API.SysMsg(f"Sampire e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            self.gump.tick()
            if not self.gump:
                return False
            self.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True

    def run(self):
        while True:
            if not self.tick():
                return

            if hasattr(API.Player, "IsGhost") and API.Player.IsGhost:
                API.Pause(1)
                continue
            self._checkBuffs()
            self._deCurse()
            self._aggro()
            self._honor()
            self._attack()
            self._checkCooldowns()
            API.Pause(0.05)

    def _checkCooldowns(self):
        if API.InJournalAny(["You deliver an onslaught of sword strikes!"]):
            Timer.create(3, "Onslaught", 43)
            API.ClearJournal()

    def _attack(self):
        autoAttack = Python.find("Auto Attack", self.options, "name")
        lightningStrikeOption = Python.find("Lightning Strike", self.options, "name")
        lightningStrikeHandled = False
        if lightningStrikeOption["isActive"]:
            lightningStrikeHandled = self._handleLightningStrike(lightningStrikeOption)

        if not autoAttack["isActive"]:
            self.currentEnemy = None
            return

        enemies = Util.scanEnemies(2)
        enemiesCount = len(enemies)
        weaponName = Util.getWeaponName()
        if enemiesCount == 0:
            self.currentEnemy = None
            return

        closestEnemy = enemies[0]

        found = False
        if self.currentEnemy:
            for enemy in enemies:
                if enemy.Serial == self.currentEnemy:
                    found = True
                    break
        if not found:
            self.currentEnemy = closestEnemy.Serial
            API.Attack(self.currentEnemy)

        if lightningStrikeHandled:
            return

        onslaughtOption = Python.find("Onslaught", self.options, "name")
        consecrateWeaponOption = Python.find("Consecrate Weapon", self.options, "name")
        doubleStrikeOption = Python.find("Double Strike", self.options, "name")
        momentumStrikeOption = Python.find("Momentum Strike", self.options, "name")
        whirlwindOption = Python.find("Whirlwind", self.options, "name")

        if (
            onslaughtOption["isActive"]
            and not Timer.exists(4, "Onslaught", 43)
            and self._castWithManaCost("Onslaught", self.onslaughtMana)
        ):
            Timer.create(4, "Onslaught", 43)

        if consecrateWeaponOption["isActive"] and not Timer.exists(8, "Consecrate Weapon", 43):
            if self._cast("Consecrate Weapon"):
                Timer.create(8, "Consecrate Weapon", 43)

        if (
            doubleStrikeOption["isActive"]
            and enemiesCount == 1
            and self._hasManaForManaCost(self.doubleStrikeMana)
        ):
            if "double axe" in weaponName.lower() and not API.PrimaryAbilityActive():
                API.ToggleAbility("primary")
        if (
            momentumStrikeOption["isActive"]
            and enemiesCount == 2
            and self._hasManaForManaCost(self.momentumStrikeMana)
            and not API.BuffExists("Momentum Strike")
        ):
            self._cast("Momentum Strike")
        if (
            whirlwindOption["isActive"]
            and enemiesCount > 2
            and self._hasManaForManaCost(self.whirlwindMana)
        ):
            if "double axe" in weaponName.lower() and not API.SecondaryAbilityActive():
                API.ToggleAbility("secondary")

    def _honor(self):
        honorOption = Python.find("Honor", self.options, "name")
        if not honorOption["isActive"]:
            return

        enemies = Util.scanEnemies(8)
        if self.currentHonorSerial:
            for enemy in enemies:
                if enemy.Serial == self.currentHonorSerial:
                    return
            self.currentHonorSerial = None
        for enemy in enemies:
            if enemy.Hits == enemy.HitsMax:
                API.Virtue("honor")
                API.WaitForTarget()
                API.Target(enemy.Serial)
                self.currentHonorSerial = enemy.Serial

    def _aggro(self):
        autoAttack = Python.find("Auto Attack", self.options, "name")
        if not autoAttack["isActive"]:
            return
        enemies = Util.scanEnemies(12)
        currentEnemySerials = {enemy.Serial for enemy in enemies}
        for enemy in enemies:
            if enemy.Serial not in self.currentAggros:
                API.Attack(enemy.Serial)
                API.Pause(0.1)
                self.currentAggros.append(enemy.Serial)
        self.currentAggros = [
            serial for serial in self.currentAggros if serial in currentEnemySerials
        ]

    def _deCurse(self):
        for curse in self.curses:
            if API.BuffExists(curse):
                if self._cast("Remove Curse") and API.WaitForTarget():
                    API.TargetSelf()

    def _checkBuffs(self):
        for option in self.options:
            if (
                option["isActive"]
                and option["isBuff"]
                and not API.BuffExists(option["name"])
            ):
                self._cast(option["name"])

    def _cast(self, spellName, maxTries=3):
        if self._canMeditateForMana():
            manaNeeded = self._getManaNeededForSpell(spellName)
            if manaNeeded and API.Player.ManaMax < manaNeeded:
                return False
            return self.magic.cast(spellName, maxTries)

        if not self._hasManaForSpell(spellName):
            return False

        API.CastSpell(spellName)
        return True

    def _castWithManaCost(self, spellName, manaCost):
        if not self._hasManaForManaCost(manaCost):
            return False
        API.CastSpell(spellName)
        return True

    def _canMeditateForMana(self):
        meditateOption = Python.find("Meditate For Mana", self.options, "name")
        if not meditateOption:
            return True
        return meditateOption["isActive"]

    def _hasManaForSpell(self, spellName):
        manaNeeded = self._getManaNeededForSpell(spellName)
        if not manaNeeded:
            return True
        return self._hasManaForManaCost(manaNeeded)

    def _getManaNeededForSpell(self, spellName):
        spellDef = self.magic.findSpellDef(spellName)
        if not spellDef:
            return None
        return self.magic.getManaCost(spellDef["manaCost"])

    def _hasManaForManaCost(self, manaCost):
        return API.Player.Mana >= max(1, manaCost)

    def _handleLightningStrike(self, lightningStrikeOption):
        if not lightningStrikeOption["isActive"]:
            return False

        lightningStrikeBuffExists = API.BuffExists("Lightning Strike")

        if not self._hasManaForManaCost(self.lightningStrikeMana):
            return True

        if lightningStrikeBuffExists:
            return True

        now = time.time()
        if now - self._lastLightningStrikeCastAttemptAt < 0.25:
            return True

        self._lastLightningStrikeCastAttemptAt = now
        if self._castWithManaCost("Lightning Strike", self.lightningStrikeMana):
            API.Pause(0.05)

        return True

    def _settings(self):
        lowerManaCost = API.Player.LowerManaCost
        bushido = Util.getSkillInfo("Bushido")["value"]
        swordsmanship = Util.getSkillInfo("Swordsmanship")["value"]
        parrying = Util.getSkillInfo("Parrying")["value"]
        totalSkill = (bushido + swordsmanship + parrying)
        specialManaBonus = 0
        if totalSkill >= 200 and totalSkill <= 299:
            specialManaBonus = 5
        if totalSkill >= 300:
            specialManaBonus = 10
        self.whirlwindMana = (
            self.whirlwindMana
            - specialManaBonus
            - (self.whirlwindMana * (lowerManaCost / 100))
        )
        self.doubleStrikeMana = (
            self.doubleStrikeMana
            - specialManaBonus
            - (self.doubleStrikeMana * (lowerManaCost / 100))
        )
        self.vampiricEmbraceMana = self.vampiricEmbraceMana - (
            self.vampiricEmbraceMana * (lowerManaCost / 100)
        )
        self.momentumStrikeMana = self.momentumStrikeMana - (
            self.momentumStrikeMana * (lowerManaCost / 100)
        )
        self.onslaughtMana = self.onslaughtMana - (
            self.onslaughtMana * (lowerManaCost / 100)
        )
        self.lightningStrikeMana = self.lightningStrikeMana - (
            self.lightningStrikeMana * (lowerManaCost / 100)
        )

    def _showGump(self):
        width, height = 210, 1 + 30 + (25 * len(self.options)) + 35
        g = Gump(width, height, self._onClose)
        self.gump = g
        y = 1
        g.addLabel("Sampire assistant", 12, y, 191)
        y += 30

        def toggleOption(option):
            option["isActive"] = not option["isActive"]

        for i, option in enumerate(self.options):
            label = option["name"].capitalize()
            checkbox = g.addCheckbox(
                label,
                20,
                y,
                option["isActive"],
                lambda option=option: toggleOption(option),
            )
            self.options[i]["checkbox"] = checkbox
            y += 25
        self.gump.create()

    def _isRunning(self):
        return self._running

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            for subGump in self.gump.subGumps:
                subGump.destroy()
            self.gump.destroy()
            self.gump = None
        API.Stop()


qt = Sampire()
qt.main()
while qt._isRunning():
    qt.tick()
    qt.run()
    API.Pause(0.1)
