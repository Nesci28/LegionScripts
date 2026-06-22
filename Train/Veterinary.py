import importlib
import os
import sys
import traceback
from LegionPath import LegionPath

LegionPath.addSubdirs()

legionPath = LegionPath.getLegionPath()
if not os.path.isdir(legionPath):
    legionPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if legionPath not in sys.path:
    sys.path.insert(0, legionPath)

for name in os.listdir(legionPath):
    subdir = os.path.join(legionPath, name)
    if os.path.isdir(subdir) and name.startswith("_") and subdir not in sys.path:
        sys.path.append(subdir)

import _Skills.Veterinary as VeterinaryModule

importlib.reload(VeterinaryModule)

try:
    VeterinaryModule.API = API
except NameError:
    pass


TARGET_SKILL = 80
FORCE_SKILL_VALUE = 62
LOOP_DELAY = 0.25


def _skillCap():
    if TARGET_SKILL is not None:
        return TARGET_SKILL
    try:
        return API.GetSkill("Veterinary").Cap
    except Exception:
        return 120


def _status(text, hue=996):
    pass


try:
    targetSkill = _skillCap()
    veterinary = VeterinaryModule.Veterinary(
        targetSkill,
        setStatus=_status,
        forcedSkillValue=FORCE_SKILL_VALUE,
    )
    veterinary.main()

    while not API.StopRequested and veterinary._isRunning():
        veterinary.run()
        API.Pause(LOOP_DELAY)
except Exception as e:
    API.SysMsg(f"Veterinary test error: {e}", 33)
    API.SysMsg(traceback.format_exc())
