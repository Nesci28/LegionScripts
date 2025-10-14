import API
import importlib
import sys
import traceback
from decimal import Decimal

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Classes"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)
sys.path.append(
    r".\\TazUO\\LegionScripts\\_Skills"
)

import Gump
import Util
import Math
import Color
import Magic

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Color)
importlib.reload(Magic)


def onMobClicked(s, mob):
    if s.isSayingAllKill:
        API.Msg("All Kill")
        API.WaitForTarget("any", 1)
        API.Target(mob.Serial)


def onMobClickedWordOfDeath(s, mob):
    API.SysMsg("Cast")
    self.magic.cast("Word of Death")
    API.WaitForTarget("any", 10)
    API.Target(mob.Serial)


def toggleAllKillState(s):
    s.isSayingAllKill = not s.isSayingAllKill
    colorHex = Color.Color.defaultGreen
    if not s.isSayingAllKill:
        colorHex = Color.Color.defaultRed
    s.allKillLabel.Hue = Color.Color.convertFromHexToHue(colorHex)


def toggleAutoHealState(s):
    s.isAutoHealing = not s.isAutoHealing
    colorHex = Color.Color.defaultGreen
    if not s.isAutoHealing:
        colorHex = Color.Color.defaultRed
    s.autoHealLabel.Hue = Color.Color.convertFromHexToHue(colorHex)


def handleGroupKill(s):
    enemies = s._scan(15)
    for enemy in enemies:
        API.Attack(enemy.Serial)
        API.Pause(0.1)
    # closeEnemies = s._scan(2)
    # enemiesCount = len(closeEnemies)
    # if enemiesCount > 2:
    #     API.CastSpell("Whirlwind")
    # if enemiesCount > 0 and enemiesCount < 2:
    #     API.CastSpell("Double Strike")


