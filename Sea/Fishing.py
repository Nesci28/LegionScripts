import API
import importlib
import time
import os
import json
from collections import OrderedDict
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Debug
import Error
import Util
import Math
import Magic
import Gump
import Peacemaking
import Notification

importlib.reload(Debug)
importlib.reload(Error)
importlib.reload(Error)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Magic)
importlib.reload(Gump)
importlib.reload(Peacemaking)
importlib.reload(Notification)

from Debug import debug
from Error import Error
from Util import Util
from Math import Math
from Magic import Magic
from Gump import Gump
from Peacemaking import Peacemaking
from Notification import Notification


class Fishing:
    offsets = [
        (-3, -3),
        (3, -3),
        (3, 3),
        (-3, 3),
    ]
    fishIds = [
        0x09CF,
        0x09CE,
        0x09CC,
        0x09CD,
        0x09CE,
        0x09CC,
        0x4306,
        0x09CD,
        0x44C6,
        0x4303,
        0x09CF,
        0x4302,
        0x44C4,
        0x4307,
        0x44C3,
        0x4306,
        0x44C4,
        0x4302,
        0x44C5,
        0x4307,
        0x4303,
        0x44C6,
        0x09CC,
        0x09CD,
        0x09CE,
    ]
    shoeIds = [0x170F, 0x170D, 0x1711, 0x170C, 0x170E, 0x1712, 0x170B, 0x1710]
    fishSteakIds = [0x097B, 0x097A]

    bigFishIds = [17158, 17159, 17156, 17157]

    def __init__(self):
        self.fishingPoleSerial = self._findItem(0x0DBF)
        self.daggerSerial = self._findItem(5110)
        self.magic = Magic()
        self.lootedCorpseSerials = []
        self._validate()
        self.peacemaking = Peacemaking()
        self.peaceTimer = time.time()
        self._running = True
        self.statLabels = []
        self.lootLabels = []

        self.notification = Notification()
        self.lastNotification = time.time()
        self.notificationInterval = 3600
        
        self.stats = OrderedDict()
        self.stats["cast"] = {"label": "Total Casts", "count": 0, "session": 0}
        self.stats["spot"] = {"label": "Empty Spots", "count": 0, "session": 0}
        self.stats["boots"] = {"label": "Boots Pulled Up", "count": 0, "session": 0}
        self.stats["fish"] = {"label": "Fish Caught", "count": 0, "session": 0}
        self.stats["specialFish"] = {
            "label": "Special Fish Caught",
            "count": 0,
            "session": 0,
        }
        self.stats["seaSerpent"] = {
            "label": "Sea Serpents Caught",
            "count": 0,
            "session": 0,
        }
        self.stats["whitePearl"] = {
            "label": "White Pearls Collected",
            "count": 0,
            "session": 0,
        }
        self.stats["delicateScales"] = {
            "label": "Delicate Scales Gathered",
            "count": 0,
            "session": 0,
        }

        self.loots = OrderedDict()
        self.loots["gold"] = {
            "label": "Gold Looted",
            "count": 0,
            "session": 0,
            "graphic": 3821,
        }
        # self.loots["map"] = {
        #     "label": "Treasure Maps Found",
        #     "count": 0,
        #     "session": 0,
        #     "graphic": 3530,
        # }
        # self.loots["fishingNet"] = {
        #     "label": "Fishing Nets Retrieved",
        #     "count": 0,
        #     "session": 0,
        #     "graphic": 5355,
        # }
        self.loots["sos"] = {
            "label": "SOS Bottles Collected",
            "count": 0,
            "session": 0,
            "graphic": 41740,
        }
        self.loots["normalSos"] = {
            "label": "SOS Discovered",
            "count": 0,
            "session": 0,
            "graphic": 5358,
            "hue": 0,
        }
        self.loots["ancientSos"] = {
            "label": "Ancient SOS Discovered",
            "count": 0,
            "session": 0,
            "graphic": 5358,
            "hue": 1153,
        }

        self.gumpHeight = 100 + 15 * (len(self.stats) + len(self.loots))
        self.gumpWidth = 350
        self.gump = Gump(self.gumpWidth, self.gumpHeight, self._onClose)

        self.offsetIndex = 0
        self.subStep = 0
        self.currentOffset = None

        playerName = Util.getPlayerName()
        self.statsFile = f"{playerName}_fishing_stats.json"
        self._loadStats()

    @debug
    def main(self):
        self._equipFishingPole()
        self._showGump()

    @debug
    def tick(self):
        self._updateStatLabels()
        self._saveStats()
        self._step()

    @debug
    def _loadStats(self):
        saved = {}
        if os.path.exists(self.statsFile):
            with open(self.statsFile, "r") as f:
                saved = json.load(f)
        for key, statData in self.stats.items():
            statData["count"] = saved.get(key, {}).get("count", 0)
        for key, lootData in self.loots.items():
            lootData["count"] = saved.get(key, {}).get("count", 0)
        if not os.path.exists(self.statsFile):
            self._saveStats()

    @debug
    def _saveStats(self):
        data = {}
        for key, val in self.stats.items():
            data[key] = {"count": val["count"]}
        for key, val in self.loots.items():
            data[key] = {"count": val["count"]}
        with open(self.statsFile, "w") as f:
            json.dump(data, f)

    @debug
    def _step(self):
        if self.subStep == 2:
            for _ in range(12):
                API.Msg("forward one")
                API.Pause(2)
            self.offsetIndex = 0
            self.currentOffset = None
            self.subStep = 0
            return

        if self.currentOffset is None or self.subStep == 0:
            if self.offsetIndex >= len(Fishing.offsets):
                self.subStep = 2
                return
            self.currentOffset = Fishing.offsets[self.offsetIndex]
            self.offsetIndex += 1
            self.subStep = 1

        if self.subStep == 1:
            xOffset, yOffset = self.currentOffset
            self._cutAndDropFish()
            actions = self._fish(xOffset, yOffset)

            if "Enemy" in actions:
                self._fightEnemy()
            if "Boots" in actions:
                self._dropBoots()
            if "Fish" in actions:
                self._cutAndDropFish()
            if "Eat" in actions:
                self._eatSpecialFish()
            if "Empty" in actions:
                self.currentOffset = None
                self.subStep = 0
                return

    @debug
    def _showGump(self):
        tabTotalX = self.gumpWidth - 80
        tabSessionX = self.gumpWidth - 160

        x = 10
        y = 10
        self.gump.addLabel("Current", tabSessionX, y)
        self.gump.addLabel("Total", tabTotalX, y)
        y += 15
        self.gump.addLabel("Stats:", x, y, 80)
        y += 15
        for name, statData in self.stats.items():
            self.gump.addLabel(f"{statData['label']}:", x, y)
            countLabel = self.gump.addLabel(str(statData["session"]), tabSessionX, y)
            self.statLabels.append((name, countLabel, "session"))
            countLabel = self.gump.addLabel(str(statData["count"]), tabTotalX, y)
            self.statLabels.append((name, countLabel, "count"))
            y += 15

        y += 5
        self.gump.addLabel("Loot:", x, y, 80)
        y += 15
        for name, lootData in self.loots.items():
            self.gump.addLabel(f"{lootData['label']}:", x, y)
            countLabel = self.gump.addLabel(str(lootData["session"]), tabSessionX, y)
            self.lootLabels.append((name, countLabel, "session"))
            countLabel = self.gump.addLabel(str(lootData["count"]), tabTotalX, y)
            self.lootLabels.append((name, countLabel, "count"))
            y += 15

        self.gump.create()

    @debug
    def _updateStatLabels(self):
        API.SysMsg("UPDATE STAT LABELS")
        for name, countLabel, type in self.statLabels:
            count = self.stats[name][type]
            # countLabel.Text = str(count)
        for name, countLabel, type in self.lootLabels:
            count = self.loots[name][type]
            # countLabel.Text = str(count)
            API.SysMsg("UPDATE STAT LABELS - DONE")

    @debug
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

    @debug
    def _cast(self, spellName, targetSerial=None):
        API.ClearJournal()
        API.CancelTarget()
        retries = 3
        for attempt in range(retries):
            API.CastSpell(spellName)
            API.Pause(0.25)
            if API.InJournal("You have not yet recovered"):
                API.Pause(0.5)
                continue
            if API.InJournal("fizzles."):
                API.SysMsg(f"{spellName} fizzled. Retrying...", 33)
                API.Pause(0.5)
                continue
            if targetSerial:
                if API.WaitForTarget("any", 5):
                    API.Target(targetSerial)
                    API.Pause(0.75)
            return
        API.SysMsg(f"Failed to cast {spellName} after {retries} attempts", 33)

    @debug
    def _fightEnemy(self):
        enemies = Util.scanEnemies()
        if len(enemies) > 0:
            self.gump.setStatus("Fighting...")
        for enemy in enemies:
            self._killEnemy(enemy)
        self._lootCorpses()
        self._autoHeal(0, 0)

    @debug
    def _lootCorpses(self):
        corpses = Util.findCorpses()
        if len(corpses) == 0:
            self.lootedCorpseSerials.clear()
            return
        corpseSerials = []
        for corpse in corpses:
            corpseSerials.append(corpse.Serial)
        self.gump.setStatus("Looting...")
        for corpseSerial in corpseSerials:
            if corpseSerial in self.lootedCorpseSerials:
                continue
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
                        Util.moveItem(item.Serial, API.Backpack)
            self._openSoses()
            self.lootedCorpseSerials.append(corpseSerial)

    @debug
    def _openSoses(self):
        startingSosCount = len(Util.findTypeAll(API.Backpack, 5358, 0))
        startingAncientSosCount = len(Util.findTypeAll(API.Backpack, 5358, 1153))
        for sosBottle in Util.findTypeAll(API.Backpack, 41740):
            API.Pause(0.25)
            Util.useObject(sosBottle.Serial)
            API.Pause(1)
            newSosCount = len(Util.findTypeAll(API.Backpack, 5358, 0))
            if newSosCount > startingSosCount:
                self.loots["normalSos"]["count"] += 1
                self.loots["normalSos"]["session"] += 1
                startingSosCount += 1
            newAncientSosCount = len(Util.findTypeAll(API.Backpack, 5358, 1153))
            if newAncientSosCount > startingAncientSosCount:
                self.loots["ancientSos"]["count"] += 1
                self.loots["ancientSos"]["session"] += 1
                startingAncientSosCount += 1

    @debug
    def _autoHeal(self, offsetGreaterHeal=40, offsetHeal=20):
        while API.BuffExists("Poisoned"):
            self._cast("Cure", API.Player.Serial)
        hpMissing = API.Player.HitsMax - API.Player.Hits
        while hpMissing > offsetHeal:
            if hpMissing >= offsetGreaterHeal:
                self._cast("Greater Heal", API.Player.Serial)
            elif hpMissing >= offsetHeal:
                self._cast("Heal", API.Player.Serial)
            hpMissing = API.Player.HitsMax - API.Player.Hits

    @debug
    def _killEnemy(self, enemy):
        while API.FindMobile(enemy.Serial):
            now = time.time()
            if enemy.InWarMode and now - self.peaceTimer > 6:
                self.peaceTimer = time.time()
                self._peace(enemy)
            self._autoHeal()
            self._cast("Energy Bolt", enemy.Serial)

    @debug
    def _peace(self, enemy):
        if Util.getSkillInfo("Peacemaking")["value"] < 100:
            return
        self.peacemaking.use(enemy.Serial)

    @debug
    def _dropBoots(self):
        goat = self._findGoat()
        for shoeId in Fishing.shoeIds:
            shoes = Util.findTypeAll(API.Backpack, shoeId)
            for shoe in shoes:
                Util.moveItem(shoe.Serial, goat.Serial)

    @debug
    def _eatSpecialFish(self):
        specialFishes = Util.findTypeAll(API.Backpack, 0x0DD6)
        for specialFish in specialFishes:
            API.UseObject(specialFish.Serial)
            API.Pause(1)

    @debug
    def _cutAndDropFish(self):
        weightDiff = API.Player.WeightMax - API.Player.Weight
        if weightDiff > 35:
            return
        for fishId in Fishing.fishIds:
            fishes = Util.findTypeAll(API.Backpack, fishId)
            for fish in fishes:
                Util.useObjectWithTarget(self.daggerSerial)
                API.Target(fish.Serial)
                API.Pause(0.25)
        for fishSteakId in Fishing.fishSteakIds:
            fishSteakWorld = Util.findTypeWorld(fishSteakId)
            fishSteaks = Util.findTypeAll(API.Backpack, fishSteakId)
            for fishSteak in fishSteaks:
                if fishSteakWorld:
                    Util.moveItem(fishSteak.Serial, fishSteakWorld.Serial)
                else:
                    Util.moveItemOffset(fishSteak.Serial, 1, 1)
                    fishSteakWorld = Util.findTypeWorld(fishSteakId)
        for bigFishId in Fishing.bigFishIds:
            bigFishes = Util.findTypeAll(API.Backpack, bigFishId)
            for bigFish in bigFishes:
                Util.moveItemOffset(bigFish.Serial, -1, 1)

    @debug
    def _validate(self):
        hasMagery = Util.getSkillInfo("Magery")["value"] > 0
        if not hasMagery:
            Util.error("Need magery")
        while not API.BuffExists("Protection"):
            self.magic.cast("Protection")
        self._findGoat()

    @debug
    def _findGoat(self):
        pets = API.GetAllMobiles()
        for pet in pets:
            isGoat = pet.Graphic == 209
            distance = Math.distanceBetween(API.Player, pet)
            if isGoat and pet.IsRenamable and not pet.IsHuman and distance < 2:
                API.HeadMsg("Goat Located", pet.Serial)
                return pet
        Util.error("Missing goat")

    @debug
    def _fish(self, xOffset, yOffset):
        self.gump.setStatus("Fishing...")
        API.ClearJournal()
        self._lootCorpses()
        self.stats["cast"]["count"] += 1
        self.stats["cast"]["session"] += 1
        Util.useObjectWithTarget(self.fishingPoleSerial)
        API.TargetLandRel(xOffset, yOffset)
        API.CreateCooldownBar(10, "Fishing...", 88)
        actions = self._scanJournal()
        return actions

    @debug
    def _scanJournal(self):
        while True:
            res = []
            if API.InJournalAny(
                [
                    "Uh oh! That doesn't look like a fish!",
                ]
            ):
                self.stats["seaSerpent"]["count"] += 1
                self.stats["seaSerpent"]["session"] += 1
                res.append("Enemy")
            if API.InJournalAny(
                [
                    "You pull out an item : uncommon shiner",
                    "You pull out an item : brook trout",
                    "You pull out an item : bluegill sunfish",
                    "You pull out an item : smallmouth bass",
                    "You pull out an item : green catfish",
                    "You pull out an item : kokanee salmon",
                    "You pull out an item : walleye",
                    "You pull out an item : rainbow trout",
                    "You pull out an item : pike",
                    "You pull out an item : pumpkinseed sunfish",
                    "You pull out an item : yellow perch",
                    "You pull out an item : redbelly bream",
                    "You pull out an item : bonefish",
                    "You pull out an item : tarpon",
                    "You pull out an item : blue grouper",
                    "You pull out an item : cape cod",
                    "You pull out an item : yellowfin tuna",
                    "You pull out an item : gray snapper",
                    "You pull out an item : red drum",
                    "You pull out an item : shad",
                    "You pull out an item : captain snook",
                    "You pull out an item : mahi-mahi",
                    "You pull out an item : red grouper",
                    "You pull out an item : bonito",
                    "You pull out an item : cobia",
                    "You pull out an item : amberjack",
                    "You pull out an item : haddock",
                    "You pull out an item : bluefish",
                    "You pull out an item : red snook",
                    "You pull out an item : black seabass",
                    "You pull out an item : grim cisco",
                    "You pull out an item : infernal tuna",
                    "You pull out an item : lurker fish",
                    "You pull out an item : orc bass",
                    "You pull out an item : snaggletooth bass",
                    "You pull out an item : tormented pike",
                    "You pull out an item : darkfish",
                    "You pull out an item : drake fish",
                    "Your fishing pole bends as you pull a big fish from the depths!",
                    "Your fishing pole bends as you pull a rare fish from the depths!",
                    "$Your fishing pole bends as you pull(.*)!",
                ]
            ):
                self.stats["fish"]["count"] += 1
                self.stats["fish"]["session"] += 1
                res.append("Fish")
            if API.InJournalAny(
                [
                    "You pull out an item : a mess of small fish",
                ]
            ):
                self.stats["specialFish"]["count"] += 1
                self.stats["specialFish"]["session"] += 1
                res.append("Eat")
            if API.InJournalAny(
                [
                    "You pull out an item : thigh boots",
                    "You pull out an item : shoes",
                    "You pull out an item : boots",
                    "You pull out an item : sandals",
                ]
            ):
                self.stats["boots"]["count"] += 1
                self.stats["boots"]["session"] += 1
                res.append("Boots")
            if API.InJournalAny(
                [
                    "You fish a while, but fail to catch anything",
                ]
            ):
                res.append("Fail")
            if API.InJournalAny(
                [
                    "The fish don't seem to be biting here",
                    "You need to be closer to the water to fish!",
                ]
            ):
                self.stats["spot"]["count"] += 1
                self.stats["spot"]["session"] += 1
                res.append("Empty")
            if API.InJournalAny(["You have found a white pearl!"]):
                self.stats["whitePearl"]["count"] += 1
                self.stats["whitePearl"]["session"] += 1
            if API.InJournalAny(
                [
                    "As you reel in, you notice that there is something odd tangled in the line."
                ]
            ):
                self.stats["delicateScales"]["count"] += 1
                self.stats["delicateScales"]["session"] += 1
            if len(res) > 0:
                self._updateStatLabels()
                return res
            API.Pause(0.5)

    @debug
    def _findItem(self, itemId):
        API.ClearLeftHand()
        API.ClearRightHand()
        API.Pause(1)
        fishingPole = Util.findType(API.Backpack, itemId)
        if not fishingPole:
            API.SysMsg(f"No: {str(itemId)}", 33)
            API.Stop()
        return fishingPole.Serial

    @debug
    def _equipFishingPole(self):
        API.EquipItem(self.fishingPoleSerial)
        API.Pause(0.25)

    @debug
    def _isRunning(self):
        return self._running

    @debug
    def _sendHourlyStats(self):
        lines = ["📊 Fishing Stats (Last Hour)"]
        for key, data in self.stats.items():
            lines.append(f"{data['label']}: {data['session']}")
        lines.append("\n🎁 Loot Collected:")
        for key, data in self.loots.items():
            lines.append(f"{data['label']}: {data['session']}")
        message = "\n".join(lines)
        self.notification.sendNotification(message)
        for data in self.stats.values():
            data["session"] = 0
        for data in self.loots.values():
            data["session"] = 0


fishing = Fishing()
try:
    fishing.main()
    while fishing._isRunning():
        now = time.time()
        fishing.gump.tick()
        fishing.gump.tickSubGumps()
        fishing.tick()
        if now - fishing.lastNotification >= fishing.notificationInterval:
            fishing._sendHourlyStats()
            fishing.lastNotification = now
        API.Pause(0.1)
except BaseException as e:
    Error.logError(e, "Fishing")
    fishing._onClose()
