try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass

# API is injected by TazUO at runtime; the import above is IDE-only.
import importlib
import os
import sys
import traceback
import time
from decimal import Decimal
from LegionPath import LegionPath

LegionPath.addSubdirs()
_IMPORT_ROOT = LegionPath.getLegionPath()
if not os.path.isdir(_IMPORT_ROOT):
    _IMPORT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _IMPORT_ROOT not in sys.path:
    sys.path.insert(0, _IMPORT_ROOT)
for _name in os.listdir(_IMPORT_ROOT):
    _subdir = os.path.join(_IMPORT_ROOT, _name)
    if os.path.isdir(_subdir) and _name.startswith("_") and _subdir not in sys.path:
        sys.path.append(_subdir)

import Gump
import Util
import Math
import Magery
import Mysticism
import Necromancy
import Chivalry
import Spellweaving
import Bushido
import EvaluatingIntelligence
import SpiritSpeak
import Meditation
import Musicianship
import Peacemaking
import ArmsLore as ArmsLoreModule
import ItemIdentification as ItemIdentificationModule
import Ninjitsu
import SkillTrainerAnimalLore
import SkillTrainerLockpicking
import SkillTrainerRemoveTrap
import AnimalTaming
import _Skills.Veterinary as Veterinary
import Tinkering as TinkeringModule
import Tailoring as TailoringModule
import Blacksmithy as BlacksmithyModule
import Cartography as CartographyModule
import BowcraftFletching as BowcraftFletchingModule

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Magery)
importlib.reload(Mysticism)
importlib.reload(Necromancy)
importlib.reload(Chivalry)
importlib.reload(Spellweaving)
importlib.reload(Bushido)
importlib.reload(EvaluatingIntelligence)
importlib.reload(SpiritSpeak)
importlib.reload(Meditation)
importlib.reload(Musicianship)
importlib.reload(Peacemaking)
importlib.reload(ArmsLoreModule)
importlib.reload(ItemIdentificationModule)
importlib.reload(Ninjitsu)
importlib.reload(SkillTrainerAnimalLore)
importlib.reload(SkillTrainerLockpicking)
importlib.reload(SkillTrainerRemoveTrap)
importlib.reload(AnimalTaming)
importlib.reload(Veterinary)
importlib.reload(TinkeringModule)
importlib.reload(TailoringModule)
importlib.reload(BlacksmithyModule)
importlib.reload(CartographyModule)
importlib.reload(BowcraftFletchingModule)

try:
    Veterinary.API = API
    Util.API = API
    TinkeringModule._Crafting.API = API
    TailoringModule._Crafting.API = API
    BlacksmithyModule._Crafting.API = API
    CartographyModule._Crafting.API = API
    BowcraftFletchingModule._Crafting.API = API
    TinkeringModule._Crafting.Crafter.API = API
    TailoringModule._Crafting.Crafter.API = API
    BlacksmithyModule._Crafting.Crafter.API = API
    CartographyModule._Crafting.Crafter.API = API
    BowcraftFletchingModule._Crafting.Crafter.API = API
    TinkeringModule._Crafting.Util.API = API
    TailoringModule._Crafting.Util.API = API
    BlacksmithyModule._Crafting.Util.API = API
    CartographyModule._Crafting.Util.API = API
    BowcraftFletchingModule._Crafting.Util.API = API
except Exception:
    pass

from Gump import Gump
from Util import Util
from Math import Math
from Magery import Magery
from Mysticism import Mysticism
from Necromancy import Necromancy
from Chivalry import Chivalry
from Spellweaving import Spellweaving
from Bushido import Bushido
from EvaluatingIntelligence import EvaluatingIntelligence
from SpiritSpeak import SpiritSpeak
from Meditation import Meditation
from Musicianship import Musicianship
from Peacemaking import Peacemaking
from ArmsLore import ArmsLore as ArmsLoreSkill
from ItemIdentification import ItemIdentification as ItemIdentificationSkill
from Ninjitsu import Ninjitsu
from SkillTrainerAnimalLore import AnimalLore
from SkillTrainerLockpicking import Lockpicking
from SkillTrainerRemoveTrap import RemoveTrap
from Tinkering import Tinkering as TinkeringSkill
from Tailoring import Tailoring as TailoringSkill
from Blacksmithy import Blacksmithy as BlacksmithySkill
from Cartography import Cartography as CartographySkill
from BowcraftFletching import BowcraftFletching as BowcraftFletchingSkill