class MobList:
    def __init__(self):
        self._running = True

        self.isSayingAllKill = True
        self.allKillLabel = None
        self.isAutoHealing = True
        self.autoHealLabel = None
        self.mobButtons = []
        self._lastMobSerials = []

        self.useMagery = True
        self.useMageryHighHP = True
        self.useVet = False
        self.bandageSerial = API.Backpack
        self.petSerials = []
        self.petMobiles = []

        self._findMyPets()

        self.magic = Magic.Magic()

    def main(self):
        try:
            Util.Util.openContainer(API.Backpack)
            self._showGump()
            self._run()
        except Exception as e:
            API.SysMsg(f"CasterTrainer e: {e}", 33)
            tb = traceback.format_exc()
            API.SysMsg(tb)
            self._onClose()

    def _isMoving(self):
        return API.Player.IsWalking

    def _mobilePercentHP(self, mob):
        return min(100, int((mob.Hits / 25.0) * 100))

    def _findMyPets(self):
        self.petSerials.clear()
        for mob in API.GetAllMobiles():
            if mob.IsRenamable and not mob.IsHuman:
                self.petSerials.append(mob.Serial)
        if self.petSerials:
            for s in self.petSerials:
                mob = API.FindMobile(s)
                if mob:
                    API.HeadMsg(f"Pet Located: {mob.Name}", s)

    def _rebuildPetList(self):
        self.petMobiles.clear()
        for s in self.petSerials:
            m = API.FindMobile(s)
            if m:
                self.petMobiles.append(m)

    def _castAtTarget(self, spell, level, targetSerial, poisonCheck=0):
        if not API.WaitForTarget("Beneficial", 2):
            return False
        mob = API.FindMobile(targetSerial)
        if not mob or Math.Math.distanceBetween(API.Player, mob) > 10:
            return False
        if poisonCheck == 1 and not mob.IsPoisoned:
            return False
        if poisonCheck == -1 and mob.IsPoisoned:
            return False
        API.Target(targetSerial)
        API.CreateCooldownBar(1, f"{spell} Cooldown", 88)
        return True

    def _curePets(self, healthPercent):
        if (
            self._isMoving()
            or not self.useMagery
            or API.Player.Mana < 15
            or API.BuffExists("Veterinary")
        ):
            return False
        self._rebuildPetList()
        for mob in self.petMobiles:
            if (
                mob.IsPoisoned
                and self._mobilePercentHP(mob) < healthPercent
                and Math.Math.distanceBetween(API.Player, mob) <= 10
            ):
                API.CastSpell("Arch Cure")
                return self._castAtTarget("Arch Cure", 4, mob.Serial, 1)
        return False

    def _healPets(self, healthPercent):
        if (
            self._isMoving()
            or not self.useMagery
            or API.Player.Mana < 15
            or API.BuffExists("Veterinary")
        ):
            return False
        self._rebuildPetList()
        for mob in self.petMobiles:
            isGhost = mob.Hits == 0
            if (
                not isGhost
                and not mob.IsPoisoned
                and self._mobilePercentHP(mob) < healthPercent
                and Math.Math.distanceBetween(API.Player, mob) <= 10
            ):
                API.CastSpell("Greater Heal")
                return self._castAtTarget("Greater Heal", 4, mob.Serial, -1)
        return False

    def _vetPets(self, healthPercent):
        if not self.useVet or API.BuffExists("Veterinary"):
            return False
        self._rebuildPetList()
        for mob in self.petMobiles:
            if Math.Math.distanceBetween(API.Player, mob) > 2:
                continue
            if self._mobilePercentHP(mob) >= healthPercent and not mob.IsPoisoned:
                continue
            bandage = API.FindType(0x0E21, self.bandageSerial)
            if bandage:
                API.UseObject(bandage.Serial)
                if API.WaitForTarget("Beneficial", 2):
                    API.Target(mob.Serial)
                API.Pause(0.25)
                return True
        return False

    def _usePriority(self):
        if self._vetPets(80):
            return True
        if self._curePets(50):
            return True
        if self._healPets(50):
            return True
        if self._curePets(95):
            return True
        if self.useMageryHighHP and self._healPets(90):
            return True
        if self._vetPets(90):
            return True
        return False

    def _run(self):
        while self._running and self.gump and not self.gump.gump.IsDisposed:
            enemies = self._scan(15)
            self._createMobButtons(enemies)
            if self.isAutoHealing and not API.Player.IsDead and self.petSerials:
                self._rebuildPetList()
                if self.petMobiles:
                    self._usePriority()
            API.Pause(1)
        self._onClose()

    def _createMobButtons(self, mobs):
        self._clearMobButtons()
        y = 75

        for mob in mobs:
            name = mob.Name or "(unknown)"
            hits = mob.Hits
            hitsMax = mob.HitsMax or 1
            hpRatio = max(0.0, min(1.0, hits / hitsMax))

            totalWidth = self.gumpWidth - 10
            redWidth = int(totalWidth * hpRatio)
            grayWidth = totalWidth - redWidth
            clickCb = self.gump.onClick(lambda s=self, m=mob: onMobClicked(s, m))
            wordOfDeathCb = self.gump.onClick(
                lambda s=self, m=mob: onMobClickedWordOfDeath(s, m)
            )
            elements = []
            btnFg, bordersFg, labelFg = self.gump.addButtonCustom(
                "",
                0,
                y,
                redWidth,
                45,
                0.25,
                Color.Color.defaultRed,
                clickCb,
                bordersHex=Color.Color.defaultGray,
            )
            elements.extend([btnFg, *bordersFg, labelFg])
            if grayWidth > 0:
                btnBg, bordersBg, labelBg = self.gump.addButtonCustom(
                    "",
                    redWidth,
                    y,
                    grayWidth,
                    45,
                    0.25,
                    Color.Color.defaultLightGray,
                    clickCb,
                    bordersHex=Color.Color.defaultGray,
                )
                elements.extend([btnBg, *bordersBg, labelBg])
            ttfLabel = self.gump.addTtfLabel(
                name,
                0,
                y,
                totalWidth,
                45 - 18 + 9,
                18,
                Color.Color.defaultLightGray,
                "center",
                clickCb,
            )
            if hpRatio <= 0.3:
                wordOfDeathBtn = self.gump.addButton(
                    "", self.gumpWidth - 50, y + 4, "skullWithCrown", wordOfDeathCb
                )
                elements.extend([wordOfDeathBtn])

            elements.extend([ttfLabel])
            self.mobButtons.extend([*elements])
            y += 50

    def _clearMobButtons(self):
        for btn in self.mobButtons:
            btn.Dispose()
        self.mobButtons = []
        # self.gump.setHeight(self.gumpHeight)

    def _scan(self, distance):
        mobs = API.NearestMobiles(
            [
                API.Notoriety.Enemy,
                API.Notoriety.Criminal,
                API.Notoriety.Gray,
                API.Notoriety.Murderer,
            ],
            distance,
        )
        mobs = [m for m in mobs if not m.IsRenamable]
        mobs = sorted(mobs, key=lambda m: Math.Math.distanceBetween(API.Player, m))
        return mobs

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

    def _showGump(self):
        self.gumpHeight = 500
        self.gumpWidth = 175
        gump = Gump.Gump(self.gumpWidth, self.gumpHeight, self._onClose, False)
        self.gump = gump

        self.gump.addTtfLabel(
            "Mob List",
            0,
            0,
            self.gumpWidth,
            22,
            22,
            Color.Color.defaultLightGray,
            "center",
            None,
        )
        if Util.Util.getSkillInfo("Animal Taming")["value"] > 0:
            allKillLabel, _, _ = self.gump.addButtonCustom(
                "All Kill",
                0,
                28,
                int((self.gumpWidth / 2 - 2)),
                35,
                opacity=1,
                backgroundHex=Color.Color.defaultGreen,
                callback=self.gump.onClick(lambda s=self: toggleAllKillState(s)),
                bordersHex=Color.Color.defaultBlack,
            )
            self.allKillLabel = allKillLabel
            self.allKillLabel.Hue = Color.Color.convertFromHexToHue(
                Color.Color.defaultGreen
            )
            autoHealLabel, _, _ = self.gump.addButtonCustom(
                "Auto Heal",
                int((self.gumpWidth / 2 + 2)),
                28,
                int((self.gumpWidth / 2 - 12)),
                35,
                opacity=1,
                backgroundHex=Color.Color.defaultGreen,
                callback=self.gump.onClick(lambda s=self: toggleAutoHealState(s)),
                bordersHex=Color.Color.defaultBlack,
            )
            self.autoHealLabel = autoHealLabel
            self.autoHealLabel.Hue = Color.Color.convertFromHexToHue(
                Color.Color.defaultGreen
            )
        if Util.Util.getSkillInfo("Swordsmanship")["value"] > 0:
            groupKillLabel, _, _ = self.gump.addButtonCustom(
                "Group Kill",
                0,
                28,
                int((self.gumpWidth / 2 - 2)),
                35,
                opacity=1,
                backgroundHex=Color.Color.defaultGreen,
                callback=self.gump.onClick(lambda s=self: handleGroupKill(s)),
                bordersHex=Color.Color.defaultBlack,
            )
            self.groupKillLabel = groupKillLabel
            self.groupKillLabel.Hue = Color.Color.convertFromHexToHue(
                Color.Color.defaultGreen
            )

        gump.create()


MobList().main()
