#----------------------------------------------------------
# Mystic Llamas Imbuing & SSI Calc 
#----------------------------------------------------------

import sys
import re
import math
import os
import time
import traceback
import importlib
import API
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util as UtilModule
import Gump as GumpModule

importlib.reload(UtilModule)
importlib.reload(GumpModule)

from Util import Util
from Gump import Gump


class _ItemProxy:
    def __init__(self, item):
        self._item = item

    @property
    def ItemID(self):
        return getattr(self._item, "Graphic", 0)

    def __getattr__(self, name):
        return getattr(self._item, name)


def _serial(obj):
    if obj is None:
        return 0
    return getattr(obj, "Serial", obj)


def _as_item(obj):
    if obj is None:
        return None
    if isinstance(obj, _ItemProxy):
        return obj
    return _ItemProxy(obj)


def _item_amount(item):
    try:
        amount = int(getattr(item, "Amount", 1) or 1)
    except Exception:
        amount = 1
    return max(1, amount)


DEBUG_IMBUING = True
DEBUG_LOG_FILE = "MysticLlamasImbuing.log"


def _debug_log_path():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    except Exception:
        base_dir = "."
    return os.path.join(base_dir, DEBUG_LOG_FILE)


def DebugLog(message, hue=55):
    if not DEBUG_IMBUING:
        return

    text = "[ML Imbue] {}".format(message)
    try:
        API.SysMsg(text, hue)
    except Exception:
        pass

    try:
        with open(_debug_log_path(), "a") as log_file:
            log_file.write("{} {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), text))
    except Exception:
        pass


def _debug_hex(value):
    try:
        return "0x{:X}".format(int(value))
    except Exception:
        return str(value)


def _debug_graphics(graphics):
    return ",".join(_debug_hex(g) for g in graphics)


def _debug_item(item):
    return "serial={} amount={} container={}".format(
        _debug_hex(_serial(item)),
        _item_amount(item),
        _debug_hex(getattr(item, "Container", 0))
    )


def _count_matching_items(container, graphic_data, hue, recursive=False):
    graphics = graphic_data if isinstance(graphic_data, (tuple, list)) else (graphic_data,)
    try:
        contents = API.ItemsInContainer(container, recursive) or []
    except Exception:
        contents = []

    total = 0
    for item in contents:
        if getattr(item, "Graphic", 0) in graphics and getattr(item, "Hue", 0) == hue:
            total += _item_amount(item)
    return total


class Misc:
    @staticmethod
    def SendMessage(message, hue=946):
        API.SysMsg(str(message), hue)

    @staticmethod
    def Pause(milliseconds):
        API.Pause(float(milliseconds) / 1000.0)


class _BackpackProxy:
    @property
    def Serial(self):
        return API.Backpack

    @property
    def Contains(self):
        return [_as_item(item) for item in (API.ItemsInContainer(API.Backpack, False) or [])]


class Player:
    Backpack = _BackpackProxy()

    @property
    def Serial(self):
        return API.Player.Serial

    @staticmethod
    def UseSkill(skill):
        API.UseSkill(skill)


class Target:
    @staticmethod
    def PromptTarget(message):
        API.SysMsg(message, 55)
        target = API.RequestTarget(30)
        return target if target else -1

    @staticmethod
    def WaitForTarget(timeout=5000, harmful=False):
        return API.WaitForTarget("any", float(timeout) / 1000.0)

    @staticmethod
    def TargetExecute(serial):
        API.Target(serial)


class Items:
    @staticmethod
    def FindBySerial(serial):
        return _as_item(API.FindItem(serial))

    @staticmethod
    def FindAllByID(graphic, hue=0, container=0, recursive=False):
        graphics = graphic if isinstance(graphic, (tuple, list)) else (graphic,)
        found_items = []

        if container:
            try:
                Items.WaitForContents(container, 400)
                contents = API.ItemsInContainer(container, recursive) or []
            except Exception:
                contents = []

            for item in contents:
                if getattr(item, "Graphic", 0) in graphics and getattr(item, "Hue", 0) == hue:
                    found_items.append(_as_item(item))

            return found_items

        for item_graphic in graphics:
            found = API.FindType(item_graphic, container, hue=hue)
            if found:
                found_items.append(_as_item(found))
        return found_items

    @staticmethod
    def FindByID(graphic, hue=0, container=0):
        found_items = Items.FindAllByID(graphic, hue, container, recursive=False)
        if found_items:
            return found_items[0]
        return None

    @staticmethod
    def Move(item, destination, amount=0):
        return Util.moveItem(_serial(item), destination, amount)

    @staticmethod
    def WaitForContents(container, timeout=1000):
        API.UseObject(container)
        API.Pause(float(timeout) / 1000.0)

    @staticmethod
    def WaitForProps(item, timeout=1000):
        API.ItemNameAndProps(_serial(item), True, max(1, int(float(timeout) / 1000.0)))

    @staticmethod
    def GetPropStringList(item):
        props = API.ItemNameAndProps(_serial(item), True, 2)
        if not props:
            return []
        return [line.strip() for line in str(props).splitlines() if line.strip()]


class Gumps:
    @staticmethod
    def WaitForGump(gump_id, timeout=5000):
        return API.WaitForGump(gump_id, float(timeout) / 1000.0)

    @staticmethod
    def SendAction(gump_id, button_id):
        return API.ReplyGump(button_id, gump_id)

    @staticmethod
    def GetLineList(gump_id):
        contents = API.GetGumpContents(gump_id)
        if not contents:
            return []
        return [line.strip() for line in str(contents).splitlines() if line.strip()]

    @staticmethod
    def CloseGump(gump_id):
        return API.CloseGump(gump_id)


class Journal:
    @staticmethod
    def Clear():
        API.ClearJournal()

    @staticmethod
    def Search(text):
        return API.InJournal(text)

# ---------------------------------------------------------
# UI SETTINGS & HUES
# ---------------------------------------------------------
BTN_SELECT_1 = 4005 
BTN_SELECT_2 = 4007 

BTN_PLUS_1 = 5540  
BTN_PLUS_2 = 5542  
BTN_MINUS_1 = 5537 
BTN_MINUS_2 = 5539 

BTN_PAGE_LEFT_1 = 4508 
BTN_PAGE_LEFT_2 = 4508
BTN_PAGE_RIGHT_1 = 4502 
BTN_PAGE_RIGHT_2 = 4502

BTN_MAX_1 = 40018 
BTN_MAX_2 = 40028

BTN_MINIMIZE_1 = 5401
BTN_MINIMIZE_2 = 5401
BTN_MAXIMIZE_1 = 5402
BTN_MAXIMIZE_2 = 5402

C_TEXT = 1153      
C_HL = 95         
C_CYAN = 87       
C_BLUE = 195       
C_GREEN = 69     
C_GRAY = 999       
C_RED = 133        

BG_OUTER = 9200
BG_INNER = 1759
BAR_BG   = 200
BAR_FG = 1759

MAIN_X = 260
SIDE_X = 48 
ITEMS_PER_PAGE = 18

# ---------------------------------------------------------
# MAATERIAL AND PROP DB
# ---------------------------------------------------------
INGREDIENT_GRAPHICS = {
    "Magical Residue": (0x2DB1, 0x0000), "Enchanted Essence": (0x2DB2, 0x0000), "Relic Fragment": (0x2DB3, 0x0000),
    
    "Tourmaline": (0xF18, 0x0000), 
    "Ruby": (0x0F13, 0x0000), 
    "Emerald": (0x0F10, 0x0000), 
    "Sapphire": (0xF11, 0x0000), 
    "Amethyst": (0x0F16, 0x0000), 
    "Star Sapphire": (0x0F0F, 0x0000),
    "Citrine": (0x0F15, 0x0000), 
    "Diamond": (0x0F26, 0x0000), 
    "Amber": (0x0F25, 0x0000), 

    "Dark Sapphire": (0x3192, 0x0000), "Brilliant Amber": (0x3199, 0x0035), "Turquoise": (0x3193, 0x0000),
    "Fire Ruby": (0x3197, 0x0000), "White Pearl": (0x3196, 0x0000), "Perfect Emerald": (0x3194, 0x0000),
    "Ecru Citrine": (0x3195, 0x0000), "Blue Diamond": (0x3198, 0x0000), 
    
    "Essence of Singularity": (0x571C, 0x0497), "Essence of Direction": (0x571C, 0x0061), "Essence of Passion": (0x571C, 0x0489), 
    "Essence of Precision": (0x571C, 0x0016), "Essence of Persistence": (0x571C, 0x0025), "Essence of Control": (0x571C, 0x048d), 
    "Essence of Achievement": (0x571C, 0x002f), "Essence of Diligence": (0x571C, 0x048e), "Essence of Order": (0x571C, 0x0481), 
    "Essence of Balance": (0x571C, 0x0043), "Essence of Feeling": (0x571C, 0x0034),
    
    "Parasitic Plant": (0x3190, 0x0000), "Seed of Renewal": (0x5736, 0x0000), "Chaga Mushroom": (0x5743, 0x0000), "Bottle of Ichor": (0x5748, 0x0000),
    "Faery Dust": (0x5745, 0x0000), "Crystal Shards": (0x5738, 0x0000),"Crushed Glass": (0x573b, 0x0000), "Elven Fletching": (0x5737, 0x0000),
    "Boura Pelt": (0x5742, 0x0000), "Undying Flesh": (0x5731, 0x0000), "Slith Tongue": (0x5746, 0x0000), "Luminescent Fungi": (0x3191, 0x0000),
    "Vial of Vitriol": (0x5722, 0x0000), "Spider Carapace": (0x5720, 0x0000), "Daemon Claw": (0x5721, 0x0000), "Arcanic Rune Stone": (0x573c, 0x0000), 
    "Fey Wings": (0x5726, 0x0000), "Lava Serpent Crust": (0x572d, 0x0000), "Goblin Blood": (0x572c, 0x0000), "Reflective Wolf Eye": (0x5749, 0x0000),
    "Void Orb": (0x573e, 0x0000), "Void Core": (0x5728, 0x0000), "Silver Snake Skin": (0x5744, 0x0000), "Delicate Scales": (0x573a, 0x0000), 
    "Crystalline Blackrock": (0x5732, 0x0000), "Raptor Teeth": (0x5747, 0x0000), 
}

BASE_PROPS = {
    "None": {"Weight": 0, "Step": 0, "Primary": "None", "Gem": "None", "Special": "None"},
    "Hit Point Increase": {"Weight": 110, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Ruby", "Special": "Luminescent Fungi"},
    "Stamina Increase": {"Weight": 110, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Diamond", "Special": "Luminescent Fungi"},
    "Mana Increase": {"Weight": 110, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Sapphire", "Special": "Luminescent Fungi"},
    "Hit Point Regeneration": {"Weight": 100, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Tourmaline", "Special": "Seed of Renewal"},
    "Stamina Regeneration": {"Weight": 100, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Diamond", "Special": "Seed of Renewal"},
    "Mana Regeneration": {"Weight": 100, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Sapphire", "Special": "Seed of Renewal"},
    "Strength Bonus": {"Weight": 110, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Diamond", "Special": "Fire Ruby"},
    "Dexterity Bonus": {"Weight": 110, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Ruby", "Special": "Blue Diamond"},
    "Intelligence Bonus": {"Weight": 110, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Tourmaline", "Special": "Turquoise"},
    "Damage Increase": {"Weight": 100, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Citrine", "Special": "Crystal Shards"},
    "Damage Increase (Wood)": {"Weight": 40, "Step": 10, "Primary": "Enchanted Essence", "Gem": "Citrine", "Special": "Crystal Shards"},
    "Defense Chance Increase": {"Weight": 110, "Step": 1, "Primary": "Relic Fragment", "Gem": "Tourmaline", "Special": "Essence of Singularity"},
    "Hit Chance Increase": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Amber", "Special": "Essence of Precision"},
    "Swing Speed Increase": {"Weight": 110, "Step": 5, "Primary": "Relic Fragment", "Gem": "Tourmaline", "Special": "Essence of Control"},
    "Balanced": {"Weight": 150, "Step": 1, "Primary": "Relic Fragment", "Gem": "Amber", "Special": "Essence of Balance"},
    "Use Best Weapon Skill": {"Weight": 150, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Amber", "Special": "Delicate Scales"},
    "Spell Damage Increase": {"Weight": 100, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Emerald", "Special": "Crystal Shards"},
    "Faster Casting": {"Weight": 140, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Essence of Achievement"},
    "Faster Cast Recovery": {"Weight": 120, "Step": 1, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Essence of Diligence"},
    "Lower Mana Cost": {"Weight": 110, "Step": 1, "Primary": "Relic Fragment", "Gem": "Tourmaline", "Special": "Essence of Order"},
    "Lower Reagent Cost": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Amber", "Special": "Faery Dust"},
    "Spell Channeling": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Diamond", "Special": "Silver Snake Skin"},
    "Mage Weapon": {"Weight": 100, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Emerald", "Special": "Arcanic Rune Stone"},
    "Mage Armor": {"Weight": 0, "Step": 1, "Primary": "Magical Residue", "Gem": "Diamond", "Special": "None"},
    "Casting Focus": {"Weight": 120, "Step": 1, "Primary": "Magical Residue", "Gem": "Amethyst", "Special": "Slith Tongue"},
    "Reflect Physical Damage": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Citrine", "Special": "Reflective Wolf Eye"},
    "Hit Life Leech": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Ruby", "Special": "Void Orb"},
    "Hit Mana Leech": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Sapphire", "Special": "Void Orb"},
    "Hit Stamina Leech": {"Weight": 100, "Step": 2, "Primary": "Magical Residue", "Gem": "Diamond", "Special": "Void Orb"},
    "Hit Lower Attack": {"Weight": 110, "Step": 2, "Primary": "Enchanted Essence", "Gem": "Emerald", "Special": "Parasitic Plant"},
    "Hit Lower Defense": {"Weight": 130, "Step": 2, "Primary": "Enchanted Essence", "Gem": "Tourmaline", "Special": "Parasitic Plant"},
    "Hit Magic Arrow": {"Weight": 120, "Step": 2, "Primary": "Relic Fragment", "Gem": "Amber", "Special": "Essence of Feeling"},
    "Hit Harm": {"Weight": 110, "Step": 2, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "Parasitic Plant"},
    "Hit Fireball": {"Weight": 140, "Step": 2, "Primary": "Magical Residue", "Gem": "Ruby", "Special": "Fire Ruby"},
    "Hit Lightning": {"Weight": 140, "Step": 2, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Essence of Passion"},
    "Hit Dispel": {"Weight": 100, "Step": 2, "Primary": "Magical Residue", "Gem": "Amber", "Special": "Slith Tongue"},
    "Hit Cold Area": {"Weight": 100, "Step": 2, "Primary": "Magical Residue", "Gem": "Sapphire", "Special": "Raptor Teeth"},
    "Hit Energy Area": {"Weight": 100, "Step": 2, "Primary": "Magical Residue", "Gem": "Amethyst", "Special": "Raptor Teeth"},
    "Hit Fire Area": {"Weight": 100, "Step": 2, "Primary": "Magical Residue", "Gem": "Ruby", "Special": "Raptor Teeth"},
    "Hit Physical Area": {"Weight": 100, "Step": 2, "Primary": "Magical Residue", "Gem": "Diamond", "Special": "Raptor Teeth"},
    "Hit Poison Area": {"Weight": 100, "Step": 2, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "Raptor Teeth"},
    "Physical Resist": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Diamond", "Special": "Boura Pelt"},
    "Fire Resist": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Ruby", "Special": "Boura Pelt"},
    "Cold Resist": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Sapphire", "Special": "Boura Pelt"},
    "Poison Resist": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "Boura Pelt"},
    "Energy Resist": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Amethyst", "Special": "Boura Pelt"},
    "Damage Eater": {"Weight": 225, "Step": 3, "Primary": "Relic Fragment", "Gem": "Diamond", "Special": "Undying Flesh"},
    "Kinetic Eater": {"Weight": 90, "Step": 3, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Undying Flesh"},
    "Fire Eater": {"Weight": 90, "Step": 3, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Undying Flesh"},
    "Cold Eater": {"Weight": 90, "Step": 3, "Primary": "Relic Fragment", "Gem": "Sapphire", "Special": "Undying Flesh"},
    "Poison Eater": {"Weight": 90, "Step": 3, "Primary": "Relic Fragment", "Gem": "Emerald", "Special": "Undying Flesh"},
    "Energy Eater": {"Weight": 90, "Step": 3, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Undying Flesh"},
    "Repond Slayer": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Goblin Blood"},
    "Undead Slayer": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Undying Flesh"},
    "Demon Slayer": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Daemon Claw"},
    "Elemental Slayer": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Vial of Vitriol"},
    "Arachnid Slayer": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Spider Carapace"},
    "Fey Slayer": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Fey Wings"},
    "Reptile Slayer": {"Weight": 130, "Step": 1, "Primary": "Relic Fragment", "Gem": "Ruby", "Special": "Lava Serpent Crust"},
    "Air Elemental Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Blood Elemental Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Earth Elemental Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Fire Elemental Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Poison Elemental Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Snow Elemental Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Water Elemental Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Dragon Slayer": {"Weight": 110, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Emerald", "Special": "White Pearl"},
    "Gargoyle Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Lizardman Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Ogre Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Ophidian Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Orc Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Scorpion Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Snake Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Spider Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Terathan Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Troll Slayer": {"Weight": 110, "Step": 1, "Primary": "Magical Residue", "Gem": "Emerald", "Special": "White Pearl"},
    "Luck": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Citrine", "Special": "Chaga Mushroom"},
    "Night Sight": {"Weight": 100, "Step": 1, "Primary": "Magical Residue", "Gem": "Tourmaline", "Special": "Bottle of Ichor"},
    "Enhance Potions": {"Weight": 100, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Citrine", "Special": "Crushed Glass"},
    "Lower Requirements": {"Weight": 100, "Step": 10, "Primary": "Enchanted Essence", "Gem": "Amethyst", "Special": "Elven Fletching"},
    "Soul Charge": {"Weight": 150, "Step": 5, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Vial of Vitriol"},
    "Reactive Paralyze": {"Weight": 140, "Step": 1, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Spider Carapace"},
    "Splintering": {"Weight": 225, "Step": 5, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Vial of Vitriol"},
    "Battle Lust": {"Weight": 100, "Step": 1, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Vial of Vitriol"},
    "Hit Fatigue": {"Weight": 125, "Step": 10, "Primary": "Relic Fragment", "Gem": "Amethyst", "Special": "Vial of Vitriol"},
    "Hit Mana Drain": {"Weight": 175, "Step": 2, "Primary": "Magical Residue", "Gem": "Sapphire", "Special": "Void Orb"},
    "Velocity": {"Weight": 140, "Step": 1, "Primary": "Relic Fragment", "Gem": "Tourmaline", "Special": "Essence of Direction"},
    # --- SKILLS ---
    "Magery": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Musicianship": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Swordsmanship": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Mace Fighting": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Fencing": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Wrestling": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Animal Taming": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Spirit Speak": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Tactics": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Provocation": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Focus": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Parrying": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Stealth": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Meditation": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Animal Lore": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Discordance": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Mysticism": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Bushido": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Necromancy": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Veterinary": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Stealing": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Eval Intelligence": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Anatomy": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Peacemaking": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Throwing": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Ninjitsu": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Chivalry": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Archery": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Resisting Spells": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"},
    "Healing": {"Weight": 140, "Step": 1, "Primary": "Enchanted Essence", "Gem": "Star Sapphire", "Special": "Crystalline Blackrock"}
}

# ---------------------------------------------------------
# WEAPONS DB
# ---------------------------------------------------------
GROUP_ORDER = [
    "CASTING", "COMBAT", "HIT AREA EFFECTS", "HIT EFFECTS", 
    "MISC.", "RESISTS", "SKILL GROUP 1", "SKILL GROUP 2",
    "SKILL GROUP 3", "SKILL GROUP 4", "SKILL GROUP 5",
    "SLAYERS", "SUPER SLAYERS", "STATS", "CUSTOM PROPERTIES"
]

WEAPON_SPEEDS = {
    "Assassin Spike": 2.00, "Axe": 3.00, "Barbed Whip": 3.25, "Bardiche": 3.75, 
    "Battle Axe": 3.50, "Black Staff": 2.75, "Bladed Staff": 3.00, "Bladed Whip": 3.25, 
    "Bloodblade": 2.00, "Bokuto": 2.00, "Bone Harvester": 3.00, "Broadsword": 3.25, 
    "Butcher Knife": 2.25, "Cleaver": 2.50, "Club": 2.50, "Crescent Blade": 2.50, 
    "Cutlass": 2.50, "Dagger": 2.00, "Daisho": 2.75, "Diamond Mace": 3.25, 
    "Disc Mace": 2.75, "Double Axe": 3.25, "Double Bladed Staff": 2.25, 
    "Dual Pointed Spear": 2.25, "Dual Short Axes": 3.00, "Elven Machete": 2.75, 
    "Elven Spellblade": 2.50, "Executioner's Axe": 3.25, "Gargish Axe": 3.00, 
    "Gargish Battle Axe": 3.50, "Gargish Bone Harvester": 3.00, "Gargish Butcher's Knife": 2.25, 
    "Gargish Cleaver": 2.50, "Gargish Dagger": 2.00, "Gargish Daisho": 2.75, 
    "Gargish Gnarled Staff": 3.25, "Gargish Katana": 2.50, "Gargish Kryss": 2.00, 
    "Gargish Lance": 4.25, "Gargish Maul": 3.50, "Gargish Pike": 3.00, 
    "Gargish Scythe": 3.50, "Gargish Talwar": 3.50, "Gargish Tekagi": 2.00, 
    "Gargish Tessen": 2.00, "Gargish War Hammer": 3.75, "Gargish Warfork": 2.50, 
    "Glass Staff": 2.25, "Glass Sword": 2.75, "Gnarled Staff": 3.25, 
    "Halberd": 4.00, "Hammer Pick": 3.25, "Hatchet": 2.75, "Kama": 2.00, 
    "Katana": 2.50, "Kryss": 2.00, "Lajatang": 3.50, "Lance": 4.50, 
    "Large Battle Axe": 3.75, "Leafblade": 2.75, "Longsword": 3.50, 
    "Mace": 2.75, "Maul": 3.50, "No-dachi": 3.50, "Nunchaku": 2.50, 
    "Ornate Axe": 3.75, "Paladin Sword": 5.00, "Pickaxe": 3.00, "Pike": 3.00, 
    "Pitchfork": 2.50, "Quarter Staff": 2.25, "Radiant Scimitar": 2.50, 
    "Rune Blade": 3.00, "Sai": 2.00, "Scepter": 3.50, "Scimitar": 3.00, 
    "Scythe": 3.50, "Serpentstone Staff": 3.50, "Shepherd's Crook": 2.75, 
    "Short Spear": 2.00, "Shortblade": 2.25, "Skinning Knife": 2.25, 
    "Sledge Hammer": 3.25, "Smith's Hammer": 3.25, "Spear": 2.75, 
    "Spiked Whip": 3.25, "Tekagi": 2.00, "Tessen": 2.00, "Tetsubo": 2.50, 
    "Two Handed Axe": 3.50, "Viking Sword": 3.75, "Wakizashi": 2.50, 
    "Wand": 2.75, "War Axe": 3.00, "War Cleaver": 2.25, "War Fork": 2.50, 
    "War Hammer": 3.75, "War Mace": 4.00, "Wild Staff": 2.25,
    "Boomerang": 2.75, "Bow": 4.25, "Composite Bow": 4.00, "Crossbow": 4.50, 
    "Cyclone": 3.25, "Elven Composite Longbow": 3.75, "Heavy Crossbow": 5.00, 
    "Magical Shortbow": 3.00, "Repeating Crossbow": 2.75, "Soul Glaive": 4.00, 
    "Yumi": 3.25
}

SPEED_MENU = {}
for w, s in WEAPON_SPEEDS.items():
    s_str = "{:.2f}s".format(s)
    if s_str not in SPEED_MENU:
        SPEED_MENU[s_str] = []
    SPEED_MENU[s_str].append(w)
SPEED_KEYS = sorted(SPEED_MENU.keys(), key=lambda x: float(x.replace('s', '')))

ITEM_DB = {
    "One-Handed Melee": {
        "Swords": ["Assassin Spike", "Bloodblade", "Bokuto", "Bone Harvester", "Broadsword", "Butcher Knife", "Cleaver", "Crescent Blade", "Cutlass", "Dagger", "Elven Machete", "Elven Spellblade", "Glass Sword", "Katana", "Longsword", "Radiant Scimitar", "Rune Blade", "Scimitar", "Shortblade", "Skinning Knife", "Viking Sword", "Wakizashi"],
        "Maces": ["Club", "Diamond Mace", "Disc Mace", "Hammer Pick", "Mace", "Maul", "Scepter", "Smith's Hammer", "Tetsubo", "Wand", "War Mace"],
        "Fencing": ["Kryss", "Leafblade", "Sai", "War Cleaver", "War Fork"],
        "Axes": ["Hatchet", "War Axe"],
        "Gargish": ["Gargish Bone Harvester", "Gargish Butcher's Knife", "Gargish Cleaver", "Gargish Dagger", "Gargish Katana", "Gargish Kryss", "Gargish Tekagi", "Gargish Tessen", "Gargish Warfork", "Gargish Maul"]
    },
    "Two-Handed Melee": {
        "Swords": ["Daisho", "Executioner's Axe", "No-dachi", "Paladin Sword"],
        "Maces": ["Black Staff", "Gnarled Staff", "Nunchaku", "Quarter Staff", "Serpentstone Staff", "Shepherd's Crook", "Sledge Hammer", "Wild Staff"],
        "Fencing": ["Pitchfork", "Short Spear", "Spear"],
        "Axes": ["Axe", "Battle Axe", "Double Axe", "Dual Short Axes", "Large Battle Axe", "Ornate Axe", "Two Handed Axe"],
        "Polearms": ["Bardiche", "Bladed Staff", "Double Bladed Staff", "Halberd", "Lajatang", "Lance", "Pike", "Scythe"],
        "Gargish": ["Gargish Axe", "Gargish Battle Axe", "Gargish Daisho", "Gargish Gnarled Staff", "Gargish Lance", "Gargish Pike", "Gargish Scythe", "Gargish Talwar", "Gargish War Hammer"]
    },
    "Ranged Weapon": {
        "Archery": ["Bow", "Composite Bow", "Elven Composite Longbow", "Magical Shortbow", "Repeating Crossbow", "Crossbow", "Heavy Crossbow", "Yumi"],
        "Throwing": ["Boomerang", "Cyclone", "Soul Glaive"]
    }
}

WEAPON_GROUPS_1H = ["ONE-HANDED MELEE", "Swords", "Maces", "Fencing", "Axes", "Gargish"]
WEAPON_GROUPS_2H = ["TWO-HANDED MELEE", "Swords", "Maces", "Fencing", "Axes", "Polearms", "Gargish"]
WEAPON_GROUPS_RANGED = ["RANGED / THROWING", "Archery", "Throwing"]

CATEGORIES = ["One-Handed Melee", "Two-Handed Melee", "Ranged Weapon", "Armor", "Jewelry", "Shields"]
SINGLE_TIER_CATS = ["Armor", "Jewelry", "Shields"]

# ---------------------------------------------------------
# SPLIT DATABASES 
# ---------------------------------------------------------
DB_ARMOR = {
    "None": {"Max": 0, "Group": "NONE"},
    "Lower Mana Cost": {"Max": 8, "Group": "CASTING"},
    "Lower Reagent Cost": {"Max": 20, "Group": "CASTING"},
    "Reflect Physical Damage": {"Max": 15, "Group": "CASTING"},
    "Luck": {"Max": 100, "Group": "MISC."},
    "Night Sight": {"Max": 1, "Group": "MISC."},
    "Cold Resist": {"Max": 15, "Group": "RESISTS"},
    "Energy Resist": {"Max": 15, "Group": "RESISTS"},
    "Fire Resist": {"Max": 15, "Group": "RESISTS"},
    "Physical Resist": {"Max": 15, "Group": "RESISTS"},
    "Poison Resist": {"Max": 15, "Group": "RESISTS"},
    "Hit Point Increase": {"Max": 5, "Group": "STATS"},
    "Hit Point Regeneration": {"Max": 2, "Group": "STATS"},
    "Mana Increase": {"Max": 8, "Group": "STATS"},
    "Mana Regeneration": {"Max": 2, "Group": "STATS"},
    "Stamina Increase": {"Max": 8, "Group": "STATS"},
    "Stamina Regeneration": {"Max": 3, "Group": "STATS"},
    "Mage Armor": {"Max": 1, "Group": "CUSTOM PROPERTIES"},
    "Casting Focus": {"Max": 3, "Group": "CUSTOM PROPERTIES"},
    "Damage Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Kinetic Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Fire Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Cold Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Poison Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Energy Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Strength Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Intelligence Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Dexterity Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Hit Chance Increase": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Defense Chance Increase": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Enhance Potions": {"Max": 3, "Weight": 12, "Group": "CUSTOM PROPERTIES"},
    "Damage Increase (Wood)": {"Max": 20, "Group": "CUSTOM PROPERTIES"}
}

DB_MELEE = {
    "None": {"Max": 0, "Group": "NONE"},
    "Faster Casting": {"Max": 1, "Group": "CASTING"},
    "Mage Weapon": {"Max": -20, "Group": "CASTING"},
    "Spell Channeling": {"Max": 1, "Group": "CASTING"},
    "Balanced": {"Max": 1, "Group": "COMBAT"},
    "Damage Increase": {"Max": 50, "Group": "COMBAT"},
    "Defense Chance Increase": {"Max": 15, "Group": "COMBAT"},
    "Hit Chance Increase": {"Max": 15, "Group": "COMBAT"},
    "Swing Speed Increase": {"Max": 30, "Group": "COMBAT"},
    "Use Best Weapon Skill": {"Max": 1, "Group": "COMBAT"},
    "Hit Cold Area": {"Max": 50, "Group": "HIT AREA EFFECTS"},
    "Hit Energy Area": {"Max": 50, "Group": "HIT AREA EFFECTS"},
    "Hit Fire Area": {"Max": 50, "Group": "HIT AREA EFFECTS"},
    "Hit Physical Area": {"Max": 50, "Group": "HIT AREA EFFECTS"},
    "Hit Poison Area": {"Max": 50, "Group": "HIT AREA EFFECTS"},
    "Hit Dispel": {"Max": 50, "Group": "HIT EFFECTS"},
    "Hit Fireball": {"Max": 50, "Group": "HIT EFFECTS"},
    "Hit Harm": {"Max": 50, "Group": "HIT EFFECTS"},
    "Hit Life Leech": {"Max": 100, "Group": "HIT EFFECTS"},
    "Hit Lightning": {"Max": 50, "Group": "HIT EFFECTS"},
    "Hit Lower Attack": {"Max": 50, "Group": "HIT EFFECTS"},
    "Hit Lower Defense": {"Max": 50, "Group": "HIT EFFECTS"},
    "Hit Magic Arrow": {"Max": 50, "Group": "HIT EFFECTS"},
    "Hit Mana Leech": {"Max": 100, "Group": "HIT EFFECTS"},
    "Hit Stamina Leech": {"Max": 50, "Group": "HIT EFFECTS"},
    "Luck": {"Max": 100, "Group": "MISC."},
    "Lower Requirements": {"Max": 100, "Group": "MISC."},
    "Cold Resist": {"Max": 15, "Group": "RESISTS"},
    "Energy Resist": {"Max": 15, "Group": "RESISTS"},
    "Fire Resist": {"Max": 15, "Group": "RESISTS"},
    "Physical Resist": {"Max": 15, "Group": "RESISTS"},
    "Poison Resist": {"Max": 15, "Group": "RESISTS"},
    "Air Elemental Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Blood Elemental Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Dragon Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Earth Elemental Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Fire Elemental Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Gargoyle Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Lizardman Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Ogre Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Ophidian Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Orc Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Poison Elemental Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Scorpion Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Snake Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Snow Elemental Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Spider Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Terathan Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Troll Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Water Elemental Slayer": {"Max": 1, "Group": "SLAYERS"},
    "Arachnid Slayer": {"Max": 1, "Group": "SUPER SLAYERS"},
    "Demon Slayer": {"Max": 1, "Group": "SUPER SLAYERS"},
    "Elemental Slayer": {"Max": 1, "Group": "SUPER SLAYERS"},
    "Fey Slayer": {"Max": 1, "Group": "SUPER SLAYERS"},
    "Repond Slayer": {"Max": 1, "Group": "SUPER SLAYERS"},
    "Reptile Slayer": {"Max": 1, "Group": "SUPER SLAYERS"},
    "Undead Slayer": {"Max": 1, "Group": "SUPER SLAYERS"},
    "Hit Point Regeneration": {"Max": 4, "Weight": 200, "Group": "CUSTOM PROPERTIES"},
    "Mana Regeneration": {"Max": 4, "Weight": 200, "Group": "CUSTOM PROPERTIES"},
    "Stamina Regeneration": {"Max": 3, "Group": "CUSTOM PROPERTIES"},
    "Strength Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Intelligence Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Dexterity Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Reactive Paralyze": {"Max": 1, "Group": "CUSTOM PROPERTIES"},
    "Hit Fatigue": {"Max": 50, "Group": "CUSTOM PROPERTIES"},
    "Splintering": {"Max": 30, "Group": "CUSTOM PROPERTIES"},
    "Battle Lust": {"Max": 1, "Group": "CUSTOM PROPERTIES"},
    "Enhance Potions": {"Max": 3, "Weight": 12, "Group": "CUSTOM PROPERTIES"},
    "Hit Mana Drain": {"Max": 70, "Group": "CUSTOM PROPERTIES"}
}

DB_RANGED = dict(DB_MELEE)
DB_RANGED["Hit Chance Increase"] = {"Max": 25, "Group": "COMBAT"}
DB_RANGED["Defense Chance Increase"] = {"Max": 25, "Group": "COMBAT"}
DB_RANGED["Cold Resist"] = {"Max": 18, "Group": "RESISTS"}
DB_RANGED["Energy Resist"] = {"Max": 18, "Group": "RESISTS"}
DB_RANGED["Fire Resist"] = {"Max": 18, "Group": "RESISTS"}
DB_RANGED["Physical Resist"] = {"Max": 18, "Group": "RESISTS"}
DB_RANGED["Poison Resist"] = {"Max": 18, "Group": "RESISTS"}
DB_RANGED["Velocity"] = {"Max": 40, "Group": "COMBAT"}
DB_RANGED["Luck"] = {"Max": 120, "Group": "MISC."}

DB_JEWELS = {
    "None": {"Max": 0, "Group": "NONE"},
    "Faster Casting": {"Max": 1, "Group": "CASTING"},
    "Faster Cast Recovery": {"Max": 3, "Group": "CASTING"},
    "Lower Mana Cost": {"Max": 8, "Group": "CASTING"},
    "Lower Reagent Cost": {"Max": 20, "Group": "CASTING"},
    "Spell Damage Increase": {"Max": 12, "Group": "CASTING"},
    "Damage Increase": {"Max": 25, "Group": "COMBAT"},
    "Defense Chance Increase": {"Max": 15, "Group": "COMBAT"},
    "Hit Chance Increase": {"Max": 15, "Group": "COMBAT"},
    "Luck": {"Max": 100, "Group": "MISC."},
    "Enhance Potions": {"Max": 25, "Group": "MISC."},
    "Night Sight": {"Max": 1, "Group": "MISC."},
    "Cold Resist": {"Max": 15, "Group": "RESISTS"},
    "Energy Resist": {"Max": 15, "Group": "RESISTS"},
    "Fire Resist": {"Max": 15, "Group": "RESISTS"},
    "Physical Resist": {"Max": 15, "Group": "RESISTS"},
    "Poison Resist": {"Max": 15, "Group": "RESISTS"},
    "Strength Bonus": {"Max": 8, "Group": "STATS"},
    "Dexterity Bonus": {"Max": 8, "Group": "STATS"},
    "Intelligence Bonus": {"Max": 8, "Group": "STATS"},
    
    # --- SKILL GROUP 1 ---
    "Fencing": {"Max": 15, "Group": "SKILL GROUP 1"},
    "Mace Fighting": {"Max": 15, "Group": "SKILL GROUP 1"},
    "Swordsmanship": {"Max": 15, "Group": "SKILL GROUP 1"},
    "Musicianship": {"Max": 15, "Group": "SKILL GROUP 1"},
    "Magery": {"Max": 15, "Group": "SKILL GROUP 1"},

    # --- SKILL GROUP 2 ---
    "Wrestling": {"Max": 15, "Group": "SKILL GROUP 2"},
    "Animal Taming": {"Max": 15, "Group": "SKILL GROUP 2"},
    "Spirit Speak": {"Max": 15, "Group": "SKILL GROUP 2"},
    "Tactics": {"Max": 15, "Group": "SKILL GROUP 2"},
    "Provocation": {"Max": 15, "Group": "SKILL GROUP 2"},

    # --- SKILL GROUP 3 ---
    "Focus": {"Max": 15, "Group": "SKILL GROUP 3"},
    "Parrying": {"Max": 15, "Group": "SKILL GROUP 3"},
    "Stealth": {"Max": 15, "Group": "SKILL GROUP 3"},
    "Meditation": {"Max": 15, "Group": "SKILL GROUP 3"},
    "Animal Lore": {"Max": 15, "Group": "SKILL GROUP 3"},
    "Discordance": {"Max": 15, "Group": "SKILL GROUP 3"},

    # --- SKILL GROUP 4 ---
    "Mysticism": {"Max": 15, "Group": "SKILL GROUP 4"},
    "Bushido": {"Max": 15, "Group": "SKILL GROUP 4"},
    "Necromancy": {"Max": 15, "Group": "SKILL GROUP 4"},
    "Veterinary": {"Max": 15, "Group": "SKILL GROUP 4"},
    "Stealing": {"Max": 15, "Group": "SKILL GROUP 4"},
    "Eval Intelligence": {"Max": 15, "Group": "SKILL GROUP 4"},
    "Anatomy": {"Max": 15, "Group": "SKILL GROUP 4"},

    # --- SKILL GROUP 5 ---
    "Peacemaking": {"Max": 15, "Group": "SKILL GROUP 5"},
    "Throwing": {"Max": 15, "Group": "SKILL GROUP 5"},
    "Ninjitsu": {"Max": 15, "Group": "SKILL GROUP 5"},
    "Chivalry": {"Max": 15, "Group": "SKILL GROUP 5"},
    "Archery": {"Max": 15, "Group": "SKILL GROUP 5"},
    "Resisting Spells": {"Max": 15, "Group": "SKILL GROUP 5"},
    "Healing": {"Max": 15, "Group": "SKILL GROUP 5"},
    
    # --- CUSTOM PROPERTIES ---
    "Hit Point Increase": {"Max": 5, "Group": "CUSTOM PROPERTIES"},
    "Mana Increase": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Stamina Increase": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Swing Speed Increase": {"Max": 10, "Weight": 36, "Group": "CUSTOM PROPERTIES"},
    "Hit Point Regeneration": {"Max": 4, "Weight": 200, "Group": "CUSTOM PROPERTIES"},
    "Mana Regeneration": {"Max": 4, "Weight": 200, "Group": "CUSTOM PROPERTIES"},
    "Stamina Regeneration": {"Max": 3, "Group": "CUSTOM PROPERTIES"}
}

DB_SHIELDS = {
    "None": {"Max": 0, "Group": "NONE"},
    "Faster Casting": {"Max": 1, "Group": "CASTING"},
    "Spell Channeling": {"Max": 1, "Group": "CASTING"},
    "Reflect Physical Damage": {"Max": 15, "Group": "CASTING"},
    "Lower Requirements": {"Max": 100, "Group": "MISC."},
    "Cold Resist": {"Max": 15, "Group": "RESISTS"},
    "Energy Resist": {"Max": 15, "Group": "RESISTS"},
    "Fire Resist": {"Max": 15, "Group": "RESISTS"},
    "Physical Resist": {"Max": 15, "Group": "RESISTS"},
    "Poison Resist": {"Max": 15, "Group": "RESISTS"},
    "Casting Focus": {"Max": 3, "Group": "CUSTOM PROPERTIES"},
    "Damage Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Kinetic Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Fire Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Cold Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Poison Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Energy Eater": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Hit Point Regeneration": {"Max": 4, "Weight": 200, "Group": "CUSTOM PROPERTIES"},
    "Mana Regeneration": {"Max": 4, "Weight": 200, "Group": "CUSTOM PROPERTIES"},
    "Stamina Regeneration": {"Max": 3, "Group": "CUSTOM PROPERTIES"},
    "Strength Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Intelligence Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Dexterity Bonus": {"Max": 8, "Group": "CUSTOM PROPERTIES"},
    "Hit Chance Increase": {"Max": 15, "Group": "CUSTOM PROPERTIES"},
    "Defense Chance Increase": {"Max": 15, "Group": "COMBAT"},
    "Enhance Potions": {"Max": 3, "Weight": 12, "Group": "CUSTOM PROPERTIES"},
    "Reactive Paralyze": {"Max": 1, "Group": "CUSTOM PROPERTIES"},
    "Luck": {"Max": 100, "Group": "CUSTOM PROPERTIES"},
    "Soul Charge": {"Max": 30, "Group": "CUSTOM PROPERTIES"}
}

# ---------------------------------------------------------
# HARDCODED GUMP BUTTONS
# ---------------------------------------------------------
IMBUE_CATS = {
    "CASTING": 1114248,
    "COMBAT": 1114249,
    "HIT AREA EFFECTS": 1114250,
    "HIT EFFECTS": 1114251,
    "MISC.": 1114252,
    "RANGED": 1114253, 
    "RESISTS": 1114254,
    "STATS": 1114262,
    "SLAYERS": 1114263,
    "SUPER SLAYERS": 1114264,
    "CUSTOM PROPERTIES": 0 
}

IMBUE_OVERRIDES = {
    "Jewelry": {
        "Damage Increase": 203,
        "Lower Reagent Cost": 204,
        "Lower Mana Cost": 203,
        "Hit Chance Increase": 202, 
        "Defense Chance Increase": 201, 
        "Luck": 202, 
        "Night Sight": 203, 
        "Enhance Potions": 201, 
        "Spell Damage Increase": 205,
        "Faster Cast Recovery": 201 
    },
    "Armor": {
        "Lower Reagent Cost": 202,
        "Lower Mana Cost": 201, 
        "Luck": 201, 
        "Night Sight": 202, 
        "Reflect Physical Damage": 203, 
    },
    "Shields": {
        "Spell Channeling": 202, 
        "Reflect Physical Damage": 203, 
        "Lower Requirements": 202,
        "Defense Chance Increase": 201, 
    }
}
IMBUE_PROPS = {
    # --- CASTING ---
    "Faster Casting": 201, 
    "Mage Weapon": 202,    
    "Spell Channeling": 203, 
    "Lower Mana Cost": 201,    
    "Lower Reagent Cost": 202,
    "Faster Cast Recovery": 0, 
    "Spell Damage Increase": 0, 
    "Casting Focus": 0, 
    
    # --- SKILL GROUP 1 ---
    "Magery": 201, "Musicianship": 202, "Swordsmanship": 203, "Mace Fighting": 204, "Fencing": 205,
    # --- SKILL GROUP 2 ---
    "Provocation": 201, "Tactics": 202, "Spirit Speak": 203, "Animal Taming": 204, "Wrestling": 205,
    # --- SKILL GROUP 3 ---
    "Discordance": 201, "Animal Lore": 202, "Meditation": 203, "Stealth": 204, "Parrying": 205, "Focus": 206,
    # --- SKILL GROUP 4 ---
    "Anatomy": 201, "Eval Intelligence": 202, "Stealing": 203, "Veterinary": 204, "Necromancy": 205, "Bushido": 206, "Mysticism": 207,
    # --- SKILL GROUP 5 ---
    "Healing": 201, "Resisting Spells": 202, "Archery": 203, "Chivalry": 204, "Ninjitsu": 205, "Throwing": 206, "Peacemaking": 207,
    
    # --- COMBAT ---
    "Swing Speed Increase": 201, 
    "Damage Increase": 202,      
    "Balanced": 201,                
    "Defense Chance Increase": 202,  
    "Hit Chance Increase": 203,      
    "Velocity": 204,                 
    
    # --- HIT AREA EFFECTS (From Screenshot) ---
    "Hit Cold Area": 201,
    "Hit Energy Area": 202,
    "Hit Fire Area": 203,
    "Hit Physical Area": 204,
    "Hit Poison Area": 205,
    
    # --- HIT EFFECTS (From Screenshot) ---
    "Hit Dispel": 202,
    "Hit Fireball": 206,
    "Hit Harm": 207,
    "Hit Life Leech": 208,
    "Hit Lightning": 209,
    "Hit Lower Attack": 210,
    "Hit Lower Defense": 211,
    "Hit Magic Arrow": 212,
    "Hit Mana Leech": 213,
    "Hit Stamina Leech": 215,
    
    # --- MISC. ---
    "Luck": 201, 
    "Night Sight": 202, 
    "Reflect Physical Damage": 203, 
    
    # --- RESISTS (From Screenshot) ---
    "Cold Resist": 201,
    "Energy Resist": 202,
    "Fire Resist": 203,
    "Poison Resist": 204,
    "Physical Resist": 205,
    
    # --- STATS (From Screenshot) ---
    "Hit Point Increase": 201,
    "Mana Increase": 202,
    "Mana Regeneration": 203,
    "Stamina Regeneration": 204,
    "Hit Point Regeneration": 205,
    "Stamina Increase": 206,
    
    # --- SLAYERS (From Screenshot - Skipping 202 and 204) ---
    "Air Elemental Slayer": 201,
    "Blood Elemental Slayer": 203,
    "Dragon Slayer": 205,
    "Earth Elemental Slayer": 206,
    "Fire Elemental Slayer": 207,
    "Gargoyle Slayer": 208,
    "Lizardman Slayer": 209,
    "Ogre Slayer": 210,
    "Ophidian Slayer": 211,
    "Orc Slayer": 212,
    "Poison Elemental Slayer": 213,
    "Scorpion Slayer": 214,
    "Snake Slayer": 215,
    "Snow Elemental Slayer": 216,
    "Spider Slayer": 217,
    "Terathan Slayer": 218,
    "Troll Slayer": 219,
    "Water Elemental Slayer": 220,
    
    # --- SUPER SLAYERS (From Screenshot) ---
    "Arachnid Slayer": 201,
    "Demon Slayer": 202,
    "Elemental Slayer": 203,
    "Fey Slayer": 204,
    "Repond Slayer": 205,
    "Reptile Slayer": 206,
    "Undead Slayer": 207
}

# ---------------------------------------------------------
# STATE MANAGEMENT
# ---------------------------------------------------------
PRESET_CUSTOM = "Custom"
IMBUING_PRESETS = [
    {
        "Name": "Basic LRC",
        "Rows": [
            ("Lower Mana Cost", 7),
            ("Lower Reagent Cost", 17),
            ("Mana Regeneration", 1),
            ("Mana Increase", 7),
        ],
    }
]

state = {
    "Category": "Armor",
    "ItemGroup": "Armor",
    "ItemName": "Armor",
    "Exceptional": False,
    "CustomMode": False,
    "Whetstone": False,
    "MatCont": 0,
    "GemCont": 0,
    "GemBuffer": "0",
    "MaterialScroll": 0,
    "StaminaInput": "",
    "SSIInput": "",
    "CalcTicks": "0",
    "CalcSpeed": "0.00s",
    "CalcBaseSpeed": 0.0,
    "CalcSelectedSpeedCat": "None Selected",
    "CalcWeaponName": "Select Weapon",
    "Rows": [{"Prop": "None", "Val": 0} for _ in range(5)],
    "SelectedPreset": PRESET_CUSTOM,
    "PickerOpen": False,
    "PickerMode": None, 
    "ActiveRow": -1, 
    "SelectedPropGroup": "None",
    "PickerPage": 0,
    "Msg": "",
    "ScannedProps": {},
    "ImbueTarget": 0
}

# ---------------------------------------------------------
# CALCULATIONS 
# ---------------------------------------------------------
def GetActiveDB():
    if state["Category"] == "Ranged Weapon": return DB_RANGED
    if state["Category"] in ["One-Handed Melee", "Two-Handed Melee"]: return DB_MELEE
    if state["Category"] == "Shields": return DB_SHIELDS
    if state["Category"] == "Jewelry": return DB_JEWELS
    return DB_ARMOR

def GetDynamicMax(prop_name):
    db = GetActiveDB().get(prop_name)
    if not db: return 0
    base_max = db["Max"]
    
    if prop_name in ["Hit Mana Leech", "Hit Life Leech"] and state["Category"] in ["One-Handed Melee", "Two-Handed Melee", "Ranged Weapon"]:
        current_ssi = 0
        for r in state["Rows"]:
            if r["Prop"] == "Swing Speed Increase":
                current_ssi = r["Val"]
                break
                
        base_speed = WEAPON_SPEEDS.get(state["ItemName"], 3.25)
        base_ticks = base_speed * 4.0
        modified_ticks = math.floor( (base_ticks * 100.0) / (100.0 + current_ssi) )
        modified_speed = modified_ticks * 0.25
        
        max_leech = math.floor(modified_speed * 25.0)
        if state["Category"] == "Ranged Weapon":
            max_leech = math.floor(max_leech / 2.0)
            
        if max_leech > 100: max_leech = 100
        return max_leech
            
    return base_max

def PreUpdateLeeches():
    old_states = {}
    for i, r in enumerate(state["Rows"]):
        if r["Prop"] in ["Hit Mana Leech", "Hit Life Leech"]:
            old_states[i] = {"val": r["Val"], "max": GetDynamicMax(r["Prop"])}
    return old_states

def PostUpdateLeeches(old_states):
    for i, r in enumerate(state["Rows"]):
        if r["Prop"] in ["Hit Mana Leech", "Hit Life Leech"]:
            new_max = GetDynamicMax(r["Prop"])
            if i in old_states:
                old_val = old_states[i]["val"]
                old_max = old_states[i]["max"]

                if old_max > 0 and old_val >= old_max: r["Val"] = new_max
                elif r["Val"] > new_max: r["Val"] = new_max
            else:
                if r["Val"] > new_max: r["Val"] = new_max

def CalculateSwingSpeed():
    try: stam = float(state.get("StaminaInput", 0))
    except: stam = 0.0
    try: ssi = float(state.get("SSIInput", 0))
    except: ssi = 0.0
    
    base_sec = state.get("CalcBaseSpeed", 0.0)
    if base_sec == 0.0:
        state["CalcTicks"] = "0"
        state["CalcSpeed"] = "0.00s"
        return
        
    base_ticks = base_sec * 4.0
    stam_ticks = math.floor(stam / 30.0)
    
    hit_start = (base_ticks - stam_ticks) * (100.0 / (100.0 + ssi))
    ticks = int(math.floor(hit_start))
    if ticks < 5: ticks = 5
        
    state["CalcTicks"] = str(ticks)
    state["CalcSpeed"] = "{:.2f}s".format(ticks * 0.25)

def GetMaxWeight():
    cat = state["Category"]
    exc = state["Exceptional"]
    
    if cat in ["Shields", "Jewelry"]: return 500
    if cat in ["Armor", "One-Handed Melee"]: return 500 if exc else 450
    if cat == "Ranged Weapon": return 550 if exc else 500
    if cat == "Two-Handed Melee": return 600 if exc else 550
    return 500 if exc else 450

def GetRowWeight(row_idx):
    row = state["Rows"][row_idx]
    prop = row["Prop"]
    val = row["Val"]
    if prop == "None" or val == 0: return 0
    
    active_db = GetActiveDB()
    if prop not in active_db or prop not in BASE_PROPS: return 0
    
    if prop == "Mage Weapon":
        abs_val = abs(val)
        return (30 - abs_val) * 10
        
    dyn_max = GetDynamicMax(prop)
    if dyn_max <= 0: return 0
    
    base_weight = active_db[prop].get("Weight", BASE_PROPS[prop]["Weight"])
    return int(math.floor((float(val) / dyn_max) * base_weight))

def GetTotalWeight():
    return sum(GetRowWeight(i) for i in range(5))

def CompileIngredients():
    totals = {}
    for row in state["Rows"]:
        prop = row["Prop"]
        val = row["Val"]
        
        if prop == "None" or val == 0: continue
        
        if prop in state.get("ScannedProps", {}):
            if val <= state["ScannedProps"][prop]:
                continue
        
        dyn_max = GetDynamicMax(prop)
        if prop not in BASE_PROPS: continue

        if prop == "Mage Weapon":
            if val < -29 or val > -20: continue
        else:
            if dyn_max <= 0: continue
            if state.get("CustomMode", False) and val > dyn_max: continue
        
        primary = BASE_PROPS[prop].get("Primary") 
        gem = BASE_PROPS[prop].get("Gem")
        spec = BASE_PROPS[prop].get("Special")

        intensity_pct = 1.0
        if prop != "Mage Weapon":
            intensity_pct = float(val) / float(dyn_max)
        else:
            intensity_pct = float(abs(val) - 30) / float(-10)
            
        primary_amt = max(1, int(math.floor(intensity_pct * 5.0)))
        gem_amt = max(1, int(math.floor(intensity_pct * 10.0)))
        
        spec_amt = 0
        if intensity_pct > 0.90:
            threshold_val = 0.90
            special_ratio = (intensity_pct - threshold_val) / (1.0 - threshold_val)
            spec_amt = int(round(special_ratio * 10.0))
            if intensity_pct >= 1.0: spec_amt = 10
        
        if primary and primary != "None": totals[primary] = totals.get(primary, 0) + primary_amt
        if gem and gem != "None": totals[gem] = totals.get(gem, 0) + gem_amt
        if spec and spec != "None" and spec_amt > 0: totals[spec] = totals.get(spec, 0) + spec_amt
            
    return totals

def PullItems():
    needed = CompileIngredients()
    if not needed:
        DebugLog("PullItems: no required materials.")
        state["Msg"] = "Nothing to pull."
        return True

    try: buffer = int((str(state["GemBuffer"]).strip() or "0"))
    except: buffer = 0

    DebugLog(
        "PullItems: MatCont={} GemCont={} Reserve={} Needed={}".format(
            _debug_hex(state["MatCont"]),
            _debug_hex(state["GemCont"]),
            buffer,
            ", ".join(["{}:{}".format(k, v) for k, v in sorted(needed.items())])
        )
    )

    all_required_found = True
    reserve_low = False

    for item_name, amount in needed.items():
        if item_name not in INGREDIENT_GRAPHICS: continue

        is_gem = False
        is_primary = False

        for prop_data in BASE_PROPS.values():
            if prop_data.get("Gem") == item_name: is_gem = True
            if prop_data.get("Primary") == item_name: is_primary = True

        reserve_amt = buffer if (is_gem or is_primary) else 0
        desired_amt = amount + reserve_amt

        graphic_data, hue = INGREDIENT_GRAPHICS[item_name]
        if not isinstance(graphic_data, (tuple, list)): graphic_data = (graphic_data,)
        
        already_have = 0
        for item in Player.Backpack.Contains:
            if item.ItemID in graphic_data and item.Hue == hue:
                already_have += _item_amount(item)

        pull_amt = desired_amt - already_have
        DebugLog(
            "{}: required={} reserve={} desired={} backpack={} pull={} graphics={} hue={}".format(
                item_name,
                amount,
                reserve_amt,
                desired_amt,
                already_have,
                max(0, pull_amt),
                _debug_graphics(graphic_data),
                _debug_hex(hue)
            )
        )

        if pull_amt <= 0:
            DebugLog("{}: already ready in backpack.".format(item_name))
            continue

        if state["MatCont"] == 0 and state["GemCont"] == 0:
            if already_have < amount:
                all_required_found = False
                DebugLog("{}: no source containers and required amount is missing.".format(item_name), 33)
                Misc.SendMessage("Could not find enough {} (need {})".format(item_name, amount - already_have), 33)
            else:
                reserve_low = True
                DebugLog("{}: no source containers; required amount ready but reserve is low.".format(item_name), 55)
            continue

        if (is_gem or is_primary) and state["GemCont"] != 0:
            primary_cont = state["GemCont"]
            fallback_cont = state["MatCont"]
        else:
            primary_cont = state["MatCont"]
            fallback_cont = state["GemCont"]

        DebugLog(
            "{}: searching primary={} fallback={}".format(
                item_name,
                _debug_hex(primary_cont),
                _debug_hex(fallback_cont)
            )
        )

        remaining = pull_amt
        moved_amt = 0
        searched_containers = set()

        for source_cont in (primary_cont, fallback_cont):
            if source_cont == 0 or source_cont in searched_containers:
                continue
            searched_containers.add(source_cont)

            found_items = Items.FindAllByID(graphic_data, hue, source_cont, recursive=True)
            DebugLog(
                "{}: source {} has {} matching stack(s).".format(
                    item_name,
                    _debug_hex(source_cont),
                    len(found_items)
                )
            )

            for found_item in found_items:
                move_amt = min(remaining, _item_amount(found_item))
                DebugLog("{}: moving {} from {}.".format(item_name, move_amt, _debug_item(found_item)))
                move_success = Items.Move(found_item, Player.Backpack.Serial, move_amt)
                Misc.Pause(1200)
                if not move_success:
                    DebugLog("{}: move failed after Util.moveItem retries.".format(item_name), 33)
                    continue
                moved_amt += move_amt
                remaining -= move_amt
                if remaining <= 0:
                    break

            if remaining <= 0:
                break

        available_after_pull = already_have + moved_amt
        DebugLog(
            "{}: moved={} available_after_pull={} remaining_pull={}".format(
                item_name,
                moved_amt,
                available_after_pull,
                remaining
            )
        )
        if available_after_pull < amount:
            all_required_found = False
            DebugLog("{}: still missing required amount {}.".format(item_name, amount - available_after_pull), 33)
            Misc.SendMessage("Could not find enough {} (need {})".format(item_name, amount - available_after_pull), 33)
        elif remaining > 0:
            reserve_low = True
            DebugLog("{}: required amount ready, reserve short by {}.".format(item_name, remaining), 55)
            Misc.SendMessage("Could not fill {} reserve (need {})".format(item_name, remaining), 55)

    if not all_required_found:
        state["Msg"] = "Missing materials."
    elif reserve_low:
        state["Msg"] = "Items ready. Reserve low."
    else:
        state["Msg"] = "Items Pulled!"
    DebugLog("PullItems result: {}".format(state["Msg"]), 65 if all_required_found else 33)
    return all_required_found

def ReturnMats():
    if state["MatCont"] == 0 and state["GemCont"] == 0:
        state["Msg"] = "No Source set!"
        send_calculator()
        return
        
    state["Msg"] = "Returning Mats..."
    send_calculator() 
    
 
    Items.WaitForContents(Player.Backpack.Serial, 1000)
    
    items_moved = 0

    for mat_name, data in INGREDIENT_GRAPHICS.items():
        graphic_data, hue = data
        if not isinstance(graphic_data, (tuple, list)): 
            graphic_data = (graphic_data,)

        is_gem = False
        is_primary = False
        for prop_data in BASE_PROPS.values():
            if prop_data.get("Gem") == mat_name: is_gem = True
            if prop_data.get("Primary") == mat_name: is_primary = True

        if (is_gem or is_primary) and state["GemCont"] != 0:
            dest = state["GemCont"]
        elif not (is_gem or is_primary) and state["MatCont"] != 0:
            dest = state["MatCont"] 
        elif state["MatCont"] != 0:
            dest = state["MatCont"]
        elif state["GemCont"] != 0:
            dest = state["GemCont"]
        else:
            dest = 0
            
        if dest == 0: continue
        
        for g in graphic_data:
            while True:
                found = Items.FindByID(g, hue, Player.Backpack.Serial)
                if found:
                    Items.Move(found, dest, 0)
                    Misc.Pause(1000) 
                    items_moved += 1
                else:
                    break 
                    
    if items_moved == 0:
        state["Msg"] = "No mats to return."
    else:
        state["Msg"] = "Mats Returned!"
        
    send_calculator()

# ---------------------------------------------------------
# AUTO-READER ENGINE
# ---------------------------------------------------------
def AutoReadItem():
    state["Msg"] = "Target item to read..."
    send_calculator()
    item_serial = Target.PromptTarget("Select an item")
    if item_serial == -1: 
        state["Msg"] = "Targeting canceled."
        return
        
    state["ImbueTarget"] = item_serial

    item = Items.FindBySerial(item_serial)
    if not item: 
        state["Msg"] = "Item not found."
        return

    Items.WaitForProps(item, 1000)
    props = Items.GetPropStringList(item)

    if not props:
        state["Msg"] = "No properties found."
        return

    raw_name = props[0].lower()

    found_cat = "Armor"
    found_item_name = "Armor"
    found_group = "Armor"

    for w in WEAPON_SPEEDS.keys():
        if w.lower() in raw_name:
            found_item_name = w
            for cat, groups in ITEM_DB.items():
                for grp, items in groups.items():
                    if w in items:
                        found_cat = cat
                        found_group = grp
                        break
            break

    if found_cat == "Armor":
        if "shield" in raw_name or "buckler" in raw_name:
            found_cat = "Shields"
            found_item_name = "Shields"
            found_group = "Shields"
        elif "ring" in raw_name or "bracelet" in raw_name:
            found_cat = "Jewelry"
            found_item_name = "Jewelry"
            found_group = "Jewelry"

    state["Category"] = found_cat
    state["ItemName"] = found_item_name
    state["ItemGroup"] = found_group
    
    if found_item_name in WEAPON_SPEEDS:
        state["CalcWeaponName"] = found_item_name
        state["CalcBaseSpeed"] = WEAPON_SPEEDS[found_item_name]

    state["Exceptional"] = any("exceptional" in p.lower() for p in props)
 
    search_map = {}
    for k in BASE_PROPS.keys():
        if k != "None": search_map[k.lower()] = k
        
    search_map["defence chance increase"] = "Defense Chance Increase"
    search_map["lower requirement"] = "Lower Requirements"
    sorted_keys = sorted(search_map.keys(), key=len, reverse=True)

    skip_list = ["physical damage", "fire damage", "cold damage", "poison damage", "energy damage", "weapon damage", "weapon speed", "durability"]

    found_props = {}
    item_resists = {}

    for p in props:
        p_lower = p.lower()
        if any(skip in p_lower for skip in skip_list): continue
            
        for sk in sorted_keys:
            if sk in p_lower:
                nums = re.findall(r'[-]?\d+', p)
                if nums:
                    val = int(nums[0])
                    real_name = search_map[sk]
                    
                    if "Resist" in real_name: item_resists[real_name] = val
                    else: found_props[real_name] = val
                break 

    if found_cat in ["One-Handed Melee", "Two-Handed Melee", "Ranged Weapon"] and state["Exceptional"]:
        if "Damage Increase" not in found_props:
            state["Whetstone"] = True
        else:
            state["Whetstone"] = False
    else:
        state["Whetstone"] = False

    if found_cat == "Armor" and item_resists:
        total_resists = sum(item_resists.values())
        threshold = 35
        if "plate" in raw_name or "dragon" in raw_name: threshold = 40
        elif "studded" in raw_name or "chain" in raw_name or "ringmail" in raw_name: threshold = 36

        if total_resists > threshold:
            highest = max(item_resists, key=item_resists.get)
            found_props[highest] = item_resists[highest]
            
    elif found_cat != "Armor":
        for r_name, r_val in item_resists.items():
            found_props[r_name] = r_val

    for r in state["Rows"]:
        r["Prop"] = "None"
        r["Val"] = 0

    state["ScannedProps"] = {} 

    for r in state["Rows"]:
        r["Prop"] = "None"
        r["Val"] = 0

    row_idx = 0
    is_locked_di = (found_cat in ["One-Handed Melee", "Two-Handed Melee", "Ranged Weapon"] 
                    and state["Exceptional"] and not state["Whetstone"])

    if is_locked_di:
        state["Rows"][0]["Prop"] = "Damage Increase"
        if "Damage Increase" in found_props:
            di_val = found_props["Damage Increase"]
            state["Rows"][0]["Val"] = di_val
            state["ScannedProps"]["Damage Increase"] = di_val 

            if di_val > GetDynamicMax("Damage Increase"):
                state["CustomMode"] = True
                
            del found_props["Damage Increase"] 
        row_idx = 1

    for p_name, p_val in found_props.items():
        state["ScannedProps"][p_name] = p_val 

        if p_val > GetDynamicMax(p_name):
            state["CustomMode"] = True
            
        if row_idx >= 5: break
        state["Rows"][row_idx]["Prop"] = p_name
        state["Rows"][row_idx]["Val"] = p_val
        row_idx += 1

    PostUpdateLeeches(PreUpdateLeeches()) 
    state["Msg"] = "Item auto-populated!"

# ---------------------------------------------------------
# LIVE PROPERTY REFRESHER
# ---------------------------------------------------------
def RefreshItemProps(serial):
    """Silently re-reads the item to prevent double-imbuing and over-pulling!"""
    item = Items.FindBySerial(serial)
    if not item: return False
    
    Items.WaitForProps(item, 1000)
    props = Items.GetPropStringList(item)
    if not props: return False
    
    search_map = {}
    for k in BASE_PROPS.keys():
        if k != "None": search_map[k.lower()] = k
        
    search_map["defence chance increase"] = "Defense Chance Increase"
    search_map["lower requirement"] = "Lower Requirements"
    sorted_keys = sorted(search_map.keys(), key=len, reverse=True)

    skip_list = ["physical damage", "fire damage", "cold damage", "poison damage", "energy damage", "weapon damage", "weapon speed", "durability"]

    found_props = {}
    item_resists = {}

    for p in props:
        p_lower = p.lower()
        if any(skip in p_lower for skip in skip_list): continue
            
        for sk in sorted_keys:
            if sk in p_lower:
                nums = re.findall(r'[-]?\d+', p)
                if nums:
                    val = int(nums[0])
                    real_name = search_map[sk]
                    if "Resist" in real_name: item_resists[real_name] = val
                    else: found_props[real_name] = val
                break 

    if state.get("Category", "Armor") != "Armor":
        for r_name, r_val in item_resists.items():
            found_props[r_name] = r_val
    else:
        if item_resists:
            highest = max(item_resists, key=item_resists.get)
            found_props[highest] = item_resists[highest]

    state["ScannedProps"] = found_props
    return True
# ---------------------------------------------------------
# AUTO-IMBUE ENGINE
# ---------------------------------------------------------
def AutoImbue():
    DebugLog("AutoImbue clicked. Current target={}".format(_debug_hex(state.get("ImbueTarget", 0))), 65)
    if state.get("ImbueTarget", 0) == 0:
        state["Msg"] = "Target item to imbue!"
        send_calculator()
        state["ImbueTarget"] = Target.PromptTarget("Select item to imbue")
        if state["ImbueTarget"] == -1:
            state["ImbueTarget"] = 0
            state["Msg"] = "Imbuing canceled."
            DebugLog("AutoImbue canceled while selecting target.", 33)
            return

    state["Msg"] = "Starting Imbue Sequence..."
    send_calculator()
    DebugLog("AutoImbue starting. Target={}".format(_debug_hex(state["ImbueTarget"])), 65)

    if not RefreshItemProps(state["ImbueTarget"]):
        DebugLog("RefreshItemProps failed for target {}.".format(_debug_hex(state["ImbueTarget"])), 33)
        Misc.SendMessage("Failed to read item properties. Is it too far away?", 33)
        return

    if not PullItems():
        DebugLog("AutoImbue stopped during pre-pull.", 33)
        send_calculator()
        return
    
    props_to_imbue = []
    for row in state["Rows"]:
        prop = row["Prop"]
        val = row["Val"]
        if prop == "None" or val == 0: continue
        
        if prop in state.get("ScannedProps", {}):
            if val <= state["ScannedProps"][prop]:
                Misc.SendMessage("Skipping {} - Already at {}%!".format(prop, state["ScannedProps"][prop]), 69)
                continue
        props_to_imbue.append(row)
        
    if not props_to_imbue:
        Misc.SendMessage("Item already meets or exceeds all targeted properties!", 69)
        state["Msg"] = "Nothing to imbue."
        DebugLog("AutoImbue: no properties need imbuing after scan.", 55)
        return

    active_db = GetActiveDB()
    abort_sequence = False
    DebugLog("AutoImbue properties: {}".format(", ".join(["{}={}".format(r["Prop"], r["Val"]) for r in props_to_imbue])), 65)
    
    # --- MAIN PROPERTY LOOP ---
    for row in props_to_imbue:
        if abort_sequence: break
        
        target_prop = row["Prop"]
        target_val = row["Val"]
        target_group = active_db[target_prop]["Group"].upper() 
        
        if target_group == "CUSTOM PROPERTIES":
            Misc.SendMessage("Skipping {} (Non-Imbuable)".format(target_prop), 55)
            continue
            
        property_completed = False

        while not property_completed and not abort_sequence:

            Gumps.SendAction(0xf3e93, 0)
            Gumps.SendAction(0xf3e90, 0)
            Misc.Pause(500)
            
            Player.UseSkill("Imbuing")
            Target.WaitForTarget(2000, False)
            Misc.Pause(200) 
            Target.TargetExecute(state["ImbueTarget"])
            if not Gumps.WaitForGump(0xf3e93, 2000):
                Misc.SendMessage("Failed to open Imbuing! Is item valid?", 33)
                abort_sequence = True
                break
                
            Gumps.SendAction(0xf3e93, 1) # Click "Imbue Item" 
            Target.WaitForTarget(2000, False)
            Misc.Pause(200)
            Target.TargetExecute(state["ImbueTarget"])
            if not Gumps.WaitForGump(0xf3e90, 2000):
                Misc.SendMessage("Failed to open Categories menu!", 33)
                abort_sequence = True
                break

            Misc.SendMessage("Navigating to {}...".format(target_prop), 55)
            
            cat_btn = IMBUE_CATS.get(target_group)
            if not cat_btn or cat_btn == 0: 
                Misc.SendMessage("No mapped ID for Category: {}!".format(target_group), 33)
                abort_sequence = True
                break
                
            Gumps.SendAction(0xf3e90, cat_btn) 
            Gumps.WaitForGump(0xf3e90, 2000)
            
            item_cat = state["Category"]
            prop_btn = 0
            if item_cat in IMBUE_OVERRIDES and target_prop in IMBUE_OVERRIDES[item_cat]:
                prop_btn = IMBUE_OVERRIDES[item_cat][target_prop]
            else:
                prop_btn = IMBUE_PROPS.get(target_prop, 0)
                
            if not prop_btn or prop_btn == 0: 
                Misc.SendMessage("No mapped ID for Property: {}!".format(target_prop), 33)
                abort_sequence = True
                break
                
            Gumps.SendAction(0xf3e90, prop_btn) 
            Gumps.WaitForGump(0xf3e90, 2000) 
            
            # --- SMART INTENSITY STEPPER ---
            dyn_max = GetDynamicMax(target_prop)
            is_max = False
            
            if target_prop == "Mage Weapon":
                if target_val >= -20: is_max = True 
            elif target_val >= dyn_max:
                is_max = True
                
            if is_max:
                Gumps.SendAction(0xf3e90, 313)
                Gumps.WaitForGump(0xf3e90, 1500)
            else:
                max_loops = 50
                loops = 0
                intensity_confirmed = False
                fallback_used = False
                while loops < max_loops:
                    loops += 1
                    Misc.Pause(250)
                    
                    lines = Gumps.GetLineList(0xf3e90)
                    current_val = None
                    
                    for i, line in enumerate(lines):
                        if line.strip() in ["<", "<<", "<<<", ">", ">>", ">>>"]:
                            val_str = lines[i-1]
                            match = re.search(r'[-]?\d+', val_str)
                            if match:
                                current_val = int(match.group())
                                break

                    if current_val is None:
                        if not fallback_used:
                            fallback_used = True
                            start_val = BASE_PROPS.get(target_prop, {}).get("Step", 1)
                            steps = abs(target_val - start_val)
                            direction = 312 if target_val > start_val else 311
                            DebugLog(
                                "Could not read intensity for {}; using fallback start={} target={} steps={}".format(
                                    target_prop,
                                    start_val,
                                    target_val,
                                    steps
                                ),
                                55
                            )
                            for _ in range(steps):
                                Gumps.SendAction(0xf3e90, direction)
                                Gumps.WaitForGump(0xf3e90, 800)
                            intensity_confirmed = True
                            break
                        continue

                    if current_val == target_val:
                        intensity_confirmed = True
                        break

                    if current_val < target_val:
                        Gumps.SendAction(0xf3e90, 312)
                    elif current_val > target_val:
                        Gumps.SendAction(0xf3e90, 311)

                    Gumps.WaitForGump(0xf3e90, 1500)

                if not intensity_confirmed:
                    lines = Gumps.GetLineList(0xf3e90)
                    DebugLog(
                        "Could not confirm intensity for {} target={} last={} lines={}".format(
                            target_prop,
                            target_val,
                            current_val,
                            " | ".join([str(line) for line in lines])
                        ),
                        33
                    )
                    Misc.SendMessage("Could not set {} to {}. Aborting.".format(target_prop, target_val), 33)
                    abort_sequence = True
                    break

            # Execute Imbue & Retry Loop
            imbuing = True
            is_retry = False
            
            while imbuing:
                Journal.Clear()
                
                if is_retry:
                    Gumps.SendAction(0xf3e93, 4) # Click "Reimbue Last"
                    Gumps.WaitForGump(0xf3e93, 3000)
                else:
                    Gumps.SendAction(0xf3e90, 302) # Click "Imbue Item"
                    Gumps.WaitForGump(0xf3e93, 5000) 
                
                Misc.Pause(1000) 
                
                if Journal.Search("successfully imbue"):
                    Misc.SendMessage("Successfully imbued {}!".format(target_prop), 69)
                    
                    state["ScannedProps"][target_prop] = target_val

                    imbuing = False
                    property_completed = True
                    
                elif Journal.Search("attempt to imbue the item, but fail"):
                    Misc.SendMessage("Failed to imbue. Retrying...", 33)
                    is_retry = True
                    
                elif Journal.Search("do not have enough resources"):
                    DebugLog("Journal reported missing resources during imbue. Running PullItems again.", 55)
                    Misc.SendMessage("Out of buffer! Pulling safely...", 55)
                    Gumps.SendAction(0xf3e93, 0)
                    Gumps.SendAction(0xf3e90, 0)
                    Misc.Pause(500)
                    if not PullItems():
                        DebugLog("PullItems failed after journal missing-resource message.", 33)
                        abort_sequence = True
                    imbuing = False
                    
                else:
                    Misc.SendMessage("Imbuing halted. Check materials or caps.", 33)
                    imbuing = False
                    abort_sequence = True

# ---------------------------------------------------------
class MysticLlamasCalculator:
    GUMP_ID = 998880
    WEAPON_CATEGORIES = ["One-Handed Melee", "Two-Handed Melee", "Ranged Weapon"]
    TAB_WIDTH = 80
    PAGE_WIDTH = 584
    MATERIAL_ROWS_VISIBLE = 5
    WIDTH = TAB_WIDTH
    HEIGHT = 760

    def __init__(self):
        self.gump = None
        self._drawGump = None
        self._running = True
        self.bufferInput = None
        self.staminaInput = None
        self.ssiInput = None
        self.materialScrollArea = None
        self.materialTableWidth = 0
        self.materialQtyX = 0
        self.mainControls = []
        self.pickerControls = []
        self.rowControls = []
        self.pickerSlots = []
        self.controls = {}
        self._last_ui_snapshot = None
        self._active_picker_tab = False
        self._showGump()
        self.updateControls(force=True)

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            self.gump.tick()
            for subGump, _, _ in self.gump.subGumps:
                if subGump._running and not subGump.gump.IsDisposed:
                    subGump.tick()
            self.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        return True

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            try:
                self.gump.destroy()
            except Exception:
                pass
            self.gump = None
        API.Stop()

    def redraw(self):
        self.updateControls()

    def updateControls(self, force=False):
        if not self._running:
            return
        if not self.gump:
            return

        picker_visible = state.get("PickerOpen", False)
        if picker_visible:
            if not self._active_picker_tab:
                self.gump.setActiveTab("Picker")
            self._active_picker_tab = True
        else:
            if state.pop("PickerWasOpen", False):
                self.gump.setActiveTab(state.get("PickerReturnTab", "Imbuing"))
            self._active_picker_tab = False

        snapshot = self._make_ui_snapshot()
        if not force and snapshot == self._last_ui_snapshot:
            return
        self._last_ui_snapshot = snapshot

        self._resize(self.WIDTH, self.HEIGHT)
        if not picker_visible:
            self._update_options()
            self._update_item_selector()
            self._update_rows()
            self._update_materials()
            self._update_speed_calc()
        self._update_picker()
        self._set_status(state.get("Msg", ""))

    def _make_ui_snapshot(self):
        rows = tuple((row.get("Prop"), row.get("Val")) for row in state.get("Rows", []))
        materials = tuple(sorted(CompileIngredients().items()))
        return (
            state.get("PickerOpen", False),
            state.get("PickerMode"),
            state.get("PickerPage", 0),
            state.get("PickerReturnTab"),
            state.get("SelectedPropGroup"),
            state.get("Category"),
            state.get("ItemGroup"),
            state.get("ItemName"),
            state.get("CustomMode", False),
            state.get("Exceptional", False),
            state.get("Whetstone", False),
            state.get("SelectedPreset", PRESET_CUSTOM),
            state.get("ImbueTarget", 0),
            state.get("GemBuffer", "0"),
            state.get("MatCont", 0),
            state.get("GemCont", 0),
            state.get("CalcWeaponName", ""),
            state.get("StaminaInput", "0"),
            state.get("SSIInput", "0"),
            state.get("CalcTicks", ""),
            state.get("CalcSpeed", ""),
            state.get("Msg", ""),
            rows,
            materials,
        )

    def _showGump(self):
        g = Gump(self.WIDTH, self.HEIGHT, self._onClose, False, gumpId=self.GUMP_ID)
        self.gump = g
        try:
            g.gump.SetX(max(12, g.gump.GetX() - self.PAGE_WIDTH // 2))
        except Exception:
            pass

        imbueGump = g.addTabButton("Imbuing", "caster", self.PAGE_WIDTH, withStatus=True)
        self._drawGump = imbueGump
        imbueGump.addTitle("MYSTIC LLAMAS IMBUING", hue=Gump.hues["text"])
        self._draw_item_properties(imbueGump)
        self._draw_settings(imbueGump)
        self._draw_rows(imbueGump)
        self._draw_material_costs(imbueGump)

        speedGump = g.addTabButton("Swing Speed", "tracking", self.PAGE_WIDTH, withStatus=True)
        self._drawGump = speedGump
        speedGump.addTitle("SWING SPEED INCREASE", hue=Gump.hues["text"])
        self._draw_speed_calc(speedGump)

        pickerGump = g.createSubGump(self.PAGE_WIDTH, self.HEIGHT, "right", withStatus=True, alwaysVisible=False)
        pickerGump.gump.IsVisible = False
        g.tabGumps["Picker"] = pickerGump
        self._drawGump = pickerGump
        self._draw_picker(pickerGump)
        self._drawGump = None

        g.setActiveTab("Imbuing")
        self._set_status(state.get("Msg", ""))
        g.create()

    def _callback(self, fn):
        return self.gump.onClick(lambda: self._run_action(fn))

    def _set_status(self, text):
        if not self.gump:
            return
        self.gump.setStatus(text)
        for tabGump in self.gump.tabGumps.values():
            tabGump.setStatus(text)

    def _ui_gump(self):
        return self._drawGump or self.gump

    def _run_action(self, fn):
        try:
            self._sync_inputs()
            state["Msg"] = ""
            fn()
        except Exception as e:
            state["Msg"] = "Error: {}".format(e)
            API.SysMsg(traceback.format_exc(), 33)
        self.updateControls()

    def _resize(self, width, height):
        try:
            self.gump.gump.SetWidth(width)
            self.gump.gump.SetHeight(height)
        except Exception:
            pass

    def _remember(self, obj, group):
        controls = list(self._iter_controls(obj))
        if group == "main":
            self.mainControls.extend(controls)
        elif group == "picker":
            self.pickerControls.extend(controls)
        return obj

    def _iter_controls(self, obj):
        if obj is None:
            return
        if isinstance(obj, dict):
            for value in obj.values():
                for control in self._iter_controls(value):
                    yield control
            return
        if isinstance(obj, (list, tuple)):
            for value in obj:
                for control in self._iter_controls(value):
                    yield control
            return
        if hasattr(obj, "IsVisible"):
            yield obj

    def _set_visible(self, obj, visible):
        for control in self._iter_controls(obj):
            try:
                control.IsVisible = visible
            except Exception:
                pass

    def _set_text(self, control, text):
        if not control:
            return
        text = str(text)
        try:
            if hasattr(control, "SetText"):
                control.SetText(text)
            else:
                control.Text = text
        except Exception:
            try:
                control.Text = text
            except Exception:
                pass

    def _set_hue(self, control, hue):
        if not control:
            return
        try:
            control.Hue = hue
        except Exception:
            pass

    def _set_checked(self, control, checked):
        if not control:
            return
        try:
            if hasattr(control, "SetIsChecked"):
                control.SetIsChecked(checked)
            else:
                control.IsChecked = checked
        except Exception:
            try:
                control.IsChecked = checked
            except Exception:
                pass

    def _set_input_text(self, control, text):
        self._set_text(control, text)

    def _addPanel(self, x, y, width, height, title=None, group="main"):
        panel = self._ui_gump().addPanel(x, y, width, height, title, withTexture=True)
        self._remember(panel["elements"], group)
        return panel

    def _addFlatRow(self, x, y, width, height, group="main"):
        ui = self._ui_gump()
        row = ui.addColorBox(x, y, height, width, Gump.theme["row"], 0.42, withTexture=False)
        line = ui.addColorBox(x, y + height - 1, 1, width, "#000000", 0.32, withTexture=False)
        return self._remember([row, line], group)

    def _addLabel(self, text, x, y, hue=None, group="main"):
        return self._remember(self._ui_gump().addLabel(text, x, y, hue), group)

    def _addButton(self, text, x, y, width, height=24, callback=None, fontSize=11, group=None):
        cb = self._callback(callback) if callback else None
        ui = self._ui_gump()
        top_height = max(1, int(height * 0.42))
        bottom_height = max(1, height - 4 - top_height)
        parts = [
            ui.addColorBox(x + 2, y + 4, height - 2, width, Gump.theme["buttonShadow"], 0.55, withTexture=False),
            ui.addColorBox(x, y, height, width, Gump.theme["buttonFrame"], 1, withTexture=False),
            ui.addColorBox(x + 1, y + 1, height - 2, width - 2, Gump.theme["buttonInset"], 1, withTexture=False),
            ui.addColorBox(x + 2, y + 2, top_height, width - 4, Gump.theme["buttonHighlight"], 0.9, withTexture=True),
            ui.addColorBox(x + 2, y + 2 + top_height, bottom_height, width - 4, Gump.theme["buttonFill"], 0.95, withTexture=True),
            ui.addColorBox(x + 2, y + 2, 1, width - 4, "#ffffff", 0.14, withTexture=False),
            ui.addColorBox(x + 2, y + height - 2, 1, width - 4, "#000000", 0.6, withTexture=False),
        ]
        hover = ui.addColorBox(x + 2, y + 2, height - 4, width - 4, Gump.theme["frameHighlight"], 0.18, withTexture=False)
        hover.IsVisible = False

        hitTarget = API.CreateGumpColorBox(0, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(width)
        hitTarget.SetHeight(height)
        if cb:
            API.AddControlOnClick(hitTarget, cb)
        ui.gump.Add(hitTarget)

        label = ui.addTtfLabel(text, x, y, width, height, fontSize, Gump.theme["buttonText"], "center", cb)
        ui.hoverControls.append({"targets": [hitTarget, label], "hover": hover})
        control = {"parts": parts, "hover": hover, "hitTarget": hitTarget, "label": label}
        if group:
            self._remember(control, group)
        return control

    def _addMaxButton(self, x, y, callback, group="main"):
        cb = self._callback(callback) if callback else None
        return self._remember(self._ui_gump().addButton("", x, y, "radioGreen", cb), group)

    def _set_button_text(self, control, text):
        if control:
            self._set_text(control.get("label"), text)

    def _addSettingAction(self, text, x, y, callback, group="main"):
        cb = self._callback(callback) if callback else None
        ui = self._ui_gump()
        icon = ui.addButton("", x, y, "radioBlue", cb)
        label = ui.addLabel(text, x + 24, y + 2, Gump.hues["text"])
        if cb:
            API.AddControlOnClick(label, cb)
        return self._remember({"icon": icon, "label": label}, group)

    def _addInput(self, defaultValue, x, y, minValue=0, maxValue=120, width=60, height=24, group="main"):
        return self._remember(
            self._ui_gump().addSkillTextBox(defaultValue, x, y, minValue, maxValue, width, height),
            group,
        )

    def _addRadio(self, label, x, y, isChecked, callback, hue=None, group="main"):
        radio_group = {
            "Custom": 5101,
            "Exceptional": 5102,
            "Whetstone": 5103,
        }.get(label, 5199)
        return self._remember(
            self._ui_gump().addRadio(label, x, y, radio_group, isChecked, self._callback(callback), hue),
            group,
        )

    def _addReadOnlyRadio(self, label, x, y, isChecked, hue=None, group="main"):
        radio_group = {
            "Custom": 5101,
            "Exceptional": 5102,
            "Whetstone": 5103,
        }.get(label, 5199)
        return self._remember(
            self._ui_gump().addRadio(label, x, y, radio_group, isChecked, None, hue),
            group,
        )

    def _draw_item_properties(self, g):
        panel = self._addPanel(12, 42, 436, 146, "Selected Item")
        x = panel["x"] + 8
        y = panel["y"] + 6
        for row_y in (y - 3, y + 31, y + 57, y + 83):
            self._addFlatRow(x - 4, row_y, panel["width"] - 8, 24, "main")

        self._addSettingAction("Select item", x + 4, y, AutoReadItem, group="main")
        self.controls["targetLabel"] = self._addLabel("", x + 134, y + 2, Gump.hues["muted"])

        type_y = y + 34
        self._addLabel("Category", x, type_y, Gump.hues["muted"])
        self.controls["categoryLabel"] = self._addLabel("", x + 78, type_y, Gump.hues["text"])
        self._addLabel("Group", x, type_y + 27, Gump.hues["muted"])
        self.controls["groupLabel"] = self._addLabel("", x + 78, type_y + 27, Gump.hues["text"])
        self._addLabel("Base Item", x, type_y + 54, Gump.hues["muted"])
        self.controls["itemLabel"] = self._addLabel("", x + 78, type_y + 54, Gump.hues["text"])

        settings_x = x + 232
        self.controls["customCheck"] = self._addReadOnlyRadio("Custom", settings_x, type_y, state.get("CustomMode", False), Gump.hues["muted"])
        self.controls["exceptionalCheck"] = self._addReadOnlyRadio("Exceptional", settings_x, type_y + 27, state.get("Exceptional", False), Gump.hues["muted"])
        self.controls["whetstoneCheck"] = self._addReadOnlyRadio("Whetstone", settings_x, type_y + 54, state.get("Whetstone", False), Gump.hues["muted"])

    def _update_options(self):
        self._set_checked(self.controls["customCheck"], state.get("CustomMode", False))
        self._set_checked(self.controls["exceptionalCheck"], state.get("Exceptional", False))
        self._set_checked(self.controls["whetstoneCheck"], state.get("Whetstone", False))
        target = state.get("ImbueTarget", 0)
        target_text = "Target: 0x{:X}".format(target) if target else "No imbue target"
        self._set_text(self.controls["targetLabel"], target_text)

    def _update_item_selector(self):
        self._set_text(self.controls["categoryLabel"], state["Category"])
        self._set_text(self.controls["groupLabel"], state["ItemGroup"])
        self._set_text(self.controls["itemLabel"], state["ItemName"])

    def _draw_rows(self, g):
        panel = self._addPanel(12, 322, 436, 206, "Properties")
        x = panel["x"] + 8
        y = panel["y"] + 5
        self._addLabel("Property", x + 90, y, Gump.hues["muted"])
        self._addLabel("Val", x + 240, y, Gump.hues["muted"])
        self._addLabel("Weight", x + 328, y, Gump.hues["muted"])
        self._addButton("Calc", x + 372, y - 1, 44, height=18, callback=self._recalculate_materials, fontSize=9, group="main")
        for i, row in enumerate(state["Rows"]):
            row_y = y + 20 + i * 23
            row_control = {
                "row": self._addFlatRow(x - 4, row_y - 3, panel["width"] - 8, 22, "main"),
                "select": self._addButton("", x + 8, row_y - 1, 204, height=20, callback=lambda idx=i: self._open_property_picker(idx), fontSize=10),
                "locked": self._addLabel("", x + 10, row_y + 2, Gump.hues["muted"], group=None),
                "input": self._addInput(str(row["Val"]), x + 230, row_y - 1, 0, 999, width=50, height=20, group=None),
                "max": self._addMaxButton(x + 294, row_y - 1, lambda idx=i: self._max_row(idx), group=None),
                "weight": self._addLabel("", x + 364, row_y + 2, Gump.hues["text"], group=None),
            }
            self.rowControls.append(row_control)
        self._addLabel("Total Weight", x + 230, y + 142, Gump.hues["muted"])
        self.controls["totalWeightLabel"] = self._addLabel("", x + 334, y + 142, Gump.hues["text"])
        preset_y = y + 164
        self._addLabel("Preset", x, preset_y + 2, Gump.hues["muted"])
        selected_preset = state.get("SelectedPreset", PRESET_CUSTOM)
        self.controls["presetCustom"] = self._addRadio(
            PRESET_CUSTOM,
            x + 62,
            preset_y,
            selected_preset == PRESET_CUSTOM,
            lambda: self._apply_preset(PRESET_CUSTOM),
            group="main",
        )
        self.controls["presetBasicLrc"] = self._addRadio(
            "Basic LRC",
            x + 160,
            preset_y,
            selected_preset == "Basic LRC",
            lambda: self._apply_preset("Basic LRC"),
            group="main",
        )

    def _update_rows(self):
        main_visible = True
        for i, row in enumerate(state["Rows"]):
            controls = self.rowControls[i]
            locked = self._is_locked_row(i)
            select_label = row["Prop"] if row["Prop"] != "None" else "Select property"
            self._set_visible(controls["row"], main_visible)
            self._set_visible(controls["select"], main_visible and not locked)
            self._set_visible(controls["max"], main_visible and not locked)
            self._set_visible(controls["locked"], main_visible and locked)
            self._set_visible(controls["input"], main_visible)
            self._set_visible(controls["weight"], main_visible)
            self._set_button_text(controls["select"], select_label)
            self._set_text(controls["locked"], "{} (Locked)".format(row["Prop"]))
            self._set_input_text(controls["input"], row["Val"])
        self._set_text(controls["weight"], GetRowWeight(i))
        self._set_text(self.controls["totalWeightLabel"], str(GetTotalWeight()) + " / " + str(GetMaxWeight()))
        selected_preset = state.get("SelectedPreset", PRESET_CUSTOM)
        self._set_checked(self.controls.get("presetCustom"), selected_preset == PRESET_CUSTOM)
        self._set_checked(self.controls.get("presetBasicLrc"), selected_preset == "Basic LRC")

    def _draw_settings(self, g):
        panel = self._addPanel(12, 198, 436, 110, "Settings")
        x = panel["x"] + 8
        y = panel["y"] + 8
        for row_y in (y - 3, y + 24, y + 51):
            self._addFlatRow(x - 3, row_y, panel["width"] - 10, 24, "main")
        self._addLabel("Reserve", x, y, Gump.hues["muted"])
        self.bufferInput = self._addInput(str(state.get("GemBuffer", "0") or "0"), x + 66, y - 3, 0, 999, width=48, height=23)
        self.controls["startImbuingButton"] = self._addButton("Start Imbuing", x + 282, y - 3, 124, height=24, callback=AutoImbue, fontSize=11, group="main")
        self.controls["matButton"] = self._addSettingAction("", x + 4, y + 27, lambda: self._target_container("MatCont", "Select Material Container"), group="main")
        self.controls["gemButton"] = self._addSettingAction("", x + 4, y + 54, lambda: self._target_container("GemCont", "Select Gem Container"), group="main")

    def _draw_material_costs(self, g):
        panel = self._addPanel(12, 542, 436, 140, "Materials Cost")
        x = panel["x"] + 8
        y = panel["y"] + 3
        scroll_y = y + 20
        scroll_width = panel["width"] - 16
        scroll_height = 82
        self.materialTableWidth = scroll_width - 18
        self.materialQtyX = self.materialTableWidth - 58
        self._addLabel("Material", x, y, Gump.hues["muted"])
        self._addLabel("Qty", x + self.materialQtyX, y, Gump.hues["muted"])
        self.controls["noMaterialsLabel"] = self._addLabel("", x, y + 24, Gump.hues["muted"], group=None)
        self.materialScrollArea = API.CreateGumpScrollArea(x - 4, scroll_y, scroll_width, scroll_height)
        self._ui_gump().gump.Add(self.materialScrollArea)
        self._remember(self.materialScrollArea, "main")
        self.controls["moreMaterialsLabel"] = self._addLabel("", x, scroll_y + scroll_height + 4, Gump.hues["muted"], group=None)

    def _update_materials(self):
        main_visible = True
        self._set_input_text(self.bufferInput, state.get("GemBuffer", "0") or "0")
        self._set_button_text(self.controls["matButton"], self._container_text("Mats", state.get("MatCont", 0)))
        self._set_button_text(self.controls["gemButton"], self._container_text("Gems", state.get("GemCont", 0)))
        items = sorted(CompileIngredients().items())
        self._set_visible(self.controls["noMaterialsLabel"], main_visible and not items)
        self._set_text(self.controls["noMaterialsLabel"], "No materials required.")
        if self.materialScrollArea:
            self.materialScrollArea.Clear()
            for index, (name, amount) in enumerate(items):
                row_y = index * 16
                row_bg = API.CreateGumpColorBox(0.42, Gump.theme["row"])
                row_bg.SetX(0)
                row_bg.SetY(row_y)
                row_bg.SetWidth(self.materialTableWidth)
                row_bg.SetHeight(15)
                self.materialScrollArea.Add(row_bg)
                line = API.CreateGumpColorBox(0.32, "#000000")
                line.SetX(0)
                line.SetY(row_y + 15)
                line.SetWidth(self.materialTableWidth)
                line.SetHeight(1)
                self.materialScrollArea.Add(line)
                name_label = API.CreateGumpLabel(name, Gump.hues["text"])
                name_label.SetX(4)
                name_label.SetY(row_y)
                self.materialScrollArea.Add(name_label)
                amount_label = API.CreateGumpLabel(str(amount), Gump.hues["text"])
                amount_label.SetX(self.materialQtyX)
                amount_label.SetY(row_y)
                self.materialScrollArea.Add(amount_label)
        overflow = len(items) > self.MATERIAL_ROWS_VISIBLE
        self._set_text(self.controls["moreMaterialsLabel"], "{} material{}".format(len(items), "" if len(items) == 1 else "s"))
        self._set_visible(self.controls["moreMaterialsLabel"], main_visible and overflow)

    def _recalculate_materials(self):
        state["MaterialScroll"] = 0
        state["Msg"] = "Material costs recalculated."

    def _draw_speed_calc(self, g):
        panel = self._addPanel(12, 42, 324, 126, "Swing Speed")
        x = panel["x"]
        y = panel["y"] + 8
        self.controls["weaponButton"] = self._addButton("", x, y - 4, 180, callback=lambda: self._open_picker("SpeedCategories"), group="speed")
        self._addLabel("Stam", x + 194, y, Gump.hues["muted"], group="speed")
        self.staminaInput = self._addInput(str(state.get("StaminaInput", "") or "0"), x + 234, y - 3, 0, 999, width=46, height=23, group="speed")
        self._addLabel("SSI", x, y + 34, Gump.hues["muted"], group="speed")
        self.ssiInput = self._addInput(str(state.get("SSIInput", "") or "0"), x + 34, y + 62, 0, 999, width=46, height=23, group="speed")
        self._addButton("Calc", x + 34, y + 31, 52, callback=CalculateSwingSpeed, group="speed")
        self._addLabel("Ticks", x + 102, y + 34, Gump.hues["muted"], group="speed")
        self.controls["ticksLabel"] = self._addLabel("", x + 146, y + 34, Gump.hues["text"], group="speed")
        self._addLabel("Speed", x + 202, y + 34, Gump.hues["muted"], group="speed")
        self.controls["speedLabel"] = self._addLabel("", x + 252, y + 34, Gump.hues["text"], group="speed")
        self._addButton("Auto Imbue", x + 202, y + 62, 92, callback=AutoImbue, group="speed")

    def _update_speed_calc(self):
        self._set_button_text(self.controls["weaponButton"], state.get("CalcWeaponName", "Select Weapon"))
        self._set_input_text(self.staminaInput, state.get("StaminaInput", "") or "0")
        self._set_input_text(self.ssiInput, state.get("SSIInput", "") or "0")
        self._set_text(self.controls["ticksLabel"], state["CalcTicks"])
        self._set_text(self.controls["speedLabel"], state["CalcSpeed"])

    def _draw_picker(self, g):
        panel = self._addPanel(12, 42, 436, 520, None, group="picker")
        x = panel["x"]
        y = panel["y"] + 2
        self.controls["pickerTitle"] = self._addLabel("", x, panel["y"] - 20, Gump.hues["text"], group="picker")
        for visible_index in range(ITEMS_PER_PAGE):
            row_y = y + visible_index * 24
            slot = {
                "button": self._addButton("", x + 2, row_y - 2, panel["width"] - 4, height=22, callback=lambda idx=visible_index: self._select_picker_visible(idx), fontSize=10, group="picker"),
                "label": self._addLabel("", x + 8, row_y + 3, Gump.hues["muted"], group="picker"),
            }
            self.pickerSlots.append(slot)
        nav_y = panel["y"] + panel["height"] - 52
        self.controls["prevButton"] = self._addButton("<", x, nav_y, 32, callback=lambda: self._change_page(-1), group="picker")
        self.controls["pageLabel"] = self._addLabel("", x + 58, nav_y + 4, Gump.hues["muted"], group="picker")
        self.controls["nextButton"] = self._addButton(">", x + 152, nav_y, 32, callback=lambda: self._change_page(1), group="picker")
        self.controls["backButton"] = self._addButton("Back", x, nav_y + 28, 72, callback=lambda: self._open_picker(self._back_target()), group="picker")
        self.controls["closePickerButton"] = self._addButton("Close", x + 142, nav_y + 28, 72, callback=self._close_picker, group="picker")

    def _update_picker(self):
        picker_visible = state.get("PickerOpen", False)
        if not picker_visible:
            self._set_visible(self.pickerControls, False)
            return

        self._set_visible(self.pickerControls, True)
        items = self._picker_items()
        total_pages = max(1, int(math.ceil(float(len(items)) / ITEMS_PER_PAGE)))
        state["PickerPage"] = max(0, min(state.get("PickerPage", 0), total_pages - 1))
        start = state["PickerPage"] * ITEMS_PER_PAGE
        end = min(start + ITEMS_PER_PAGE, len(items))
        self._set_text(self.controls["pickerTitle"], self._picker_title())
        for visible_index, slot in enumerate(self.pickerSlots):
            item_index = start + visible_index
            has_item = item_index < end
            if not has_item:
                self._set_visible(slot, False)
                continue
            item_name = items[item_index]
            is_header = item_name in ["ONE-HANDED MELEE", "TWO-HANDED MELEE", "RANGED / THROWING"]
            is_locked_custom = state["PickerMode"] == "PropertyGroup" and item_name == "CUSTOM PROPERTIES" and not state.get("CustomMode", False)
            if is_header or is_locked_custom:
                self._set_visible(slot["button"], False)
                self._set_visible(slot["label"], True)
                self._set_text(slot["label"], item_name)
                self._set_hue(slot["label"], 33 if is_header else Gump.hues["muted"])
            else:
                self._set_visible(slot["button"], True)
                self._set_visible(slot["label"], False)
                self._set_button_text(slot["button"], item_name)
        self._set_visible(self.controls["prevButton"], total_pages > 1 and state["PickerPage"] > 0)
        self._set_visible(self.controls["nextButton"], total_pages > 1 and state["PickerPage"] < total_pages - 1)
        self._set_text(self.controls["pageLabel"], "Pg {} / {}".format(state["PickerPage"] + 1, total_pages))
        self._set_visible(self.controls["pageLabel"], total_pages > 1)
        back = self._back_target()
        self._set_visible(self.controls["backButton"], back is not None)
        self._set_visible(self.controls["closePickerButton"], True)

    def _sync_inputs(self):
        if self.bufferInput:
            state["GemBuffer"] = (str(self.bufferInput.Text).strip() or "0")
        if self.staminaInput:
            state["StaminaInput"] = str(self.staminaInput.Text)
        if self.ssiInput:
            state["SSIInput"] = str(self.ssiInput.Text)
        for i, controls in enumerate(self.rowControls):
            if i >= len(state["Rows"]):
                continue
            box = controls["input"]
            prop = state["Rows"][i]["Prop"]
            if prop == "None":
                continue
            new_val = self._clamp_value(prop, self._parse_int(box.Text, state["Rows"][i]["Val"]))
            if state["Rows"][i]["Val"] != new_val:
                state["SelectedPreset"] = PRESET_CUSTOM
            state["Rows"][i]["Val"] = new_val

    def _input_bounds(self, prop):
        if prop == "Mage Weapon":
            return -29, -20
        return 0, 999

    def _parse_int(self, value, default=0):
        try:
            return int(float(str(value).strip()))
        except Exception:
            return default

    def _clamp_value(self, prop, value):
        if prop == "Mage Weapon":
            return min(max(value, -29), -20)
        if state.get("CustomMode", False) and prop not in ["Hit Life Leech", "Hit Mana Leech"]:
            return max(0, value)
        maximum = GetDynamicMax(prop)
        if maximum <= 0:
            return max(0, value)
        return min(max(0, value), maximum)

    def _max_row(self, idx):
        prop = state["Rows"][idx]["Prop"]
        if prop in GetActiveDB():
            state["SelectedPreset"] = PRESET_CUSTOM
            old_states = PreUpdateLeeches()
            state["Rows"][idx]["Val"] = GetDynamicMax(prop)
            PostUpdateLeeches(old_states)

    def _apply_preset(self, preset_name):
        state["SelectedPreset"] = preset_name
        if preset_name == PRESET_CUSTOM:
            return

        preset = next((p for p in IMBUING_PRESETS if p["Name"] == preset_name), None)
        if not preset:
            state["SelectedPreset"] = PRESET_CUSTOM
            return

        old_states = PreUpdateLeeches()
        rows = []
        active_db = GetActiveDB()
        for prop, value in preset["Rows"]:
            if prop in active_db and prop in BASE_PROPS:
                rows.append({"Prop": prop, "Val": self._clamp_value(prop, value)})
            else:
                rows.append({"Prop": "None", "Val": 0})
        while len(rows) < len(state["Rows"]):
            rows.append({"Prop": "None", "Val": 0})
        state["Rows"] = rows[: len(state["Rows"])]
        PostUpdateLeeches(old_states)

    def _toggle_exceptional(self):
        old_states = PreUpdateLeeches()
        state["Exceptional"] = not state["Exceptional"]
        if not state["Exceptional"]:
            state["Whetstone"] = False
        PostUpdateLeeches(old_states)

    def _toggle_custom(self):
        old_states = PreUpdateLeeches()
        state["CustomMode"] = not state["CustomMode"]
        if not state["CustomMode"]:
            for row in state["Rows"]:
                row["Val"] = self._clamp_value(row["Prop"], row["Val"])
        PostUpdateLeeches(old_states)

    def _toggle_whetstone(self):
        old_states = PreUpdateLeeches()
        state["Whetstone"] = not state["Whetstone"]
        PostUpdateLeeches(old_states)

    def _target_container(self, key, prompt):
        state["Msg"] = prompt + "..."
        self.updateControls()
        target = Target.PromptTarget(prompt)
        if target != -1:
            state[key] = target
            state["Msg"] = "{} set.".format(prompt.replace("Select ", ""))
        else:
            state["Msg"] = "Targeting canceled."

    def _container_text(self, label, serial):
        if label == "Mats":
            return "Selected material container (0x{:X})".format(serial) if serial else "Select material container"
        if label == "Gems":
            return "Selected gem container (0x{:X})".format(serial) if serial else "Select gem container"
        if serial:
            return "{} 0x{:X}".format(label, serial)
        return "Set " + label

    def _open_property_picker(self, idx):
        state["SelectedPreset"] = PRESET_CUSTOM
        state["ActiveRow"] = idx
        self._open_picker("PropertyGroup")

    def _open_picker(self, mode):
        state["PickerOpen"] = True
        state["PickerWasOpen"] = True
        state["PickerReturnTab"] = "Swing Speed" if mode.startswith("Speed") else "Imbuing"
        state["PickerMode"] = mode
        state["PickerPage"] = 0
        self.gump.setActiveTab("Picker")

    def _close_picker(self):
        state["PickerOpen"] = False

    def _change_page(self, delta):
        state["PickerPage"] = max(0, state.get("PickerPage", 0) + delta)

    def _select_picker_visible(self, visible_index):
        self._select_picker(state.get("PickerPage", 0) * ITEMS_PER_PAGE + visible_index)

    def _picker_items(self):
        mode = state.get("PickerMode")
        if mode == "Category":
            return CATEGORIES
        if mode == "ItemGroup":
            if state["Category"] == "One-Handed Melee":
                return WEAPON_GROUPS_1H
            if state["Category"] == "Two-Handed Melee":
                return WEAPON_GROUPS_2H
            if state["Category"] == "Ranged Weapon":
                return WEAPON_GROUPS_RANGED
            return []
        if mode == "BaseItem":
            return sorted(ITEM_DB.get(state["Category"], {}).get(state["ItemGroup"], []))
        if mode == "PropertyGroup":
            active_db = GetActiveDB()
            groups_present = set(v["Group"] for v in active_db.values())
            return [g for g in GROUP_ORDER if g in groups_present]
        if mode == "Property":
            active_db = GetActiveDB()
            return sorted([k for k, v in active_db.items() if v.get("Group") == state["SelectedPropGroup"]])
        if mode == "SpeedCategories":
            return SPEED_KEYS
        if mode == "SpeedWeapons":
            return sorted(SPEED_MENU[state["CalcSelectedSpeedCat"]])
        return []

    def _select_picker(self, idx):
        items = self._picker_items()
        if idx >= len(items):
            return
        selection = items[idx]
        old_states = PreUpdateLeeches()
        mode = state.get("PickerMode")
        if mode == "Category":
            state["Category"] = selection
            state["ScannedProps"] = {}
            for row in state["Rows"]:
                row["Prop"] = "None"
                row["Val"] = 0
            if selection in SINGLE_TIER_CATS:
                state["ItemGroup"] = selection
                state["ItemName"] = selection
                state["PickerOpen"] = False
            else:
                state["ItemGroup"] = "Choose One"
                state["ItemName"] = "Choose One"
                state["PickerMode"] = "ItemGroup"
                state["PickerPage"] = 0
        elif mode == "ItemGroup":
            if selection.startswith("ONE-") or selection.startswith("TWO-") or selection.startswith("RANGED"):
                return
            state["ItemGroup"] = selection
            state["ItemName"] = "Choose One"
            state["PickerMode"] = "BaseItem"
            state["PickerPage"] = 0
        elif mode == "BaseItem":
            state["ItemName"] = selection
            if selection in WEAPON_SPEEDS:
                state["CalcWeaponName"] = selection
                state["CalcBaseSpeed"] = WEAPON_SPEEDS[selection]
                CalculateSwingSpeed()
            state["ScannedProps"] = {}
            state["PickerOpen"] = False
        elif mode == "PropertyGroup":
            if selection == "CUSTOM PROPERTIES" and not state.get("CustomMode", False):
                state["Msg"] = "Enable Custom first."
                return
            state["SelectedPropGroup"] = selection
            state["PickerMode"] = "Property"
            state["PickerPage"] = 0
        elif mode == "Property":
            target_row = state["ActiveRow"]
            if target_row < 0:
                return
            state["Rows"][target_row]["Prop"] = selection
            if selection == "Mage Weapon":
                state["Rows"][target_row]["Val"] = -29
            elif selection in BASE_PROPS:
                state["Rows"][target_row]["Val"] = BASE_PROPS[selection]["Step"]
            else:
                state["Rows"][target_row]["Val"] = 1
            state["PickerOpen"] = False
        elif mode == "SpeedCategories":
            state["CalcSelectedSpeedCat"] = selection
            state["PickerMode"] = "SpeedWeapons"
            state["PickerPage"] = 0
        elif mode == "SpeedWeapons":
            state["CalcWeaponName"] = selection
            state["CalcBaseSpeed"] = WEAPON_SPEEDS[selection]
            state["PickerOpen"] = False
            CalculateSwingSpeed()
        PostUpdateLeeches(old_states)

    def _picker_title(self):
        mode = state.get("PickerMode")
        if mode == "Category":
            return "Select Category"
        if mode == "ItemGroup":
            return "Select Group"
        if mode == "BaseItem":
            return "Select Item"
        if mode == "PropertyGroup":
            return "Property Group"
        if mode == "Property":
            return state.get("SelectedPropGroup", "Property")
        if mode == "SpeedCategories":
            return "Base Speed"
        if mode == "SpeedWeapons":
            return state.get("CalcSelectedSpeedCat", "Weapon")
        return "Select"

    def _back_target(self):
        mode = state.get("PickerMode")
        if mode == "Property":
            return "PropertyGroup"
        if mode == "BaseItem":
            return "ItemGroup"
        if mode == "ItemGroup":
            return "Category"
        if mode == "SpeedWeapons":
            return "SpeedCategories"
        return None

    def _is_locked_row(self, idx):
        return (
            idx == 0
            and state.get("Category") in self.WEAPON_CATEGORIES
            and state.get("Exceptional")
            and not state.get("Whetstone")
            and state["Rows"][0]["Prop"] == "Damage Increase"
        )

    def _showGump(self):
        g = Gump(self.WIDTH, self.HEIGHT, self._onClose, False, gumpId=self.GUMP_ID)
        self.gump = g
        try:
            g.gump.SetX(max(12, g.gump.GetX() - self.PAGE_WIDTH // 2))
        except Exception:
            pass

        imbueGump = g.addTabButton("Imbuing", "caster", self.PAGE_WIDTH, withStatus=False)
        self._drawGump = imbueGump
        imbueGump.addTitle("MYSTIC LLAMAS IMBUING", hue=Gump.hues["text"])
        self._draw_item_properties(imbueGump)
        self._draw_settings(imbueGump)
        self._draw_rows(imbueGump)
        self._draw_material_costs(imbueGump)

        speedGump = g.addTabButton("Swing Speed", "tracking", self.PAGE_WIDTH, withStatus=False)
        self._drawGump = speedGump
        speedGump.addTitle("SWING SPEED INCREASE", hue=Gump.hues["text"])
        self._draw_speed_calc(speedGump)

        pickerGump = g.createSubGump(self.PAGE_WIDTH, self.HEIGHT, "right", withStatus=False, alwaysVisible=False)
        pickerGump.gump.IsVisible = False
        g.tabGumps["Picker"] = pickerGump
        self._drawGump = pickerGump
        self._draw_picker(pickerGump)
        self._drawGump = None

        g.setActiveTab("Imbuing")
        self._set_status(state.get("Msg", ""))
        g.create()

    def _addPanel(self, x, y, width, height, title=None, group="main"):
        panel = self._ui_gump().addPanel(x, y, width, height, None, withTexture=True)
        self._remember(panel["elements"], group)
        if title:
            self._addSectionTitle("", title, x + 8, y + 10, width - 16, group)
        return panel

    def _addSectionPanel(self, number, title, x, y, width, height, group="main"):
        panel = self._addPanel(x, y, width, height, None, group)
        self._addSectionTitle(str(number), title, x + 8, y + 10, width - 16, group)
        return panel

    def _addSectionTitle(self, number, title, x, y, width, group="main"):
        ui = self._ui_gump()
        parts = [
            ui.addColorBox(x, y, 26, 26, Gump.theme["panelOuter"], 1, withTexture=False),
            ui.addColorBox(x + 2, y + 2, 22, 22, Gump.theme["sectionBadge"], 0.98, withTexture=False),
            ui.addColorBox(x + 5, y + 5, 16, 16, Gump.theme["frameInner"], 0.86, withTexture=False),
            ui.addColorBox(x + 8, y + 8, 10, 10, Gump.theme["bgOuter"], 0.98, withTexture=False),
            ui.addColorBox(x + 34, y + 20, 1, max(1, width - 34), Gump.theme["panelHeaderLine"], 0.55, withTexture=False),
        ]
        label = None
        if number:
            label = ui.addLabel(number, x + 9, y + 5, Gump.hues["text"])
            parts.append(label)
        title_label = ui.addLabel(title.upper(), x + 42, y + 6, Gump.hues["text"])
        parts.append(title_label)
        return self._remember(parts, group)

    def _addFlatRow(self, x, y, width, height, group="main"):
        ui = self._ui_gump()
        row = ui.addColorBox(x, y, height, width, Gump.theme["row"], 0.48, withTexture=False)
        top = ui.addColorBox(x, y, 1, width, "#2f4850", 0.22, withTexture=False)
        line = ui.addColorBox(x, y + height - 1, 1, width, "#000000", 0.52, withTexture=False)
        return self._remember([row, top, line], group)

    def _addButton(self, text, x, y, width, height=24, callback=None, fontSize=11, group=None):
        ui = self._ui_gump()
        cb = self._callback(callback) if callback else None
        top_height = max(1, int(height * 0.42))
        parts = [
            ui.addColorBox(x + 2, y + 3, height, width, Gump.theme["buttonShadow"], 0.62, withTexture=False),
            ui.addColorBox(x, y, height, width, Gump.theme["buttonFrame"], 1, withTexture=False),
            ui.addColorBox(x + 1, y + 1, height - 2, width - 2, Gump.theme["buttonInset"], 1, withTexture=False),
            ui.addColorBox(x + 3, y + 3, top_height, width - 6, Gump.theme["buttonHighlight"], 0.76, withTexture=True),
            ui.addColorBox(x + 3, y + 3 + top_height, max(1, height - 6 - top_height), width - 6, Gump.theme["buttonFill"], 0.94, withTexture=True),
            ui.addColorBox(x + 2, y + 2, 1, width - 4, "#ffffff", 0.12, withTexture=False),
            ui.addColorBox(x + 2, y + height - 2, 1, width - 4, "#000000", 0.58, withTexture=False),
        ]
        hover = ui.addColorBox(x + 2, y + 2, height - 4, width - 4, Gump.theme["frameHighlight"], 0.16, withTexture=False)
        hover.IsVisible = False
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(width)
        hitTarget.SetHeight(height)
        if cb:
            API.AddControlOnClick(hitTarget, cb)
        ui.gump.Add(hitTarget)
        label = ui.addTtfLabel(text, x, y, width, height, fontSize, Gump.theme["buttonText"], "center", cb)
        ui.hoverControls.append({"targets": [hitTarget, label], "hover": hover})
        control = {"parts": parts, "hover": hover, "hitTarget": hitTarget, "label": label}
        if group:
            self._remember(control, group)
        return control

    def _addGemDot(self, x, y, color, group="main", callback=None):
        ui = self._ui_gump()
        cb = self._callback(callback) if callback else None
        parts = [
            ui.addColorBox(x + 5, y, 4, 8, "#d7f2ff", 0.62, withTexture=False),
            ui.addColorBox(x + 2, y + 3, 10, 14, color, 0.98, withTexture=False),
            ui.addColorBox(x + 5, y + 6, 8, 8, "#f5fbff", 0.28, withTexture=False),
            ui.addColorBox(x + 7, y + 2, 3, 4, "#ffffff", 0.68, withTexture=False),
        ]
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(20)
        hitTarget.SetHeight(20)
        if cb:
            API.AddControlOnClick(hitTarget, cb)
        ui.gump.Add(hitTarget)
        control = {"parts": parts, "hitTarget": hitTarget}
        return self._remember(control, group) if group else control

    def _addMaxButton(self, x, y, callback, group="main"):
        return self._addGemDot(x, y + 1, "#69be37", group, callback)

    def _addSettingAction(self, text, x, y, callback, group="main"):
        ui = self._ui_gump()
        cb = self._callback(callback) if callback else None
        icon = self._addGemDot(x, y + 1, "#2384d7", group=None, callback=callback)
        label = ui.addLabel(text, x + 28, y + 3, Gump.hues["text"])
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(260)
        hitTarget.SetHeight(22)
        if cb:
            API.AddControlOnClick(hitTarget, cb)
        ui.gump.Add(hitTarget)
        control = {"icon": icon, "label": label, "hitTarget": hitTarget}
        return self._remember(control, group) if group else control

    def _addInput(self, defaultValue, x, y, minValue=0, maxValue=120, width=60, height=24, group="main"):
        return self._remember(
            self._ui_gump().addSkillTextBox(defaultValue, x, y, minValue, maxValue, width, height),
            group,
        )

    def _addRadio(self, label, x, y, isChecked, callback, hue=None, group="main"):
        ui = self._ui_gump()
        if hue is None:
            hue = Gump.hues["text"]
        radio = API.CreateGumpRadioButton("", 6200, 9020, 9021, hue, isChecked)
        radio.SetX(x)
        radio.SetY(y)
        radio.IsVisible = False
        ui.gump.Add(radio)
        box = ui.addColorBox(x, y + 2, 18, 18, Gump.theme["buttonFrame"], 1, withTexture=False)
        inner = ui.addColorBox(x + 3, y + 5, 12, 12, Gump.theme["inputFill"], 0.98, withTexture=False)
        fill = ui.addColorBox(x + 5, y + 7, 8, 8, "#69be37", 0.98, withTexture=False)
        fill.IsVisible = isChecked
        text = ui.addLabel(label, x + 28, y + 3, hue)
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(110)
        hitTarget.SetHeight(22)
        if callback:
            API.AddControlOnClick(hitTarget, self._callback(callback))
        ui.gump.Add(hitTarget)
        self._remember({"radio": radio, "box": box, "inner": inner, "fill": fill, "label": text, "hitTarget": hitTarget}, group)
        return GumpModule.GumpRadio(radio, [fill])

    def _addReadOnlyRadio(self, label, x, y, isChecked, hue=None, group="main"):
        ui = self._ui_gump()
        if hue is None:
            hue = Gump.hues["muted"]
        radio_group = {"Custom": 5101, "Exceptional": 5102, "Whetstone": 5103}.get(label, 5100)
        radio = API.CreateGumpRadioButton("", radio_group, 9020, 9021, hue, isChecked)
        radio.SetX(x)
        radio.SetY(y)
        radio.IsVisible = False
        ui.gump.Add(radio)
        box = ui.addColorBox(x, y + 2, 18, 18, Gump.theme["buttonFrame"], 1, withTexture=False)
        inner = ui.addColorBox(x + 3, y + 5, 12, 12, Gump.theme["inputFill"], 0.98, withTexture=False)
        fill = ui.addColorBox(x + 5, y + 7, 8, 8, "#69be37", 0.98, withTexture=False)
        fill.IsVisible = isChecked
        text = ui.addLabel(label, x + 30, y + 3, hue)
        self._remember({"radio": radio, "box": box, "inner": inner, "fill": fill, "label": text}, group)
        return GumpModule.GumpRadio(radio, [fill])

    def _draw_item_properties(self, g):
        panel = self._addSectionPanel(1, "Select Item", 8, 44, 568, 150)
        x = panel["x"] + 10
        y = panel["y"] + 34
        row_w = panel["width"] - 20
        for row_y in (y - 4, y + 34, y + 61, y + 88):
            self._addFlatRow(x - 6, row_y, row_w, 25, "main")
        self._addSettingAction("Select item", x + 4, y, AutoReadItem, group="main")
        self.controls["targetLabel"] = self._addLabel("", x + 206, y + 3, Gump.hues["muted"])

        type_y = y + 38
        value_x = x + 116
        check_x = x + 358
        self._addLabel("Category", x, type_y, Gump.hues["muted"])
        self.controls["categoryLabel"] = self._addLabel("", value_x, type_y, Gump.hues["text"])
        self._addLabel("Group", x, type_y + 27, Gump.hues["muted"])
        self.controls["groupLabel"] = self._addLabel("", value_x, type_y + 27, Gump.hues["text"])
        self._addLabel("Base Item", x, type_y + 54, Gump.hues["muted"])
        self.controls["itemLabel"] = self._addLabel("", value_x, type_y + 54, Gump.hues["text"])
        self.controls["customCheck"] = self._addReadOnlyRadio("Custom", check_x, type_y, state.get("CustomMode", False), Gump.hues["muted"])
        self.controls["exceptionalCheck"] = self._addReadOnlyRadio("Exceptional", check_x, type_y + 27, state.get("Exceptional", False), Gump.hues["muted"])
        self.controls["whetstoneCheck"] = self._addReadOnlyRadio("Whetstone", check_x, type_y + 54, state.get("Whetstone", False), Gump.hues["muted"])

    def _draw_settings(self, g):
        panel = self._addSectionPanel(2, "Settings", 8, 204, 568, 132)
        x = panel["x"] + 10
        y = panel["y"] + 34
        row_w = panel["width"] - 20
        for row_y in (y - 4, y + 35, y + 70):
            self._addFlatRow(x - 6, row_y, row_w, 28, "main")
        self._addLabel("Reserve", x, y + 3, Gump.hues["muted"])
        self.bufferInput = self._addInput(str(state.get("GemBuffer", "0") or "0"), x + 88, y - 1, 0, 999, width=72, height=26)
        self.controls["matButton"] = self._addSettingAction("Select material container", x + 4, y + 38, lambda: self._target_container("MatCont", "Select Material Container"), group="main")
        self.controls["gemButton"] = self._addSettingAction("Select gem container", x + 4, y + 73, lambda: self._target_container("GemCont", "Select Gem Container"), group="main")

    def _draw_rows(self, g):
        panel = self._addSectionPanel(3, "Properties", 8, 346, 568, 196)
        x = panel["x"] + 10
        y = panel["y"] + 32
        row_w = panel["width"] - 20
        self._addLabel("Property", x + 110, y, Gump.hues["muted"])
        self._addLabel("Val", x + 292, y, Gump.hues["muted"])
        self._addLabel("Weight", x + 410, y, Gump.hues["muted"])
        self._addButton("Calc", x + row_w - 56, y - 2, 48, height=20, callback=self._recalculate_materials, fontSize=9, group="main")
        for i, row in enumerate(state["Rows"]):
            row_y = y + 25 + i * 23
            row_control = {
                "row": self._addFlatRow(x - 6, row_y - 2, row_w, 22, "main"),
                "select": self._addButton("", x + 8, row_y, 246, height=20, callback=lambda idx=i: self._open_property_picker(idx), fontSize=10, group=None),
                "locked": self._addLabel("", x + 12, row_y + 3, Gump.hues["muted"], group=None),
                "input": self._addInput(str(row["Val"]), x + 286, row_y, 0, 999, width=56, height=20, group=None),
                "max": self._addMaxButton(x + 368, row_y, lambda idx=i: self._max_row(idx), group=None),
                "weight": self._addLabel("", x + 452, row_y + 3, Gump.hues["text"], group=None),
            }
            self.rowControls.append(row_control)
        preset_y = y + 147
        self._addLabel("Preset", x, preset_y + 3, Gump.hues["muted"])
        selected_preset = state.get("SelectedPreset", PRESET_CUSTOM)
        self.controls["presetCustom"] = self._addRadio(
            PRESET_CUSTOM,
            x + 66,
            preset_y,
            selected_preset == PRESET_CUSTOM,
            lambda: self._apply_preset(PRESET_CUSTOM),
            group="main",
        )
        self.controls["presetBasicLrc"] = self._addRadio(
            "Basic LRC",
            x + 170,
            preset_y,
            selected_preset == "Basic LRC",
            lambda: self._apply_preset("Basic LRC"),
            group="main",
        )
        self._addLabel("Total Weight", x + 336, preset_y + 3, Gump.hues["muted"])
        self.controls["totalWeightLabel"] = self._addLabel("", x + 450, preset_y + 3, Gump.hues["text"])

    def _draw_material_costs(self, g):
        panel = self._addSectionPanel(4, "Materials Cost", 8, 552, 568, 158)
        x = panel["x"] + 10
        y = panel["y"] + 31
        scroll_y = y + 22
        scroll_width = panel["width"] - 20
        scroll_height = 82
        self.materialTableWidth = scroll_width - 18
        self.materialQtyX = self.materialTableWidth - 86
        self._addLabel("Material", x + 20, y, Gump.hues["muted"])
        self._addLabel("Qty", x + self.materialQtyX, y, Gump.hues["muted"])
        self.controls["noMaterialsLabel"] = self._addLabel("", x, y + 28, Gump.hues["muted"], group=None)
        self.materialScrollArea = API.CreateGumpScrollArea(x - 4, scroll_y, scroll_width, scroll_height)
        self._ui_gump().gump.Add(self.materialScrollArea)
        self._remember(self.materialScrollArea, "main")
        self.controls["moreMaterialsLabel"] = self._addSettingAction("", x, scroll_y + scroll_height + 5, lambda: None, group="main")
        self.controls["startImbuingButton"] = self._addButton("Start Imbuing", x - 4, panel["y"] + panel["height"] - 28, scroll_width, height=24, callback=AutoImbue, fontSize=11, group="main")

    def _update_materials(self):
        main_visible = True
        self._set_input_text(self.bufferInput, state.get("GemBuffer", "0") or "0")
        self._set_button_text(self.controls["matButton"], self._container_text("Mats", state.get("MatCont", 0)))
        self._set_button_text(self.controls["gemButton"], self._container_text("Gems", state.get("GemCont", 0)))
        items = sorted(CompileIngredients().items())
        self._set_visible(self.controls["noMaterialsLabel"], main_visible and not items)
        self._set_text(self.controls["noMaterialsLabel"], "No materials required.")
        if self.materialScrollArea:
            self.materialScrollArea.Clear()
            for index, (name, amount) in enumerate(items):
                row_y = index * 16
                row_bg = API.CreateGumpColorBox(0.42, Gump.theme["row"])
                row_bg.SetX(0)
                row_bg.SetY(row_y)
                row_bg.SetWidth(self.materialTableWidth)
                row_bg.SetHeight(15)
                self.materialScrollArea.Add(row_bg)
                line = API.CreateGumpColorBox(0.32, "#000000")
                line.SetX(0)
                line.SetY(row_y + 15)
                line.SetWidth(self.materialTableWidth)
                line.SetHeight(1)
                self.materialScrollArea.Add(line)
                graphic_data = INGREDIENT_GRAPHICS.get(name)
                if graphic_data:
                    try:
                        icon = API.CreateGumpItemPic(graphic_data[0], 16, 16)
                        icon.SetX(2)
                        icon.SetY(row_y - 1)
                        self.materialScrollArea.Add(icon)
                    except Exception:
                        pass
                name_label = API.CreateGumpLabel(name, Gump.hues["text"])
                name_label.SetX(26)
                name_label.SetY(row_y)
                self.materialScrollArea.Add(name_label)
                amount_label = API.CreateGumpLabel(str(amount), Gump.hues["text"])
                amount_label.SetX(self.materialQtyX)
                amount_label.SetY(row_y)
                self.materialScrollArea.Add(amount_label)
        overflow = len(items) > self.MATERIAL_ROWS_VISIBLE
        count_text = "{} material{}".format(len(items), "" if len(items) == 1 else "s")
        self._set_button_text(self.controls["moreMaterialsLabel"], count_text)
        self._set_visible(self.controls["moreMaterialsLabel"], main_visible)

    def _draw_speed_calc(self, g):
        panel = self._addSectionPanel(1, "Swing Speed", 8, 44, 568, 178, group="speed")
        x = panel["x"] + 10
        y = panel["y"] + 34
        row_w = panel["width"] - 20
        for row_y in (y - 4, y + 34, y + 68, y + 102):
            self._addFlatRow(x - 6, row_y, row_w, 27, "speed")
        self.controls["weaponButton"] = self._addButton("", x + 6, y, 250, height=23, callback=lambda: self._open_picker("SpeedCategories"), group="speed")
        self._addLabel("Stam", x + 280, y + 3, Gump.hues["muted"], group="speed")
        self.staminaInput = self._addInput(str(state.get("StaminaInput", "") or "0"), x + 334, y - 1, 0, 999, width=60, height=24, group="speed")
        self._addLabel("SSI", x, y + 38, Gump.hues["muted"], group="speed")
        self.ssiInput = self._addInput(str(state.get("SSIInput", "") or "0"), x + 54, y + 34, 0, 999, width=60, height=24, group="speed")
        self._addButton("Calc", x + 134, y + 34, 58, height=24, callback=CalculateSwingSpeed, group="speed")
        self._addLabel("Ticks", x, y + 72, Gump.hues["muted"], group="speed")
        self.controls["ticksLabel"] = self._addLabel("", x + 84, y + 72, Gump.hues["text"], group="speed")
        self._addLabel("Speed", x + 220, y + 72, Gump.hues["muted"], group="speed")
        self.controls["speedLabel"] = self._addLabel("", x + 304, y + 72, Gump.hues["text"], group="speed")
        self._addButton("Auto Imbue", x, y + 104, 110, height=24, callback=AutoImbue, group="speed")

    def _draw_picker(self, g):
        self.pickerSlots = []
        panel = self._addSectionPanel("", "Select", 8, 44, 568, 600, group="picker")
        x = panel["x"] + 8
        y = panel["y"] + 34
        self.controls["pickerTitle"] = self._addLabel("", x + 8, panel["y"] + 6, Gump.hues["text"], group="picker")
        for visible_index in range(ITEMS_PER_PAGE):
            row_y = y + visible_index * 24
            slot = {
                "button": self._addButton("", x + 2, row_y - 2, panel["width"] - 20, height=22, callback=lambda idx=visible_index: self._select_picker_visible(idx), fontSize=10, group="picker"),
                "label": self._addLabel("", x + 8, row_y + 3, Gump.hues["muted"], group="picker"),
            }
            self.pickerSlots.append(slot)
        nav_y = panel["y"] + panel["height"] - 60
        self.controls["prevButton"] = self._addButton("<", x, nav_y, 36, callback=lambda: self._change_page(-1), group="picker")
        self.controls["pageLabel"] = self._addLabel("", x + 58, nav_y + 4, Gump.hues["muted"], group="picker")
        self.controls["nextButton"] = self._addButton(">", x + 160, nav_y, 36, callback=lambda: self._change_page(1), group="picker")
        self.controls["backButton"] = self._addButton("Back", x, nav_y + 32, 82, callback=lambda: self._open_picker(self._back_target()), group="picker")
        self.controls["closePickerButton"] = self._addButton("Close", x + 132, nav_y + 32, 82, callback=self._close_picker, group="picker")

    def _showGump(self):
        g = Gump(self.WIDTH, self.HEIGHT, self._onClose, False, gumpId=self.GUMP_ID)
        self.gump = g
        try:
            g.gump.SetX(max(12, g.gump.GetX() - self.PAGE_WIDTH // 2))
        except Exception:
            pass

        imbueGump = g.addTabButton("Imbuing", "caster", self.PAGE_WIDTH, withStatus=False)
        self._drawGump = imbueGump
        imbueGump.addTitle("MYSTIC LLAMAS IMBUING", hue=Gump.hues["text"])
        self._draw_item_properties(imbueGump)
        self._draw_settings(imbueGump)
        self._draw_rows(imbueGump)
        self._draw_material_costs(imbueGump)

        speedGump = g.addTabButton("Swing Speed", "bard", self.PAGE_WIDTH, withStatus=False)
        self._drawGump = speedGump
        speedGump.addTitle("SWING SPEED INCREASE", hue=Gump.hues["text"])
        self._draw_speed_calc(speedGump)

        pickerGump = g.createSubGump(self.PAGE_WIDTH, self.HEIGHT, "right", withStatus=False, alwaysVisible=False)
        pickerGump.gump.IsVisible = False
        g.tabGumps["Picker"] = pickerGump
        self._drawGump = pickerGump
        self._draw_picker(pickerGump)
        self._drawGump = None

        g.setActiveTab("Imbuing")
        self._set_status(state.get("Msg", ""))
        g.create()

    def _addNativeCircleButton(self, button_type, x, y, callback=None, group="main"):
        cb = self._callback(callback) if callback else None
        button = self._ui_gump().addButton("", x, y, button_type, cb)
        return self._remember(button, group) if group else button

    def _addMaxButton(self, x, y, callback, group="main"):
        return self._addNativeCircleButton("radioGreen", x, y, callback, group)

    def _addSettingAction(self, text, x, y, callback, group="main"):
        ui = self._ui_gump()
        cb = self._callback(callback) if callback else None
        button = self._addNativeCircleButton("radioBlue", x, y, callback, group=None)
        label = ui.addLabel(text, x + 28, y + 2, Gump.hues["text"])
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(286)
        hitTarget.SetHeight(22)
        if cb:
            API.AddControlOnClick(hitTarget, cb)
        ui.gump.Add(hitTarget)
        control = {"button": button, "label": label, "hitTarget": hitTarget}
        return self._remember(control, group) if group else control

    def _draw_rows(self, g):
        panel = self._addSectionPanel(3, "Properties", 8, 338, 568, 202)
        x = panel["x"] + 10
        y = panel["y"] + 32
        row_w = panel["width"] - 20
        self._addLabel("Property", x + 112, y, Gump.hues["muted"])
        self._addLabel("Val", x + 292, y, Gump.hues["muted"])
        self._addLabel("Weight", x + 408, y, Gump.hues["muted"])
        self._addButton("Calc", x + row_w - 56, y - 2, 48, height=20, callback=self._recalculate_materials, fontSize=9, group="main")
        for i, row in enumerate(state["Rows"]):
            row_y = y + 23 + i * 21
            row_control = {
                "row": self._addFlatRow(x - 6, row_y - 2, row_w, 20, "main"),
                "select": self._addButton("", x + 8, row_y - 1, 246, height=19, callback=lambda idx=i: self._open_property_picker(idx), fontSize=10, group=None),
                "locked": self._addLabel("", x + 12, row_y + 2, Gump.hues["muted"], group=None),
                "input": self._addInput(str(row["Val"]), x + 286, row_y - 1, 0, 999, width=56, height=20, group=None),
                "max": self._addMaxButton(x + 370, row_y - 1, lambda idx=i: self._max_row(idx), group=None),
                "weight": self._addLabel("", x + 452, row_y + 2, Gump.hues["text"], group=None),
            }
            self.rowControls.append(row_control)
        preset_y = y + 136
        self._addLabel("Preset", x, preset_y + 3, Gump.hues["muted"])
        selected_preset = state.get("SelectedPreset", PRESET_CUSTOM)
        self.controls["presetCustom"] = self._addRadio(
            PRESET_CUSTOM,
            x + 66,
            preset_y,
            selected_preset == PRESET_CUSTOM,
            lambda: self._apply_preset(PRESET_CUSTOM),
            group="main",
        )
        self.controls["presetBasicLrc"] = self._addRadio(
            "Basic LRC",
            x + 170,
            preset_y,
            selected_preset == "Basic LRC",
            lambda: self._apply_preset("Basic LRC"),
            group="main",
        )
        self._addLabel("Total Weight", x + 334, preset_y + 3, Gump.hues["muted"])
        self.controls["totalWeightLabel"] = self._addLabel("", x + 448, preset_y + 3, Gump.hues["text"])

    def _draw_material_costs(self, g):
        panel = self._addSectionPanel(4, "Materials Cost", 8, 550, 568, 194)
        x = panel["x"] + 10
        y = panel["y"] + 31
        scroll_y = y + 22
        scroll_width = panel["width"] - 20
        scroll_height = 82
        self.materialTableWidth = scroll_width - 18
        self.materialQtyX = self.materialTableWidth - 86
        self._addLabel("Material", x + 20, y, Gump.hues["muted"])
        self._addLabel("Qty", x + self.materialQtyX, y, Gump.hues["muted"])
        self.controls["noMaterialsLabel"] = self._addLabel("", x, y + 28, Gump.hues["muted"], group=None)
        self.materialScrollArea = API.CreateGumpScrollArea(x - 4, scroll_y, scroll_width, scroll_height)
        self._ui_gump().gump.Add(self.materialScrollArea)
        self._remember(self.materialScrollArea, "main")
        footer_y = scroll_y + scroll_height + 4
        self.controls["moreMaterialsIcon"] = self._addNativeCircleButton("radioBlue", x + 4, footer_y - 2, None, group="main")
        self.controls["moreMaterialsLabel"] = self._addLabel("", x + 32, footer_y, Gump.hues["muted"], group="main")
        self.controls["startImbuingButton"] = self._addButton(
            "Start Imbuing",
            x - 4,
            716,
            scroll_width,
            height=24,
            callback=AutoImbue,
            fontSize=11,
            group="main",
        )

    def _update_materials(self):
        main_visible = True
        self._set_input_text(self.bufferInput, state.get("GemBuffer", "0") or "0")
        self._set_button_text(self.controls["matButton"], self._container_text("Mats", state.get("MatCont", 0)))
        self._set_button_text(self.controls["gemButton"], self._container_text("Gems", state.get("GemCont", 0)))
        items = sorted(CompileIngredients().items())
        self._set_visible(self.controls["noMaterialsLabel"], main_visible and not items)
        self._set_text(self.controls["noMaterialsLabel"], "No materials required.")
        if self.materialScrollArea:
            self.materialScrollArea.Clear()
            for index, (name, amount) in enumerate(items):
                row_y = index * 16
                row_bg = API.CreateGumpColorBox(0.42, Gump.theme["row"])
                row_bg.SetX(0)
                row_bg.SetY(row_y)
                row_bg.SetWidth(self.materialTableWidth)
                row_bg.SetHeight(15)
                self.materialScrollArea.Add(row_bg)
                line = API.CreateGumpColorBox(0.32, "#000000")
                line.SetX(0)
                line.SetY(row_y + 15)
                line.SetWidth(self.materialTableWidth)
                line.SetHeight(1)
                self.materialScrollArea.Add(line)
                graphic_data = INGREDIENT_GRAPHICS.get(name)
                if graphic_data:
                    try:
                        icon = API.CreateGumpItemPic(graphic_data[0], 16, 16)
                        icon.SetX(2)
                        icon.SetY(row_y - 1)
                        self.materialScrollArea.Add(icon)
                    except Exception:
                        pass
                name_label = API.CreateGumpLabel(name, Gump.hues["text"])
                name_label.SetX(26)
                name_label.SetY(row_y)
                self.materialScrollArea.Add(name_label)
                amount_label = API.CreateGumpLabel(str(amount), Gump.hues["text"])
                amount_label.SetX(self.materialQtyX)
                amount_label.SetY(row_y)
                self.materialScrollArea.Add(amount_label)
        count_text = "{} material{}".format(len(items), "" if len(items) == 1 else "s")
        self._set_text(self.controls["moreMaterialsLabel"], count_text)
        self._set_visible(self.controls["moreMaterialsIcon"], main_visible and bool(items))
        self._set_visible(self.controls["moreMaterialsLabel"], main_visible and bool(items))


_APP = None


def send_calculator():
    if _APP:
        _APP.redraw()


def main():
    global _APP
    API.SysMsg("Starting Imbuing & SSI Calculator", 65)
    DebugLog("Debug logging enabled. File={}".format(_debug_log_path()), 65)
    _APP = MysticLlamasCalculator()
    while not API.StopRequested and _APP.tick():
        API.Pause(0.1)


main()
