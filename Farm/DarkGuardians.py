import API
import importlib
import traceback
from collections import OrderedDict
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump
import Util
import Item

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Item)

from Gump import Gump
from Util import Util
from Item import Item


class DarkGuardians:
    RUNEBOOK_SERIAL = 0x468AD8F3
    RUNE_TRASH_CAN_INDEX = 15
    RUNE_DARK_GUARDIANS_INDEX = 12
    TRASH_GRAPHIC = 0x0E41

    def __init__(self):
        self._running = True
        self.gump = None

        self.currentAggros = []
        self.currentEnemy = None

        self.runebookItem = Item(API.FindItem(DarkGuardians.RUNEBOOK_SERIAL))
        self.lootedCorpseSerials = []
        self.loots = OrderedDict()
        self.loots["map"] = {
            "label": "Treasure Maps Found",
            "count": 0,
            "session": 0,
            "graphic": 0x14EB,
        }

    def main(self):
        try:
            self._showGump()
        except Exception as e:
            API.SysMsg(f"DarkGuardians e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            darkGuardians.gump.tick()
            darkGuardians.gump.tickSubGumps()
        return True

    def run(self):
        isGearBroken = Util.checkIfGearBroken()
        if isGearBroken:
            self.runebookItem.recall(DarkGuardians.RUNE_TRASH_CAN_INDEX)
            API.Stop()
        items = self._getItemsCount()
        if items >= 120:
            self._goToOutside()
            self.runebookItem.recall(DarkGuardians.RUNE_TRASH_CAN_INDEX)
            self._trashMaps()
            self.runebookItem.recall(DarkGuardians.RUNE_DARK_GUARDIANS_INDEX)
        self._goToGuardians()
        self._aggro()
        self._attack()
        self._lootCorpses()
        self._goToCorner1()
        self._goToGuardians()
        self._aggro()
        self._attack()
        self._lootCorpses()
        self._goToCorner2()
        self._goToGuardians()
        self._aggro()
        self._attack()
        self._lootCorpses()

    def _trashMaps(self):
        self._updateStatus("Trashing maps")
        trash = API.FindType(DarkGuardians.TRASH_GRAPHIC, 4294967295, 2)
        if not trash:
            API.Stop()
        graphic = self.loots["map"]["graphic"]
        maps = Util.findTypeAll(API.Backpack, graphic)
        for map in maps:
            Util.moveItem(map.Serial, trash.Serial)
            self._updateStatus("Trashing maps")

    def _goToOutside(self):
        self._updateStatus("Leaving room")
        API.Pathfind(350, 15, wait=True)

    def _goToGuardians(self):
        self._updateStatus("Going to the center of the room")
        API.Pathfind(365, 15, wait=True)

    def _goToCorner1(self):
        self._updateStatus("Going to corner 1")
        API.Pathfind(358, 7, wait=True)

    def _goToCorner2(self):
        self._updateStatus("Going to corner 2")
        API.Pathfind(373, 23, wait=True)

    def _aggro(self):
        self._updateStatus("Aggroing mobs")
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

    def _attack(self):
        self._updateStatus("Attacking mobs")
        enemies = Util.scanEnemies(2)
        enemiesCount = len(enemies)
        while enemiesCount > 0:
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
            if enemiesCount <= 2 and not API.BuffExists("Momentum Strike"):
                API.CastSpell("Momentum Strike")
            if enemiesCount > 2 and not API.SecondaryAbilityActive():
                API.ToggleAbility("secondary")
            enemies = Util.scanEnemies(2)
            enemiesCount = len(enemies)
            API.Pause(1)

    def _getItemsCount(self):
        container = API.FindItem(API.Backpack)
        contents = Util.getContents(container)
        items = contents["items"]
        return items

    def _updateStatus(self, currentText):
        items = self._getItemsCount()
        self.gump.setStatus(f"{currentText} - {str(items)}/125")
        return items

    def _lootCorpses(self):
        self._updateStatus("Looting...")
        hasFoundItem = False
        corpses = Util.findCorpses()
        if len(corpses) == 0:
            self.lootedCorpseSerials.clear()
            return
        corpseSerials = []
        for corpse in corpses:
            corpseSerials.append(corpse.Serial)
        for corpseSerial in corpseSerials:
            if corpseSerial in self.lootedCorpseSerials:
                continue
            try:
                corpse = API.FindItem(corpseSerial)
                Util.openContainer(corpse)
                items = Util.itemsInContainer(corpseSerial)
                for item in items:
                    for loot in self.loots:
                        lootId = self.loots[loot]["graphic"]
                        if item.Graphic == lootId:
                            if item.Graphic == 3821:
                                self.loots[loot]["count"] += item.Amount
                                self.loots[loot]["session"] += item.Amount
                            else:
                                self.loots[loot]["count"] += 1
                                self.loots[loot]["session"] += 1
                            hasFoundItem = True
                            Util.moveItem(item.Serial, API.Backpack)
                            self._updateStatus("Looting...")
            except:
                pass
            self.lootedCorpseSerials.append(corpseSerial)
        if hasFoundItem:
            self._updateStatus("Waiting after loot")
            API.Pause(45)

    def _showGump(self):
        width = 500
        height = 32
        g = Gump(width, height, self._onClose)
        self.gump = g
        y = 1

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


darkGuardians = DarkGuardians()
darkGuardians.main()
while darkGuardians._isRunning():
    darkGuardians.tick()
    darkGuardians.run()
    API.Pause(0.1)
