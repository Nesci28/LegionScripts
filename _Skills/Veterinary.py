import importlib
import os
import time
import traceback
from decimal import Decimal
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util
import Math
import Timer

importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Timer)

Util = Util.Util
Math = Math.Math
Timer = Timer.Timer


class Veterinary:
    skillName = "Veterinary"
    bandageId = 0x0E21
    bandageHue = 0
    bandageTimerText = "Veterinary Bandage"
    bandageTimerHue = 68
    bandageRestockAmount = 100
    restockLogPath = "_Logs/VeterinaryBandage.log"
    resourceContainerSharedVar = "SKILL_TRAINER_RESOURCE_CONTAINER_SERIAL"
    petScanInterval = 3

    def __init__(
        self,
        skillCap=120,
        label=None,
        skillLevelLabel=None,
        setStatus=None,
        forcedSkillValue=None,
    ):
        self.skillCap = Decimal(str(skillCap))
        self.forcedSkillValue = (
            Decimal(str(forcedSkillValue)) if forcedSkillValue is not None else None
        )
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.setStatus = setStatus

        self._running = True
        self._petSerial = None
        self._deadPetSerial = None
        self._nextCastAt = 0
        self._resourceContainerSerial = self._getSharedVar(self.resourceContainerSharedVar)
        self._petPrompted = False
        self._deadPetPrompted = False
        self._lastPetScanAt = 0
        self._lastDeadPetScanAt = 0
        self._lastStatus = None
        self._lastDebug = {}
        self._lastPetScan = "not scanned"

        API.SetSkillLock(self.skillName, "up")
        self._debug(
            f"loaded from _Skills/Veterinary.py, cap={self.skillCap}, forcedSkillValue={self.forcedSkillValue}"
        )

    @classmethod
    def validate(cls, skillCap=None):
        try:
            if API.GetSharedVar(cls.resourceContainerSharedVar):
                return []
        except Exception:
            pass
        return ["Veterinary - Select the global resource container."]

    def main(self):
        try:
            self._status("Veterinary trainer ready.")
        except Exception as e:
            API.SysMsg(f"Veterinary error: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def train(self, calculateSkillLabels=None):
        self._debug("train() entered")
        while self._running and self._skillValue() < self.skillCap:
            self.trainOnce()
            if calculateSkillLabels:
                calculateSkillLabels()
            API.Pause(0.25)

    def trainOnce(self):
        if not self._running:
            return False

        skillValue = self._skillValue()
        self._debug(f"tick skill={skillValue} cap={self.skillCap}", "tick", 2)

        if skillValue >= self.skillCap:
            self._status("Veterinary target reached.")
            return True

        if not self._getBandage():
            self._status("No clean bandages available; waiting before training.")
            return False

        if self._stopPetIfAttackingMe():
            return False

        if skillValue < Decimal("60"):
            return self._trainFireball(skillValue)
        if skillValue < Decimal("80"):
            return self._trainPoison(skillValue)
        return self._trainGhost(skillValue)

    def tick(self):
        return self._running

    def run(self):
        return self.trainOnce()

    def _stopPetIfAttackingMe(self):
        pet = self._findSavedPet(self._petSerial)
        if not pet or getattr(pet, "IsDead", False):
            return False

        if not self._petAttackingPlayer(pet):
            return False

        self._status("Pet is attacking you; sending all stop.", 33)
        self._debug(f"all stop: {self._mobileSummary(pet)}", "pet-all-stop", 1, 33)
        API.Msg("All stop")
        API.Pause(0.3)
        return True

    def _petAttackingPlayer(self, pet):
        playerSerial = getattr(API.Player, "Serial", API.Player)
        for attr in (
            "TargetSerial",
            "Combatant",
            "AttackTarget",
            "CurrentTarget",
            "LastTargetSerial",
        ):
            target = getattr(pet, attr, None)
            if self._sameSerial(target, playerSerial):
                return True

        return bool(getattr(pet, "InWarMode", False))

    def _sameSerial(self, left, right):
        leftSerial = getattr(left, "Serial", left)
        rightSerial = getattr(right, "Serial", right)
        try:
            return int(leftSerial) == int(rightSerial)
        except Exception:
            return leftSerial == rightSerial

    def _trainFireball(self, skillValue):
        pet = self._getLivePet()
        if not pet:
            return False

        self._debug(f"<60 live pet: {self._mobileSummary(pet)}", "live-pet", 2)
        if self._needsBandage(pet):
            return self._bandage(pet, skillValue, "Healing pet with Veterinary.")

        return self._cast("Fireball", pet)

    def _trainPoison(self, skillValue):
        pet = self._getLivePet()
        if not pet:
            return False

        self._debug(f"60-80 live pet: {self._mobileSummary(pet)}", "live-pet", 2)
        if getattr(pet, "IsPoisoned", False):
            return self._bandage(pet, skillValue, "Curing poisoned pet with Veterinary.")

        return self._cast("Poison", pet)

    def _trainGhost(self, skillValue):
        pet = self._getDeadPet()
        if not pet:
            return False

        self._debug(f"80+ ghost pet: {self._mobileSummary(pet)}", "dead-pet", 2)
        return self._bandage(pet, skillValue, "Resurrecting ghost pet with Veterinary.")

    def _getLivePet(self):
        pet = self._findSavedPet(self._petSerial)
        if pet and not getattr(pet, "IsDead", False):
            return pet

        if self._petSerial:
            self._status("Waiting for selected pet to be nearby.", 48)
            self._followPetSerial(self._petSerial)
            self._followPet()
            return None

        now = time.time()
        if now - self._lastPetScanAt >= self.petScanInterval:
            self._lastPetScanAt = now
            pet = self._findAutoHealPet()
            if pet:
                self._petSerial = pet.Serial
                self._debug(f"selected live pet {self._mobileSummary(pet)}")
                try:
                    API.HeadMsg(f"Pet Located: {pet.Name}", pet.Serial)
                except Exception:
                    pass
                return pet

        if not self._petPrompted:
            self._petPrompted = True
            self._status(f"No live pet found. AutoHeal scan: {self._lastPetScan}. Target your pet.", 33)
            return self._requestPet(dead=False)

        self._status(f"Waiting for selected pet. AutoHeal scan: {self._lastPetScan}.", 48)
        return None

    def _findAutoHealPet(self):
        pets = []
        scanned = 0

        try:
            for mob in API.GetAllMobiles():
                scanned += 1
                if mob.IsRenamable and not mob.IsHuman and not getattr(mob, "IsDead", False):
                    pets.append(mob)
        except Exception as e:
            self._lastPetScan = f"error after {scanned} mobiles: {e}"
            self._debug(f"AutoHeal pet scan failed: {self._lastPetScan}", "pet-scan-error", 2, 33)
            return None

        self._lastPetScan = f"scanned={scanned}, live={len(pets)}"
        self._debug(f"AutoHeal pet scan {self._lastPetScan}", "pet-scan", 2)
        return self._nearest(pets)

    def _getDeadPet(self):
        pet = self._findSavedPet(self._deadPetSerial)
        if pet and getattr(pet, "IsDead", False):
            return pet

        if self._deadPetSerial:
            self._status("Waiting for selected ghost/dead pet to be nearby.", 48)
            self._followPetSerial(self._deadPetSerial)
            self._followPet()
            return None

        now = time.time()
        if now - self._lastDeadPetScanAt < self.petScanInterval:
            self._status("Waiting for ghost/dead pet scan.", 48)
            return None
        self._lastDeadPetScanAt = now

        deadPets = []
        try:
            for mob in API.GetAllMobiles():
                if getattr(mob, "IsDead", False) and not getattr(mob, "IsHuman", False):
                    deadPets.append(mob)
        except Exception as e:
            self._debug(f"dead pet scan failed: {e}", "dead-scan-error", 2, 33)

        pet = self._nearest(deadPets)
        if pet:
            self._deadPetSerial = pet.Serial
            return pet

        if not self._deadPetPrompted:
            self._deadPetPrompted = True
            self._status("80+ Veterinary: target a ghost/dead pet.", 48)
            return self._requestPet(dead=True)

        self._status("Waiting for selected ghost/dead pet.", 48)
        return None

    def _findSavedPet(self, serial):
        if not serial:
            return None
        return API.FindMobile(serial)

    def _requestPet(self, dead=False):
        prompt = "Target your ghost/dead pet." if dead else "Target your live pet."
        self._status(prompt, 48)

        serial = API.RequestTarget(5)
        if not serial:
            return False

        pet = API.FindMobile(serial)
        if not pet:
            self._status("Target was not a mobile.", 33)
            return False

        if dead:
            self._deadPetSerial = serial
            self._deadPetPrompted = True
        else:
            self._petSerial = serial
            self._petPrompted = True
        self._debug(f"manual pet selected {self._mobileSummary(pet)}")
        return pet

    def _cast(self, spellName, pet):
        now = time.time()
        if now < self._nextCastAt:
            self._status(f"Waiting to cast {spellName}.")
            return False

        distance = Math.distanceBetween(API.Player, pet)
        if distance > 10:
            self._status(f"Pet is too far for {spellName}: {distance} tiles.", 33)
            self._followPet(pet)
            return False

        self._status(f"Casting {spellName} on {getattr(pet, 'Name', 'pet')}.")
        self._debug(f"cast {spellName}: {self._mobileSummary(pet)}")

        API.CastSpell(spellName)
        if not API.WaitForTarget():
            self._status(f"No target cursor for {spellName}.", 33)
            self._nextCastAt = time.time() + 1
            return False

        API.Target(pet.Serial)
        self._nextCastAt = time.time() + 2.25
        API.Pause(0.75)
        return True

    def _bandage(self, pet, skillValue, message):
        delay = self._bandageDelay(skillValue)
        if Timer.exists(delay, self.bandageTimerText, self.bandageTimerHue):
            self._status("Waiting for Veterinary bandage timer.")
            return False

        distance = Math.distanceBetween(API.Player, pet)
        if distance > 2:
            self._status(f"Pet must be within 2 tiles for Veterinary. Current distance={distance}.", 33)
            self._followPet(pet)
            return False

        bandage = self._getBandage()
        if not bandage:
            self._status("No bandages available.", 33)
            return False

        self._status(message)
        self._debug(f"bandage {self._serial(bandage.Serial)} -> {self._mobileSummary(pet)}")

        API.UseObject(bandage.Serial)
        if not API.WaitForTarget("Beneficial", 2) and not API.WaitForTarget("any", 0):
            self._status("No bandage target cursor.", 33)
            return False

        API.Target(pet.Serial)
        Timer.create(delay, self.bandageTimerText, self.bandageTimerHue)
        API.Pause(0.5)
        return True

    def _getBandage(self):
        backpackSerial = self._backpackSerial()
        bandage = self._findBandageInContainer(backpackSerial, recursive=False)
        if bandage:
            return bandage

        self._logRestock("Backpack has no clean bandages; attempting restock.")
        if not self._restockBandages():
            return None

        bandage = self._findBandageInContainer(backpackSerial, recursive=False)
        self._logRestock(f"Backpack lookup after restock: {self._itemSummary(bandage)}")
        return bandage

    def _restockBandages(self):
        backpackSerial = self._backpackSerial()
        self._logRestock(
            f"Restock start sharedContainer={self._serial(self._resourceContainerSerial)} "
            f"backpack={self._serial(backpackSerial)} "
            f"backpackBefore={self._countBandages(backpackSerial, recursive=False)}"
        )
        if not self._ensureResourceContainer():
            self._logRestock("Restock aborted: global resource container missing.")
            return False

        container = self._getResourceContainer()
        if not container:
            self._status("Bandage resource container not found. Move near it or open it.", 33)
            self._logRestock(
                f"Restock aborted: FindItem failed for container={self._serial(self._resourceContainerSerial)}"
            )
            return False

        distance = self._distanceTo(container)
        if distance is not None and distance > 2:
            self._status(f"Bandage container is too far: {distance} tiles.", 33)
            self._logRestock(
                f"Restock aborted: container={self._itemSummary(container)} distance={distance}"
            )
            return False

        try:
            API.UseObject(container.Serial)
            API.Pause(0.3)
            self._logRestock(f"Opened resource container: {self._itemSummary(container)}")
        except Exception:
            self._logRestock(f"UseObject failed for resource container: {traceback.format_exc()}")

        containerBefore = self._countBandages(container.Serial, recursive=True)
        backpackBefore = self._countBandages(backpackSerial, recursive=False)
        self._logRestock(
            f"Counts before move: backpack={backpackBefore} container={containerBefore}"
        )

        bandage = self._findBandageInContainer(container.Serial, recursive=True)
        if not bandage:
            self._status("No bandages found in resource container.", 33)
            self._logRestock(
                f"Restock aborted: no bandage graphic={hex(self.bandageId)} hue={self.bandageHue} "
                f"in container={self._serial(container.Serial)}"
            )
            return False

        amount = min(self.bandageRestockAmount, getattr(bandage, "Amount", self.bandageRestockAmount) or self.bandageRestockAmount)
        self._status(f"Restocking {amount} bandages.")
        confirmed = self._moveBandagesToBackpack(bandage, backpackSerial, backpackBefore, amount)
        backpackAfter = self._countBandages(backpackSerial, recursive=False)
        containerAfter = self._countBandages(container.Serial, recursive=True)
        self._logRestock(
            f"MoveItem end confirmed={confirmed} backpackAfter={backpackAfter} "
            f"containerAfter={containerAfter}"
        )
        return confirmed

    def _ensureResourceContainer(self, prompt=False, force=False):
        self._resourceContainerSerial = self._getSharedVar(self.resourceContainerSharedVar)
        if self._resourceContainerSerial:
            return True
        self._status("Global resource container not selected.", 33)
        return False

    def _getResourceContainer(self):
        if not self._resourceContainerSerial:
            return None

        container = API.FindItem(self._resourceContainerSerial)
        if container:
            return container

        try:
            API.UseObject(self._resourceContainerSerial)
            API.Pause(0.3)
            return API.FindItem(self._resourceContainerSerial)
        except Exception:
            return None

    def _findBandageInContainer(self, containerSerial, recursive=True):
        try:
            bandage = API.FindType(
                self.bandageId, containerSerial, hue=self.bandageHue
            )
            if self._isCleanBandage(bandage):
                return bandage
        except Exception as e:
            self._logRestock(
                f"FindType failed container={self._serial(containerSerial)}: {e}"
            )

        try:
            items = API.ItemsInContainer(containerSerial, recursive) or []
        except Exception as e:
            self._debug(f"bandage container scan failed: {e}", "bandage-container-scan", 2, 33)
            self._logRestock(
                f"ItemsInContainer failed container={self._serial(containerSerial)} "
                f"recursive={recursive}: {e}"
            )
            return None

        for item in items:
            if self._isCleanBandage(item):
                return item
        return None

    def _isCleanBandage(self, item):
        if not item:
            return False
        try:
            graphic = int(getattr(item, "Graphic", -1))
            hue = int(getattr(item, "Hue", -1))
        except Exception:
            return False
        return (
            graphic == self.bandageId
            and hue == self.bandageHue
            and (getattr(item, "Amount", 1) or 0) != 0
        )

    def _countBandages(self, containerSerial, recursive=True):
        try:
            items = API.ItemsInContainer(containerSerial, recursive) or []
        except Exception as e:
            self._logRestock(
                f"Count failed container={self._serial(containerSerial)} "
                f"recursive={recursive}: {e}"
            )
            return None

        total = 0
        for item in items:
            if self._isCleanBandage(item):
                total += getattr(item, "Amount", 1) or 1
        return total

    def _moveBandagesToBackpack(self, bandage, backpackSerial, backpackBefore, amount):
        attempts = [
            (
                "MoveItem(serial,destSerial)",
                lambda: API.MoveItem(bandage.Serial, backpackSerial, amount),
            ),
            (
                "MoveItem(item,destSerial)",
                lambda: API.MoveItem(bandage, backpackSerial, amount),
            ),
            (
                "MoveItem(serial,API.Backpack)",
                lambda: API.MoveItem(bandage.Serial, API.Backpack, amount),
            ),
            (
                "QueueMoveItem(serial,destSerial)",
                lambda: API.QueueMoveItem(bandage.Serial, backpackSerial, amount),
            ),
            (
                "CursorPickDrop(serial,destSerial)",
                lambda: self._moveBandageByCursor(bandage.Serial, backpackSerial, amount),
            ),
        ]

        for method, action in attempts:
            before = self._countBandages(backpackSerial, recursive=False)
            effectiveBefore = before if before is not None else backpackBefore
            self._logRestock(
                f"{method} start source={self._itemSummary(bandage)} "
                f"destination={self._serial(backpackSerial)} amount={amount} "
                f"backpackBefore={effectiveBefore}"
            )
            try:
                action()
            except Exception:
                self._logRestock(f"{method} raised: {traceback.format_exc()}")
                continue

            if self._waitForBandageMove(backpackSerial, effectiveBefore, amount):
                self._logRestock(f"{method} confirmed.")
                return True

            self._logRestock(f"{method} not confirmed.")

        return False

    def _moveBandageByCursor(self, serial, backpackSerial, amount):
        try:
            held = API.GetHeldItem()
            if held:
                self._logRestock(f"Cursor move skipped; held item={self._serial(held)}")
                return
        except Exception:
            pass

        API.PickUpToCursor(serial, amount)
        API.Pause(0.4)
        try:
            held = API.GetHeldItem()
            self._logRestock(f"Cursor held after pickup={self._serial(held)}")
        except Exception:
            pass
        API.DropFromCursor(container=backpackSerial)

    def _waitForBandageMove(self, backpackSerial, backpackBefore, amount, timeout=2.5):
        start = time.time()
        expected = None if backpackBefore is None else backpackBefore + amount
        while time.time() - start < timeout:
            API.Pause(0.1)
            backpackNow = self._countBandages(backpackSerial, recursive=False)
            if expected is not None and backpackNow is not None and backpackNow >= expected:
                self._logRestock(
                    f"Move confirmed backpackNow={backpackNow} expected={expected}"
                )
                return True

        backpackNow = self._countBandages(backpackSerial, recursive=False)
        self._logRestock(
            f"Move not confirmed backpackBefore={backpackBefore} "
            f"amount={amount} backpackNow={backpackNow}"
        )
        return False

    def _logRestock(self, text):
        try:
            path = LegionPath.createPath(self.restockLogPath)
            directory = os.path.dirname(path)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(path, "a", encoding="utf-8") as logFile:
                logFile.write(f"{timestamp} {text}\n")
        except Exception:
            pass

    def _itemSummary(self, item):
        if not item:
            return "None"
        return (
            f"serial={self._serial(getattr(item, 'Serial', None))} "
            f"graphic={self._serial(getattr(item, 'Graphic', None))} "
            f"hue={getattr(item, 'Hue', None)} "
            f"amount={getattr(item, 'Amount', None)} "
            f"container={self._serial(getattr(item, 'Container', None))}"
        )

    def _needsBandage(self, pet):
        if getattr(pet, "IsPoisoned", False):
            return True

        hitsDiff = getattr(pet, "HitsDiff", None)
        if hitsDiff is not None:
            return hitsDiff != 0

        hits = getattr(pet, "Hits", None)
        hitsMax = getattr(pet, "HitsMax", None)
        if hits is None or hitsMax is None:
            return False
        return hits < hitsMax

    def _bandageDelay(self, skillValue):
        return 5.5 if skillValue >= Decimal("80") else 3

    def _followPet(self, pet=None):
        if pet:
            self._followPetSerial(pet.Serial)
        API.Msg("All Follow Me")
        API.Pause(0.2)

    def _followPetSerial(self, serial):
        if not serial:
            return
        try:
            API.AutoFollow(serial)
        except Exception:
            pass

    def _nearest(self, mobiles):
        if not mobiles:
            return None
        mobiles.sort(key=lambda mob: Math.distanceBetween(API.Player, mob))
        return mobiles[0]

    def _distanceTo(self, obj):
        try:
            return Math.distanceBetween(API.Player, obj)
        except Exception:
            return None

    def _skillValue(self):
        if self.forcedSkillValue is not None:
            return self.forcedSkillValue
        return Util.getSkillInfo(self.skillName)["value"]

    def _backpackSerial(self):
        return self._containerSerial(API.Backpack)

    def _containerSerial(self, container):
        return getattr(container, "Serial", container)

    def _getSharedVar(self, name):
        try:
            return API.GetSharedVar(name) or None
        except Exception:
            return None

    def _serial(self, serial):
        if not serial:
            return "None"
        try:
            return hex(int(serial))
        except Exception:
            return str(serial)

    def _mobileSummary(self, mob):
        if not mob:
            return "None"
        return (
            f"name={getattr(mob, 'Name', None)} "
            f"serial={self._serial(getattr(mob, 'Serial', None))} "
            f"dead={getattr(mob, 'IsDead', None)} "
            f"poisoned={getattr(mob, 'IsPoisoned', None)} "
            f"hits={getattr(mob, 'Hits', None)}/{getattr(mob, 'HitsMax', None)} "
            f"hitsDiff={getattr(mob, 'HitsDiff', None)} "
            f"renamable={getattr(mob, 'IsRenamable', None)} "
            f"human={getattr(mob, 'IsHuman', None)} "
            f"distance={Math.distanceBetween(API.Player, mob)}"
        )

    def _debug(self, text, key=None, interval=0, hue=1153):
        now = time.time()
        debugKey = key or text
        if interval and now - self._lastDebug.get(debugKey, 0) < interval:
            return
        self._lastDebug[debugKey] = now

    def _status(self, text, hue=996):
        if text != self._lastStatus:
            self._lastStatus = text
            if self.setStatus:
                self.setStatus(text, hue)

    def _isRunning(self):
        return self._running

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        API.Stop()