RESOURCE_CONTAINER_SHARED_VAR = "SKILL_TRAINER_RESOURCE_CONTAINER_SERIAL"
POST_CAST_MOVE_DIRECTIONS = ("north", "south")
POST_CAST_MOVE_PAUSE_SECONDS = 0.25
MAGIC_POST_CAST_MOVE_SKILLS = {
    "Bushido",
    "Chivalry",
    "Evaluating Intelligence",
    "Magery",
    "Meditation",
    "Mysticism",
    "Necromancy",
    "Ninjitsu",
    "Spellweaving",
}


def getResourceContainerSerial():
    try:
        return API.GetSharedVar(RESOURCE_CONTAINER_SHARED_VAR) or None
    except Exception:
        return None


def setResourceContainerSerial(serial):
    API.SetSharedVar(RESOURCE_CONTAINER_SHARED_VAR, serial)


def resourceContainerValidationError(skillName):
    if getResourceContainerSerial():
        return None
    return f"{skillName} - Select the global resource container."


def _skill(name, trainer=None, useStatus=False):
    skill = {
        "skillName": name,
        "trainer": trainer,
        "skillLabel": None,
        "capLabel": None,
    }
    if useStatus:
        skill["useStatus"] = True
    return skill


class _StatusProxy:
    def __init__(self, setStatus):
        self._setStatus = setStatus
        self._text = ""
        self._hue = None

    @property
    def Text(self):
        return self._text

    @Text.setter
    def Text(self, text):
        self._text = text
        if self._setStatus:
            self._setStatus(text, self._hue)

    @property
    def Hue(self):
        return self._hue

    @Hue.setter
    def Hue(self, hue):
        self._hue = hue
        if self._setStatus and self._text:
            self._setStatus(self._text, hue)


class _LabelProxy:
    def __init__(self, label=None):
        self.label = label

    @property
    def Text(self):
        return self.label.Text if self.label else ""

    @Text.setter
    def Text(self, text):
        if self.label:
            self.label.Text = text

    @property
    def Hue(self):
        return self.label.Hue if self.label else None

    @Hue.setter
    def Hue(self, hue):
        if self.label:
            self.label.Hue = hue


class AnimalTamingTrainer:
    skillName = "Animal Taming"

    @staticmethod
    def validate(skillCap=None):
        errors = []
        info = Util.getSkillInfo(AnimalTamingTrainer.skillName)
        if info["value"] < 31:
            errors.append("Animal Taming - Buy skill to 31.0 before using trainer.")
        return errors

    def __init__(self, skillCap, label=None, skillLevelLabel=None, setStatus=None):
        self.skillCap = skillCap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.setStatus = setStatus
        self.trainer = AnimalTaming.AnimalTaming()
        API.SetSkillLock(self.skillName, "up")

    def train(self, calculateSkillLabels=None):
        self.trainer.main()
        while Util.getSkillInfo(self.skillName)["value"] < self.skillCap:
            if self.setStatus:
                self.setStatus(f"Training {self.skillName}...")
            self.trainer.tick()
            if calculateSkillLabels:
                calculateSkillLabels()
            API.Pause(0.1)


