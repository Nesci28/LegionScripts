import API
import importlib
import math

from LegionPath import LegionPath

LegionPath.addSubdirs()

import Animal
import Util
import Magic
import Timer
import Math

importlib.reload(Animal)
importlib.reload(Util)
importlib.reload(Magic)
importlib.reload(Timer)
importlib.reload(Math)

from Animal import Animal
from Util import Util
from Magic import Magic
from Timer import Timer
from Math import Math


class AnimalTaming:
    _maxDistance = 18
    _animals = {
        # between 30 - 31
        "cat": Animal("cat", 0x00C9, 0x0000, 30, 39, ["feline"]),
        "chicken": Animal("chicken", 0x00D0, 0x0000, 30, 39, None),
        "mountain goat": Animal("mountain goat", 0x0058, 0x0000, 30, 39, None),
        # between 31.1 - 51.1
        "Cow (brown)": Animal("cow", 0x00E7, 0x0000, 31.1, 51.1, None),
        "Cow (black)": Animal("cow", 0x00D8, 0x0000, 31.1, 51.1, None),
        "Goat": Animal("goat", 0x00D1, 0x0000, 31.1, 51.1, None),
        "Pig": Animal("pig", 0x00CB, 0x0000, 31.1, 51.1, None),
        "Sheep": Animal("sheep", 0x00CF, 0x0000, 31.1, 51.1, None),
        # between 43.1 - 63.1
        "Hind": Animal("hind", 0x00ED, 0x0000, 43.1, 63.1, None),
        "Timber Wolf": Animal("timber wolf", 0x00E1, 0x0000, 43.1, 63.1, ["canine"]),
        # between 49.1 - 69.1
        "Boar": Animal("boar", 0x0122, 0x0000, 49.1, 69.1, None),
        "Desert Ostard": Animal(
            "desert ostard", 0x00D2, 0x0000, 49.1, 69.1, ["ostard"]
        ),
        "forest ostard (green)": Animal(
            "forest ostard", 0x00DB, 0x88A0, 49.1, 69.1, ["ostard"]
        ),
        "forest ostard (red)": Animal(
            "forest ostard", 0x00DB, 0x889D, 49.1, 69.1, ["ostard"]
        ),
        "horse": Animal("horse", 0x00C8, 0x0000, 49.1, 69.1, None),
        "horse2": Animal("horse", 0x00E2, 0x0000, 49.1, 69.1, None),
        "horse3": Animal("horse", 0x00CC, 0x0000, 49.1, 69.1, None),
        "horse4": Animal("horse", 0x00E4, 0x0000, 49.1, 69.1, None),
        # between 55.1 - 75.1
        "Black bear": Animal("black bear", 0x00D3, 0x0000, 55.1, 75.1, ["bear"]),
        "Llama": Animal("llama", 0x00DC, 0x0000, 55.1, 75.1, None),
        "Polar bear": Animal("polar bear", 0x00D5, 0x0000, 55.1, 75.1, ["bear"]),
        "Walrus": Animal("walrus", 0x00DD, 0x0000, 55.1, 75.1, None),
        # between 61.1 - 81.1
        "Brown Bear": Animal("brown bear", 0x00A7, 0x0000, 61.1, 81.1, ["bear"]),
        "cougar": Animal("cougar", 0x003F, 0x0000, 61.1, 81.1, ["feline"]),
        # between 73.1 - 93.1
        "snow leopard": Animal("snow leopard", 0x0040, 0x0000, 73.1, 93.1, ["feline"]),
        "snow leopard2": Animal("snow leopard", 0x0041, 0x0000, 73.1, 93.1, ["feline"]),
        # between 79.1 - 99.1
        "great hart": Animal("great hart", 0x00EA, 0x0000, 79.1, 99.1, None),
    }

    def __init__(self):
        self._running = True
        self._killList = []
        self._magic = Magic()

        self._animalBeingTamed = None
        self._tameHandled = False
        self._isTaming = False
        self._ownPetSerial = None

    def main(self):
        self._checkSkill()

    def tick(self):
        animalSkillInfo = Util.getSkillInfo("Animal Taming")
        if animalSkillInfo["value"] >= 90:
            if not self._ownPetSerial:
                self._ownPetSerial = API.RequestTarget()
            self._magic.regenMana(26)
            API.PreTarget(self._ownPetSerial, "beneficial")
            API.CastSpell("Combat training")
            API.Pause(2)

        else:
            if not self._isTaming:
                self._attackTamed(self._animalBeingTamed)

                animalSkillInfo = Util.getSkillInfo("Animal Taming")
                if animalSkillInfo["value"] == animalSkillInfo["cap"]:
                    API.SysMsg("You've already maxed out Animal Taming!", 65)
                    API.Stop()

                API.ClearJournal()

                # If there is no animal being tamed, try to find an animal to tame
                if self._animalBeingTamed == None:
                    self._animalBeingTamed = self._findAnimalToTame()
                    if self._animalBeingTamed == None:
                        API.Pause(0.5)
                        return
                    else:
                        API.HeadMsg(
                            "Found animal to tame", self._animalBeingTamed.Serial, 90
                        )

                # Check if animal is close enough to tame
                distance = Math.distanceBetween(API.Player, self._animalBeingTamed)
                if distance > self._maxDistance:
                    API.SysMsg("Animal moved too far away, ignoring for now", 1100)
                    self._animalBeingTamed = None
                    return
                elif self._animalBeingTamed != None and distance > 1:
                    self._followMobile(self._animalBeingTamed)
                    animal = API.FindMobile(self._animalBeingTamed.Serial)
                    isBlocked = False
                    lastCoordX = None
                    lastCoordY = None
                    count = 0
                    while animal and Math.distanceBetween(API.Player, self._animalBeingTamed) > 2 and not isBlocked:
                        if count >= 10:
                            isBlocked = True
                        hasMoved = False
                        if lastCoordX != API.Player.X:
                            lastCoordX = API.Player.X
                            hasMoved = True
                        if lastCoordY != API.Player.Y:
                            lastCoordY = API.Player.Y
                            hasMoved = True
                        if not hasMoved:
                            count += 1
                        animal = API.FindMobile(self._animalBeingTamed.Serial)
                        API.Pause(0.1)

                # Tame the animal if a tame is not currently being attempted and enough time has passed since last using Animal Taming
                if not self._isTaming:
                    self._tame()

            if self._isTaming:
                if self._animalBeingTamed and not Timer.exists(13, "Animal Taming"):
                    self._animalBeingTamed = None
                    self._isTaming = False
                    return
                self._followMobile(self._animalBeingTamed)
                self._animalBeingTamed = API.FindMobile(self._animalBeingTamed.Serial)
                if self._animalBeingTamed == None:
                    self._isTaming = False
                if API.InJournalAny(
                    ["It seems to accept you as master.", "That wasn't even challenging."]
                ):
                    Animal.rename(self._animalBeingTamed, "Tamed")
                    Animal.release(self._animalBeingTamed)
                    self._attackTamed(self._animalBeingTamed)
                    self._animalBeingTamed = None
                    self._isTaming = False
                elif API.InJournalAny(
                    [
                        "You fail to tame the creature.",
                        "The animal is too angry to continue taming.",
                        "You must wait a few moments to use another skill.",
                        "That is too far away.",
                        "You are too far away to continue taming.",
                        "Someone else is already taming that creature.",
                    ]
                ):
                    self._animalBeingTamed = None
                    self._isTaming = False

    def _tame(self):
        animal = API.FindMobile(self._animalBeingTamed.Serial)
        if not animal:
            return
        API.CancelTarget()
        API.PreTarget(self._animalBeingTamed.Serial)
        API.UseSkill("Animal Taming")
        Timer.create(13, "Animal Taming")
        self._isTaming = True

    def _pathfindToMobile(animalSerial):
        animal = API.FindMobile(animal.Serial)
        if animal:
            API.PathfindEntity(animal)

    def _followMobile(self, animal):
        animal = API.FindMobile(animal)
        if animal:
            API.AutoFollow(animal.Serial)

    def _attackTamed(self, animal):
        if not animal:
            return
        animal = API.FindMobile(animal.Serial)
        if not animal or animal.IsDead:
            return
        while animal and animal.Hits > 0 and not animal.IsDead:
            API.HeadMsg(f"Killing this animal", animal.Serial, 33)
            API.PreTarget(animal.Serial, "Harmful")
            spell = "Flamestrike"
            self._magic.cast(spell)
            API.Pause(3)
            animal = API.FindMobile(animal.Serial)

    def _getAnimalIDsAtOrOverTamingDifficulty(self):
        animalSkillInfo = Util.getSkillInfo("Animal Taming")["value"]
        animalList = []
        for animal in self._animals:
            if (
                animalSkillInfo >= self._animals[animal].minTamingSkill
                and animalSkillInfo < self._animals[animal].maxTamingSkill
            ):
                animalList.append(self._animals[animal].mobileID)
        return animalList

    def _findAnimalToTame(self):
        tameableAnimals = []
        animalIds = self._getAnimalIDsAtOrOverTamingDifficulty()
        for animalId in animalIds:
            animals = API.GetAllMobiles(
                animalId,
                self._maxDistance,
                [
                    API.Notoriety.Enemy,
                    API.Notoriety.Criminal,
                    API.Notoriety.Gray,
                    # API.Notoriety.Innocent,
                ],
            )
            for animal in animals:
                if self._hasPath(animal):
                    tameableAnimals.append(animal)
        if len(tameableAnimals) > 0:
            finalAnimal = None
            finalDistance = math.inf
            for tameableAnimal in tameableAnimals:
                distance = Math.distanceBetween(API.Player, tameableAnimal)
                if distance < finalDistance:
                    finalAnimal = tameableAnimal
                    finalDistance = distance
            return finalAnimal
        API.SysMsg("No animal")
        return None

    def _hasPath(self, animal):
        return API.GetPath(int(animal.X), int(animal.Y), distance=self._maxDistance + 4)

    def _checkSkill(self):
        animalSkillInfo = Util.getSkillInfo("Animal Taming")
        if animalSkillInfo["value"] < 31:
            API.SysMsg("Buy Taming Skill Up, stopping", 33)
            API.Stop()

    def _isRunning(self):
        return self._running


animalTaming = AnimalTaming()
animalTaming.main()
while animalTaming._isRunning():
    # animalTaming.gump.tick()
    # animalTaming.gump.tickSubGumps()
    animalTaming.tick()
    API.Pause(0.1)
