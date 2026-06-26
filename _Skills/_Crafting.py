import importlib
from decimal import Decimal

try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass
# API is injected by TazUO at runtime; the import above is IDE-only.
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Crafter
import Math
import Util

importlib.reload(Crafter)
importlib.reload(Math)
importlib.reload(Util)

Math = Math.Math
Util = Util.Util

RESOURCE_CONTAINER_SHARED_VAR = "SKILL_TRAINER_RESOURCE_CONTAINER_SERIAL"
_RESOURCE_CONTAINER_SERIAL = None


def _serialValue(target):
    return getattr(target, "Serial", target)


class _StatusProxy:
    def __init__(self, setStatus=None):
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


def setResourceContainerSerial(serial):
    global _RESOURCE_CONTAINER_SERIAL
    serial = _serialValue(serial)
    _RESOURCE_CONTAINER_SERIAL = serial
    try:
        API.SetSharedVar(RESOURCE_CONTAINER_SHARED_VAR, serial)
    except Exception:
        pass


def _getResourceContainerSerial():
    if _RESOURCE_CONTAINER_SERIAL:
        return _RESOURCE_CONTAINER_SERIAL
    try:
        return API.GetSharedVar(RESOURCE_CONTAINER_SHARED_VAR) or None
    except Exception:
        return None


def _findResourceContainer(serial):
    serial = _serialValue(serial)
    if not serial:
        return None

    container = API.FindItem(serial)
    if container:
        return container

    try:
        API.UseObject(serial)
        API.Pause(0.3)
    except Exception:
        return serial

    return API.FindItem(serial) or serial


class CraftingSkill:
    skillName = None

    @classmethod
    def setResourceContainerSerial(cls, serial):
        setResourceContainerSerial(serial)

    def __init__(self, skillCap=None, label=None, skillLevelLabel=None, setStatus=None):
        if not self.skillName:
            raise Exception("Crafting skill class is missing skillName.")

        self.skillCap = Decimal(str(skillCap if skillCap is not None else self._skill().Cap))
        self.label = label
        self.skillLevelLabel = skillLevelLabel
        self.setStatus = setStatus

        API.SetSkillLock(self.skillName, "up")
        self._ensureCrafterState()

    @classmethod
    def validate(cls, skillCap=None):
        errors = []

        if not _getResourceContainerSerial():
            errors.append(f"{cls.skillName} - Select the global resource container.")

        if cls.skillName not in Crafter.craftingSkills:
            errors.append(f"{cls.skillName} - Crafting trainer not implemented.")

        skillCapValue = Decimal(str(skillCap)) if skillCap is not None else None
        if cls.skillName == "Cartography" and skillCapValue is not None and skillCapValue > Decimal("99.5"):
            errors.append("Cartography - Target should be <= 99.5.")

        if cls.skillName != "Tinkering":
            tinkering = API.GetSkill("Tinkering")
            if not tinkering:
                errors.append("Tinkering - API.GetSkill returned None.")
            elif Decimal(str(tinkering.Value)) < Decimal("50"):
                errors.append(f"{cls.skillName} - Tinkering must be at least 50.0.")

        return errors

    def train(self, calculateSkillLabels=None):
        self._ensureCrafterState()
        self._status(f"Training {self.skillName}...")
        Crafter.trainCraftingSkill(self.skillName, self.skillCap)
        if calculateSkillLabels:
            calculateSkillLabels()

    def trainOnce(self):
        self._ensureCrafterState()
        skillValue = Decimal(str(self._skill().Value))
        if skillValue >= self.skillCap:
            return False

        item = self._itemForSkill(skillValue)
        if not item:
            return False

        Crafter.makeFirst(item, self.skillName, self.skillCap)
        return True

    def _ensureCrafterState(self):
        Crafter.API = API
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

        resourceChestSerial = _getResourceContainerSerial()
        resourceChest = _findResourceContainer(resourceChestSerial)
        if not resourceChest:
            raise Exception("Global resource container not selected or not found.")

        Crafter.resourceChestSerial = resourceChestSerial
        Crafter.resourceChest = resourceChest
        Crafter.openContainer(API.Backpack)
        Crafter.openContainer(resourceChest)

    def _skill(self):
        skill = API.GetSkill(self.skillName)
        if not skill:
            raise Exception(f"{self.skillName} - API.GetSkill returned None.")
        return skill

    def _itemForSkill(self, skillValue):
        items = Crafter.craftingSkills[self.skillName]["items"]
        for item in items:
            if skillValue < Decimal(str(item["skill"])):
                return item
        return items[-1] if items else None

    def _status(self, text, hue=None):
        if self.setStatus:
            self.setStatus(text, hue)
