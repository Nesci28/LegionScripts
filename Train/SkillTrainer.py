import API
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
import Crafter

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
importlib.reload(Crafter)

try:
    Veterinary.API = API
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

RESOURCE_CONTAINER_SHARED_VAR = "SKILL_TRAINER_RESOURCE_CONTAINER_SERIAL"


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

    @classmethod
    def validate(cls, skillCap=None):
        errors = []
        resourceError = resourceContainerValidationError(cls.skillName)
        if resourceError:
            errors.append(resourceError)
        if cls.skillName not in Crafter.craftingSkills:
            errors.append(f"{cls.skillName} - Crafting trainer not implemented.")
        if cls.skillName == "Cartography" and skillCap is not None and skillCap > Decimal("99.5"):
            errors.append("Cartography - Target should be <= 99.5.")
        tinkering = Util.getSkillInfo("Tinkering")["value"]
        if cls.skillName != "Tinkering" and tinkering < 50:
            errors.append(f"{cls.skillName} - Tinkering must be at least 50.0.")
        return errors

    def __init__(self, skillCap, label=None, skillLevelLabel=None, setStatus=None):
        self.skillCap = skillCap
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.setStatus = setStatus
        API.SetSkillLock(self.skillName, "up")

    def _ensureCrafterState(self):
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
        self._ensureCrafterState()
        if self.setStatus:
            self.setStatus(f"Training {self.skillName}...")
        Crafter.trainCraftingSkill(self.skillName, self.skillCap)
        if calculateSkillLabels:
            calculateSkillLabels()


class TinkeringTrainer(CraftingSkillTrainer):
    skillName = "Tinkering"


class TailoringTrainer(CraftingSkillTrainer):
    skillName = "Tailoring"


class BlacksmithyTrainer(CraftingSkillTrainer):
    skillName = "Blacksmithy"


class CartographyTrainer(CraftingSkillTrainer):
    skillName = "Cartography"


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
            _skill("Bowcraft/Fletching"),
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
        self.skillInfoCache = {}
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

    def _validate(self, school, skillCap):
        trainer = self._getTrainer(school)
        if not trainer:
            self.errors.append(f"{school['skillName']} - Training not implemented.")
            return
        errors = trainer.validate(skillCap)
        self.errors.extend(errors)

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
        serial = API.RequestTarget(10)
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

    def _getSelectedSkills(self):
        selected = []
        for school, box, lbl, skillLbl in self.schoolInputs:
            skillName = school["skillName"]
            try:
                desired = Decimal(box.Text)
            except Exception:
                continue

            try:
                current = Decimal(skillLbl.Text)
            except Exception:
                current = Util.getSkillInfo(skillName)["value"]
            if desired > current:
                selected.append((school, box, lbl, skillLbl, desired))
        return selected

    def _selectedSkillRowData(self, selected):
        rows = []
        for school, _, _, skillLbl, desired in selected:
            try:
                current = Decimal(skillLbl.Text)
            except Exception:
                current = Util.getSkillInfo(school["skillName"])["value"]
            rows.append(
                (
                    school["skillName"],
                    Math.truncateDecimal(current, 1),
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

        for i, (skillName, current, target) in enumerate(self.selectedSkillsCache):
            y = i * 18
            self._addQueueScrollLabel(skillName, 8, y)
            self._addQueueScrollLabel(str(current), 270, y)
            self._addQueueScrollLabel(str(target), 350, y)

    def _onStart(self):
        try:
            if not self.gump.checkValidateForm():
                return

            self.errors.clear()
            workingSkills = self._getSelectedSkills()

            if not workingSkills:
                self._setStatus("No skills selected.", 33)
                return

            for school, _, _, _, desired in workingSkills:
                self._validate(school, desired)

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
                    self._setStatus(f"Training {school['skillName']}...")
                    trainer.train(lambda shcoolName=school["name"]: self.calculateSkillLabels(shcoolName))
        except Exception as e:
            API.SysMsg(str(e))
            API.SysMsg(traceback.format_exc())

    def _setSkillToCap(self, textbox, maxValue):
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
                    lambda tb=textbox, maxV=maxValue: self._setSkillToCap(tb, maxV)
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
        self.trainingQueueGump.addLabel("Current", x + 262, y)
        self.trainingQueueGump.addLabel("Target", x + 342, y)

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