class VeterinaryTrainer:
    skillName = "Veterinary"

    @staticmethod
    def validate(skillCap=None):
        return Veterinary.Veterinary.validate(skillCap)

    def __init__(self, skillCap, label=None, skillLevelLabel=None, setStatus=None):
        API.SysMsg(f"SkillTrainer: creating Veterinary trainer to {skillCap}", 1153)
        self.trainer = Veterinary.Veterinary(
            skillCap, label, skillLevelLabel, setStatus
        )

    def train(self, calculateSkillLabels=None):
        API.SysMsg("SkillTrainer: starting Veterinary trainer", 1153)
        self.trainer.train(calculateSkillLabels)


class TrainOnceSkillTrainer:
    skillName = None
    trainerClass = None

    @staticmethod
    def validate(skillCap=None):
        return []

    def __init__(self, skillCap, label=None, skillLevelLabel=None, setStatus=None):
        self.skillCap = skillCap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.setStatus = setStatus
        self.trainer = self.trainerClass(skillCap)

    def train(self, calculateSkillLabels=None):
        while Util.getSkillInfo(self.skillName)["value"] < self.skillCap:
            if self.setStatus:
                self.setStatus(f"Training {self.skillName}...")
            self.trainer.trainOnce()
            if calculateSkillLabels:
                calculateSkillLabels()


class ArmsLoreTrainer(TrainOnceSkillTrainer):
    skillName = "Arms Lore"
    trainerClass = ArmsLoreSkill


class ItemIdentificationTrainer(TrainOnceSkillTrainer):
    skillName = "Item Identification"
    trainerClass = ItemIdentificationSkill


class CraftingSkillTrainer:
    skillName = None
    trainerClass = None

    @classmethod
    def setResourceContainerSerial(cls, serial):
        if cls.trainerClass and hasattr(cls.trainerClass, "setResourceContainerSerial"):
            cls.trainerClass.setResourceContainerSerial(serial)

    @classmethod
    def validate(cls, skillCap=None):
        if not cls.trainerClass:
            return [f"{cls.skillName} - Training not implemented."]
        return cls.trainerClass.validate(skillCap)

    def __init__(self, skillCap, label=None, skillLevelLabel=None, setStatus=None):
        self.trainer = self.trainerClass(skillCap, label, skillLevelLabel, setStatus)

    def _ensureCrafterState(self):
        return None
        if not hasattr(Crafter, "truncateDecimal"):
            Crafter.truncateDecimal = Math.truncateDecimal

        keys = list(Crafter.craftingSkills.keys())
        Crafter.skillNameLabels = []
        Crafter.skillNumberLabels = []
        for key in keys:
            Crafter.skillNameLabels.append(
                _LabelProxy(self.label if key == self.skillName else None)
            )
            Crafter.skillNumberLabels.append(
                _LabelProxy(self.skillLevelLabel if key == self.skillName else None)
            )
        Crafter.itemLabel = _LabelProxy()
        Crafter.statusLabel = _StatusProxy(self.setStatus)

        resourceChestSerial = getResourceContainerSerial()
        resourceChest = API.FindItem(resourceChestSerial) if resourceChestSerial else None
        if resourceChestSerial and not resourceChest:
            try:
                API.UseObject(resourceChestSerial)
                API.Pause(0.3)
                resourceChest = API.FindItem(resourceChestSerial)
            except Exception:
                resourceChest = None
        if not resourceChest:
            raise Exception("Global resource container not selected or not found.")

        Crafter.resourceChestSerial = resourceChestSerial
        Crafter.resourceChest = resourceChest
        Crafter.openContainer(API.Backpack)
        Crafter.openContainer(resourceChest)

    def train(self, calculateSkillLabels=None):
        self.trainer.train(calculateSkillLabels)


class TinkeringTrainer(CraftingSkillTrainer):
    skillName = "Tinkering"
    trainerClass = TinkeringSkill


class TailoringTrainer(CraftingSkillTrainer):
    skillName = "Tailoring"
    trainerClass = TailoringSkill


class BlacksmithyTrainer(CraftingSkillTrainer):
    skillName = "Blacksmithy"
    trainerClass = BlacksmithySkill


