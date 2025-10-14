import API
import importlib
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
            qt.gump.tick()
            qt.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True

    def run(self):
        while True:
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
        enemies = Util.scanEnemies(2)
        enemiesCount = len(enemies)
        currentMana = API.Player.Mana
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
        
        onslaughtOption = Python.find("Onslaught", self.options, "name")
        consecrateWeaponOption = Python.find("Consecrate Weapon", self.options, "name")
        doubleStrikeOption = Python.find("Double Strike", self.options, "name")
        momentumStrikeOption = Python.find("Momentum Strike", self.options, "name")
        whirlwindOption = Python.find("Whirlwind", self.options, "name")

        if onslaughtOption["isActive"] and not Timer.exists(4, "Onslaught", 43):
            API.CastSpell("Onslaught")
            Timer.create(4, "Onslaught", 43)

        if consecrateWeaponOption["isActive"] and not Timer.exists(8, "Consecrate Weapon", 43):
            self.magic.cast("Consecrate Weapon")
            Timer.create(8, "Consecrate Weapon", 43)
            
        if doubleStrikeOption["isActive"] and enemiesCount == 1 and currentMana >= self.doubleStrikeMana:
            if "double axe" in weaponName.lower() and not API.PrimaryAbilityActive():
                API.ToggleAbility("primary")
        if momentumStrikeOption["isActive"] and enemiesCount == 2 and currentMana >= self.momentumStrikeMana and not API.BuffExists("Momentum Strike"):
            self.magic.cast("Momentum Strike")
        if whirlwindOption["isActive"] and enemiesCount > 2 and currentMana >= self.whirlwindMana:
            if "double axe" in weaponName.lower() and not API.SecondaryAbilityActive():
                API.ToggleAbility("secondary")

    def _honor(self):
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
                self.magic.cast("Remove Curse")
                if API.WaitForTarget():
                    API.TargetSelf()

    def _checkBuffs(self):
        for option in self.options:
            if option["isBuff"] and not API.BuffExists(option["name"]):
                self.magic.cast(option["name"])

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
        for i, option in enumerate(self.options):
            label = option["name"].capitalize()
            checkbox = g.addCheckbox(
                label,
                20,
                y,
                option["isActive"],
                None,
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