class CartographyTrainer(CraftingSkillTrainer):
    skillName = "Cartography"
    trainerClass = CartographySkill


class BowcraftFletchingTrainer(CraftingSkillTrainer):
    skillName = "Bowcraft/Fletching"
    trainerClass = BowcraftFletchingSkill


class Trainer:
    schools = {
        "Miscellaneous": [
            _skill("Arms Lore", ArmsLoreTrainer, True),
            _skill("Begging"),
            _skill("Camping"),
            _skill("Cartography", CartographyTrainer, True),
            _skill("Forensic Evaluation"),
            _skill("Item Identification", ItemIdentificationTrainer, True),
            _skill("Taste Identification"),
        ],
        "Combat": [
            _skill("Anatomy"),
            _skill("Archery"),
            _skill("Fencing"),
            _skill("Focus"),
            _skill("Healing"),
            _skill("Mace Fighting"),
            _skill("Parrying"),
            _skill("Swordsmanship"),
            _skill("Tactics"),
            _skill("Throwing"),
            _skill("Wrestling"),
        ],
        "Trade Skills": [
            _skill("Alchemy"),
            _skill("Blacksmithy", BlacksmithyTrainer, True),
            _skill("Bowcraft/Fletching", BowcraftFletchingTrainer, True),
            _skill("Carpentry"),
            _skill("Cooking"),
            _skill("Inscription"),
            _skill("Lumberjacking"),
            _skill("Mining"),
            _skill("Tailoring", TailoringTrainer, True),
            _skill("Tinkering", TinkeringTrainer, True),
        ],
        "Magic": [
            _skill("Bushido", Bushido),
            _skill("Chivalry", Chivalry),
            _skill("Evaluating Intelligence", EvaluatingIntelligence),
            _skill("Imbuing"),
            _skill("Magery", Magery),
            _skill("Meditation", Meditation),
            _skill("Mysticism", Mysticism),
            _skill("Necromancy", Necromancy),
            _skill("Ninjitsu", Ninjitsu),
            _skill("Resisting Spells"),
            _skill("Spellweaving", Spellweaving),
            _skill("Spirit Speak", SpiritSpeak),
        ],
        "Wilderness": [
            _skill("Animal Lore", AnimalLore),
            _skill("Animal Taming", AnimalTamingTrainer, True),
            _skill("Fishing"),
            _skill("Herding"),
            _skill("Tracking"),
            _skill("Veterinary", VeterinaryTrainer, True),
        ],
        "Thieving": [
            _skill("Detecting Hidden"),
            _skill("Hiding"),
            _skill("Lockpicking", Lockpicking),
            _skill("Poisoning"),
            _skill("Remove Trap", RemoveTrap, True),
            _skill("Snooping"),
            _skill("Stealing"),
            _skill("Stealth"),
        ],
        "Bard": [
            _skill("Discordance"),
            _skill("Musicianship", Musicianship),
            _skill("Peacemaking", Peacemaking),
            _skill("Provocation"),
        ]
    }
    tabIcons = {
        "Miscellaneous": "default",
        "Combat": "default",
        "Trade Skills": "default",
        "Magic": "caster",
        "Wilderness": "tracking",
        "Thieving": "thief",
        "Bard": "bard",
    }

    def __init__(self):
        self.errors = []
        self._running = True
        self.gump = None
        self.schoolInputs = []
        self.createdSchoolGumps = set()
        self.trainingQueueGump = None
        self.trainingQueueScrollArea = None
        self.selectedSkillElements = []
        self.selectedSkillSummary = None
        self.selectedSkillsCache = []
        self.selectedSkillOrder = []
        self.skillInfoCache = {}
        self.sessionStartSkillValues = {}
        self.lastSelectedPanelUpdate = 0
        self.selectedPanelUpdateInterval = 0.75
        self.startBtn = None
        self.resourceContainerSerial = getResourceContainerSerial()
        self.resourceContainerLabel = None
        self.tabGumpWidth = 144
        self.mainGumpWidth = 400
        self.gumpHeight = max(400, 100 + max(len(skills) for skills in self.schools.values()) * 30)
        self.bottomPanelHeight = 220
        self.totalGumpWidth = self.tabGumpWidth + self.mainGumpWidth

    def main(self):
        try:
            Util.openContainer(API.Backpack)
            self._captureSessionStartSkillValues()
            self._showGump()
        except Exception as e:
            API.SysMsg(f"CasterTrainer e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            self.gump.tick()
            self.gump.tickSubGumps()
            self._updateSelectedSkillsPanelThrottled()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            self.gump.destroy()
            self.gump = None
        API.Stop()

    def _getSkillInfo(self, skillName, refresh=False):
        if refresh or skillName not in self.skillInfoCache:
            self.skillInfoCache[skillName] = Util.getSkillInfo(skillName)
        return self.skillInfoCache[skillName]

    def calculateSkillLabels(self, schoolName, refresh=True):
        for school in self.schools[schoolName]:
            skillName = school["skillName"]
            info = self._getSkillInfo(skillName, refresh)
            school["skillLabel"].Text = Math.truncateDecimal(info["value"], 1)
            school["capLabel"].Text = Math.truncateDecimal(info["cap"], 1)
        self._updateSelectedSkillsPanel(force=True)

    def _getTrainer(self, school):
        if school["skillName"] == "Remove Trap":
            importlib.reload(SkillTrainerRemoveTrap)
            school["trainer"] = SkillTrainerRemoveTrap.RemoveTrap
        return school["trainer"]

    def _withMagicPostCastMovement(self, school, trainer):
        skillName = school["skillName"]
        if school.get("name") != "Magic" or skillName not in MAGIC_POST_CAST_MOVE_SKILLS:
            return trainer

        trainOnce = getattr(trainer, "trainOnce", None)
        if trainOnce:
            def trainOnceWithPostCastMovement(*args, **kwargs):
                result = trainOnce(*args, **kwargs)
                self._moveAfterMagicCast(skillName)
                return result

            trainer.trainOnce = trainOnceWithPostCastMovement
            return trainer

        afterCast = getattr(trainer, "_afterCast", None)
        if not afterCast:
            return trainer

        def afterCastWithMovement(skillInfo, spellName, nextSpell):
            result = afterCast(skillInfo, spellName, nextSpell)
            self._moveAfterMagicCast(skillName)
            return result

        trainer._afterCast = afterCastWithMovement
        return trainer

    def _moveAfterMagicCast(self, skillName):
        for direction in POST_CAST_MOVE_DIRECTIONS:
            try:
                API.Walk(direction)
            except Exception as e:
                API.SysMsg(f"{skillName} post-cast walk {direction} failed: {e}", 33)
            API.Pause(POST_CAST_MOVE_PAUSE_SECONDS)

    def _validate(self, school, skillCap, projectedSkillValues=None):
        trainer = self._getTrainer(school)
        if not trainer:
            self.errors.append(f"{school['skillName']} - Training not implemented.")
            return
        if getattr(trainer, "setResourceContainerSerial", None):
            trainer.setResourceContainerSerial(self.resourceContainerSerial)
        errors = trainer.validate(skillCap)
        errors = self._filterProjectedValidationErrors(
            school, errors, projectedSkillValues
        )
        self.errors.extend(errors)

    def _filterProjectedValidationErrors(self, school, errors, projectedSkillValues):
        if not projectedSkillValues:
            return errors

        skillName = school["skillName"]
        tinkeringError = f"{skillName} - Tinkering must be at least 50.0."
        if tinkeringError not in errors:
            return errors

        try:
            projectedTinkering = Decimal(str(projectedSkillValues.get("Tinkering", 0)))
        except Exception:
            projectedTinkering = Decimal("0")

        if projectedTinkering >= Decimal("50"):
            return [error for error in errors if error != tinkeringError]
        return errors

    def _hideStartButton(self):
        if not self.startBtn:
            return

        elements = self.startBtn.get("elements") if isinstance(self.startBtn, dict) else None
        if elements:
            for element in elements:
                try:
                    element.IsVisible = False
                except Exception:
                    pass
            return

        self.startBtn.SetWidth(0)
        self.startBtn.SetHeight(0)

    def _setStatus(self, text, hue=None):
        statusGump = self.trainingQueueGump or self.gump
        if statusGump:
            statusGump.setStatus(text, hue)

    def _resourceContainerText(self):
        serial = self.resourceContainerSerial or getResourceContainerSerial()
        if serial:
            return f"Resource: {self._serial(serial)}"
        return "Resource: not selected"

    def _onResourceContainerClicked(self):
        self._setStatus("Target global resource container.", 48)
        target = API.RequestTarget(10)
        serial = getattr(target, "Serial", target)
        if not serial:
            self._setStatus("Global resource container unchanged.", 33)
            return
        self.resourceContainerSerial = serial
        setResourceContainerSerial(serial)
        if self.resourceContainerLabel:
            self.resourceContainerLabel.Text = self._resourceContainerText()
        self._setStatus(f"Global resource container set: {self._serial(serial)}.", 68)

    def _serial(self, serial):
        try:
            return hex(int(serial))
        except Exception:
            return str(serial)

    def _captureSessionStartSkillValues(self):
        for schools in self.schools.values():
            for school in schools:
                skillName = school["skillName"]
                if skillName not in self.sessionStartSkillValues:
                    self.sessionStartSkillValues[skillName] = Util.getSkillInfo(
                        skillName
                    )["value"]

    def _getSelectedSkills(self):
        selected = []
        for school, box, lbl, skillLbl in self.schoolInputs:
            skillName = school["skillName"]
            try:
                desired = Decimal(box.Text)
            except Exception:
                continue

            skillInfo = Util.getSkillInfo(skillName)
            if str(skillInfo.get("lock", "")).lower() == "down":
                continue

            startValue = self.sessionStartSkillValues.get(skillName)
            if startValue is None:
                startValue = skillInfo["value"]
                self.sessionStartSkillValues[skillName] = startValue
            if desired > startValue:
                selected.append((school, box, lbl, skillLbl, desired))

        selectedNames = [school["skillName"] for school, *_ in selected]
        for skillName in selectedNames:
            if skillName not in self.selectedSkillOrder:
                self.selectedSkillOrder.append(skillName)

        selectedNameSet = set(selectedNames)
        self.selectedSkillOrder = [
            skillName
            for skillName in self.selectedSkillOrder
            if skillName in selectedNameSet
        ]
        order = {
            skillName: index
            for index, skillName in enumerate(self.selectedSkillOrder)
        }
        return sorted(
            selected,
            key=lambda row: order.get(row[0]["skillName"], len(order)),
        )

    def _selectedSkillRowData(self, selected):
        rows = []
        for school, _, _, skillLbl, desired in selected:
            skillName = school["skillName"]
            try:
                current = Util.getSkillInfo(skillName)["value"]
            except Exception:
                current = Decimal(skillLbl.Text)

            startValue = self.sessionStartSkillValues.get(skillName, current)
            gain = current - startValue
            if gain < Decimal("0"):
                gain = Decimal("0")
            rows.append(
                (
                    skillName,
                    Math.truncateDecimal(current, 1),
                    Math.truncateDecimal(gain, 1),
                    Math.truncateDecimal(desired, 1),
                )
            )
        return rows

    def _addQueueScrollLabel(self, text, x, y, hue=None):
        label = self.trainingQueueGump.createLabel(text, hue)
        label.SetX(x)
        label.SetY(y)
        self.trainingQueueScrollArea.Add(label)
        self.selectedSkillElements.append(label)
        return label

    def _updateSelectedSkillsPanelThrottled(self):
        now = time.time()
        if now - self.lastSelectedPanelUpdate < self.selectedPanelUpdateInterval:
            return
        self.lastSelectedPanelUpdate = now
        self._updateSelectedSkillsPanel()

    def _updateSelectedSkillsPanel(self, force=False):
        if not self.trainingQueueScrollArea:
            return

        self.selectedSkillsCache = self._selectedSkillRowData(self._getSelectedSkills())
        summary = tuple(self.selectedSkillsCache)
        if not force and summary == self.selectedSkillSummary:
            return

        self.selectedSkillSummary = summary
        self.trainingQueueScrollArea.Clear()
        self.selectedSkillElements = []

        if not self.selectedSkillsCache:
            self._addQueueScrollLabel("None selected.", 8, 0)
            return

        for i, (skillName, current, gain, target) in enumerate(self.selectedSkillsCache):
            y = i * 18
            self._addQueueScrollLabel(skillName, 8, y)
            self._addQueueScrollLabel(str(current), 240, y)
            self._addQueueScrollLabel(str(gain), 320, y)
            self._addQueueScrollLabel(str(target), 390, y)

    def _onStart(self):
        try:
            if not self.gump.checkValidateForm():
                return

            self.errors.clear()
            workingSkills = self._getSelectedSkills()

            if not workingSkills:
                self._setStatus("No skills selected.", 33)
                return

            projectedSkillValues = {}
            for school, _, _, _, desired in workingSkills:
                self._validate(school, desired, projectedSkillValues)
                projectedSkillValues[school["skillName"]] = desired

            totalNeeded = sum(
                Decimal(box.Text) - Util.getSkillInfo(school["skillName"])["value"]
                for school, box, *_ in workingSkills
            )
            charInfo = Util.getCharSkillInfo()
            if charInfo["totalPlus"] + totalNeeded > 720:
                self.errors.append("Too many skill points selected.")

            if self.errors:
                self._setStatus(f"Validation failed: {self.errors[0]}", 33)
            else:
                self._hideStartButton()
                for school, box, lbl, skillLbl, skillCap in workingSkills:
                    trainerClass = self._getTrainer(school)
                    if school.get("useStatus"):
                        trainer = trainerClass(
                            skillCap, lbl, skillLbl, self._setStatus
                        )
                    else:
                        trainer = trainerClass(skillCap, lbl, skillLbl)
                    trainer = self._withMagicPostCastMovement(school, trainer)
                    self._setStatus(f"Training {school['skillName']}...")
                    trainer.train(lambda shcoolName=school["name"]: self.calculateSkillLabels(shcoolName))
        except Exception as e:
            API.SysMsg(str(e))
            API.SysMsg(traceback.format_exc())

    def _setSkillToCap(self, school, textbox, maxValue):
        skillName = school["skillName"]
        if skillName not in self.selectedSkillOrder:
            self.selectedSkillOrder.append(skillName)
        textbox.SetText(str(maxValue))
        self._updateSelectedSkillsPanel(force=True)

    def _ensureSchoolGump(self, gump, schoolName):
        if schoolName in self.createdSchoolGumps:
            return
        self._createSchoolGump(gump, schoolName)
        self.createdSchoolGumps.add(schoolName)
        self._updateSelectedSkillsPanel(force=True)

    def _createSchoolGump(self, gump, schoolName):
        gump.setStatus("Configure training and press okay...")
        gump.addLabel("Select Skill & Target Cap:", 10, 10)
        gump.addLabel("Current", 270, 30)
        gump.addLabel("Cap", 320, 30)

        y = 60
        x = 155
        schools = self.schools[schoolName]
        for school in schools:
            skillName = school["skillName"]
            info = self._getSkillInfo(skillName)
            lbl = gump.addLabel(skillName, 10, y)
            minValue = info["value"]
            maxValue = info["cap"]
            textbox = gump.addSkillTextBox(str(minValue), x, y, minValue, maxValue)
            gump.addButton(
                "",
                x + 85,
                y,
                "radioGreen",
                gump.onClick(
                    lambda sh=school, tb=textbox, maxV=maxValue: self._setSkillToCap(
                        sh, tb, maxV
                    )
                ),
            )
            school["skillLabel"] = gump.addLabel("", x + 115, y)
            school["capLabel"] = gump.addLabel("", x + 165, y)
            school["name"] = schoolName
            self.schoolInputs.append((school, textbox, lbl, school["skillLabel"]))
            y += 30

        self.calculateSkillLabels(schoolName, False)

    def _createTrainingQueuePanel(self):
        self.trainingQueueGump = self.gump.createSubGump(
            self.totalGumpWidth, self.bottomPanelHeight, "bottom", withStatus=True
        )
        footerHeight = 32
        statusReserve = 36
        footerY = self.bottomPanelHeight - statusReserve - footerHeight - 4
        listPanel = self.trainingQueueGump.addPanel(
            10,
            10,
            self.totalGumpWidth - 20,
            footerY - 18,
            "Selected skills to train",
        )
        x = listPanel["x"]
        y = listPanel["y"] + 2

        self.trainingQueueGump.addLabel("Skill", x, y)
        self.trainingQueueGump.addLabel("Current", x + 242, y)
        self.trainingQueueGump.addLabel("Gain", x + 322, y)
        self.trainingQueueGump.addLabel("Target", x + 392, y)

        self.trainingQueueScrollArea = self.trainingQueueGump.addScrollArea(
            listPanel["x"],
            y + 18,
            listPanel["width"],
            listPanel["height"] - 24,
        )

        self.trainingQueueGump.addColorBox(
            10, footerY, 1, self.totalGumpWidth - 20, Gump.theme["panelHeaderLine"], 0.85
        )
        self.trainingQueueGump.addColorBox(
            10,
            footerY + 1,
            footerHeight - 1,
            self.totalGumpWidth - 20,
            Gump.theme["statusBg"],
            0.92,
            withTexture=True,
        )
        self.trainingQueueGump.addTextButton(
            "Resource",
            16,
            footerY + 5,
            78,
            callback=self.trainingQueueGump.onClick(
                self._onResourceContainerClicked, "Select resource container...", ""
            ),
        )
        self.resourceContainerLabel = self.trainingQueueGump.addLabel(
            self._resourceContainerText(), 104, footerY + 8
        )
        self.startBtn = self.trainingQueueGump.addTextButton(
            "Start",
            self.totalGumpWidth - 78,
            footerY + 5,
            63,
            callback=self.trainingQueueGump.onClick(self._onStart, "Validating...", ""),
        )
        self._updateSelectedSkillsPanel(force=True)

    def _showGump(self):
        g = Gump(self.tabGumpWidth, self.gumpHeight, None, False)
        self.gump = g

        firstSchoolName = next(iter(self.schools))
        firstSchoolGump = None
        for schoolName in self.schools:
            schoolGump = g.addTabButton(
                schoolName,
                self.tabIcons.get(schoolName, "default"),
                self.mainGumpWidth,
                callback=lambda schoolName=schoolName: self._ensureSchoolGump(
                    self.gump.tabGumps[schoolName], schoolName
                ),
                yOffset=52,
                tabStyle="list",
            )
            if schoolName == firstSchoolName:
                firstSchoolGump = schoolGump

        self._createTrainingQueuePanel()

        self._ensureSchoolGump(firstSchoolGump, firstSchoolName)
        g.setActiveTab(firstSchoolName)
        g.create()

    def _isRunning(self):
        return self._running


trainer = Trainer()
trainer.main()
while trainer._isRunning():
    # trainer.gump.tick()
    # trainer.gump.tickSubGumps()
    trainer.tick()
    API.Pause(0.1)
