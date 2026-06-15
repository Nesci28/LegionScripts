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

try:
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except Exception:
    _SCRIPT_DIR = os.getcwd()
for _IMPORT_ROOT in (_SCRIPT_DIR, os.path.join(os.getcwd(), "Other")):
    if (
        os.path.isdir(os.path.join(_IMPORT_ROOT, "_Presets"))
        or os.path.isdir(os.path.join(_IMPORT_ROOT, "_Utils"))
    ) and _IMPORT_ROOT not in sys.path:
        sys.path.insert(0, _IMPORT_ROOT)

LegionPath.addSubdirs()

import Util as UtilModule
import Gump as GumpModule
import Craft as CraftModule

importlib.reload(UtilModule)
importlib.reload(GumpModule)
importlib.reload(CraftModule)

from Util import Util
from Gump import Gump
from Craft import Craft
from _Utils.GumpControlMixin import GumpControlMixin
from _Utils.LegionApiCompat import (
    Gumps,
    Items,
    Journal,
    Misc,
    Player,
    Target,
    configure_legion_api_compat,
    _item_amount,
    _serial,
)

configure_legion_api_compat(API, Util)


DEBUG_IMBUING = True
DEBUG_SUIT_DECISIONS = True
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
    _write_debug_log(text)


def _write_debug_log(text):
    try:
        with open(_debug_log_path(), "a") as log_file:
            log_file.write("{} {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), text))
    except Exception:
        pass


def SuitLog(message):
    if not DEBUG_SUIT_DECISIONS:
        return
    text = "[ML Imbue] [Suit] {}".format(message)
    _write_debug_log(text)


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

SUIT_PRESET_BASIC = "Basic LRC Training"
SUIT_PRESET_MAGE = "Mage 70 Resists"
SUIT_PRESET_LUCK = "Luck"
SUIT_PRESET_SAMPIRE = "Sampire"
SUIT_BODIES = ("Male", "Female", "Gargoyle")
SUIT_RESISTS = (
    "Physical Resist",
    "Fire Resist",
    "Cold Resist",
    "Poison Resist",
    "Energy Resist",
)
SUIT_RESIST_DISPLAY = (
    ("Physical Resist", "P", "#d8c6a0", "Phys"),
    ("Fire Resist", "F", "#d35c4c", "Fire"),
    ("Cold Resist", "C", "#63b9d7", "Cold"),
    ("Poison Resist", "Po", "#74c95c", "Pois"),
    ("Energy Resist", "E", "#b07ad8", "Ener"),
)
SUIT_RESIST_TARGET = 70
SUIT_MAX_ROWS = 5
SUIT_MAX_RESIST_ROWS = 2
SUIT_HIGH_RESIST_COUNT = 2
SUIT_HIGH_RESIST_GAP = 3
SUIT_HIGH_BALANCE_MIN = 2
SUIT_HIGH_BALANCE_MAX = 3
SUIT_NORMAL_LEATHER_HUE = 0
SUIT_NORMAL_LEATHER_MATERIAL = {
    "name": "normal leather",
    "hue": SUIT_NORMAL_LEATHER_HUE,
    "buttonId": 5000,
}
TAILORING_CRAFTING_INFO = {
    "tool": {"graphic": 0x0F9D, "buttonId": 14},
    "materialHues": {
        "normal leather": SUIT_NORMAL_LEATHER_MATERIAL,
    },
}


def _leather_item(name, graphic, button_id, amount):
    return {
        "name": name,
        "graphic": graphic,
        "buttonId": button_id,
        "disposeMethod": "Salvage Bag",
        "resources": [
            {
                "graphic": 0x1081,
                "amount": amount,
                "hasSpecialHue": True,
                "backpackTargetAmount": amount,
            },
        ],
    }


SUIT_ITEM_DEFS = {
    "Leather Cap": _leather_item("leather cap", 0x1DB9, 609, 2),
    "Leather Gorget": _leather_item("leather gorget", 0x13C7, 608, 4),
    "Leather Sleeves": _leather_item("leather sleeves", 0x13C5, 611, 4),
    "Leather Gloves": _leather_item("leather gloves", 0x13C6, 610, 3),
    "Leather Tunic": _leather_item("leather tunic", 0x13CC, 613, 12),
    "Leather Leggings": _leather_item("leather leggings", 0x13CB, 612, 10),
    "Female Leather Armor": _leather_item("female leather armor", 0x1C06, 637, 8),
    "Leather Skirt": _leather_item("leather skirt", 0x1C08, 634, 6),
    "Gargish Leather Wing Armor": _leather_item("gargish leather wing armor", None, 680, 6),
    "Gargish Leather Arms": _leather_item("gargish leather arms", None, 681, 8),
    "Gargish Leather Chest": _leather_item("gargish leather chest", None, 682, 8),
    "Gargish Leather Leggings": _leather_item("gargish leather leggings", None, 683, 10),
    "Gargish Leather Kilt": _leather_item("gargish leather kilt", None, 684, 6),
    "Gargish Leather Talons": _leather_item("gargish leather talons", None, 685, 6),
}

SUIT_BODY_ITEMS = {
    "Male": (
        "Leather Cap",
        "Leather Gorget",
        "Leather Sleeves",
        "Leather Gloves",
        "Leather Tunic",
        "Leather Leggings",
    ),
    "Female": (
        "Leather Cap",
        "Leather Gorget",
        "Leather Sleeves",
        "Leather Gloves",
        "Female Leather Armor",
        "Leather Skirt",
    ),
    "Gargoyle": (
        "Gargish Leather Wing Armor",
        "Gargish Leather Arms",
        "Gargish Leather Chest",
        "Gargish Leather Leggings",
        "Gargish Leather Kilt",
        "Gargish Leather Talons",
    ),
}

SUIT_GEAR_FALLBACK_GRAPHICS = (
    0x1DB9,
    0x13C7,
    0x13C5,
    0x13C6,
    0x13CC,
    0x13CB,
)
SUIT_SELECTED_ITEM_HUE = 69

SUIT_BASIC_ROWS = [
    {"Prop": "Lower Mana Cost", "Val": 7},
    {"Prop": "Lower Reagent Cost", "Val": 17},
    {"Prop": "Mana Regeneration", "Val": 1},
    {"Prop": "Mana Increase", "Val": 7},
]
SUIT_MAGE_REQUIRED_ROWS = [
    {"Prop": "Lower Reagent Cost", "Val": 17},
    {"Prop": "Lower Mana Cost", "Val": 7},
]
SUIT_MAGE_STAT_CAPS = {
    "Lower Reagent Cost": 100,
    "Lower Mana Cost": 40,
}


from _Presets import (
    BasicLrcSuitPreset,
    Mage70ResistsSuitPreset,
    LuckSuitPreset,
    SampireSuitPreset,
)


SUIT_PRESETS = (
    BasicLrcSuitPreset(globals()),
    Mage70ResistsSuitPreset(globals()),
    LuckSuitPreset(globals()),
    SampireSuitPreset(globals()),
)
SUIT_PRESETS_BY_KEY = dict((preset.key, preset) for preset in SUIT_PRESETS)


def _suit_preset_for_key(preset_key):
    return SUIT_PRESETS_BY_KEY.get(preset_key, SUIT_PRESETS_BY_KEY[SUIT_PRESET_BASIC])


def _suit_current_preset():
    preset = _suit_preset_for_key(state.get("SuitPreset", SUIT_PRESET_BASIC))
    if state.get("SuitPreset") != preset.key:
        state["SuitPreset"] = preset.key
    return preset


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
    "SuitBody": "Male",
    "SuitPreset": SUIT_PRESET_BASIC,
    "SuitKeepCont": 0,
    "SuitRows": [],
    "SuitRunning": False,
    "SuitStop": False,
    "SuitMsg": "",
    "SuitMarkedSerial": 0,
    "SuitSelectedItemHues": {},
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


def _suit_row_is_additive_resist(row):
    return row.get("Mode") == "Add" and row.get("Prop") in SUIT_RESISTS


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
        
        if prop in state.get("ScannedProps", {}) and not _suit_row_is_additive_resist(row):
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
            return False

    state["Msg"] = "Starting Imbue Sequence..."
    send_calculator()
    DebugLog("AutoImbue starting. Target={}".format(_debug_hex(state["ImbueTarget"])), 65)

    if not RefreshItemProps(state["ImbueTarget"]):
        DebugLog("RefreshItemProps failed for target {}.".format(_debug_hex(state["ImbueTarget"])), 33)
        Misc.SendMessage("Failed to read item properties. Is it too far away?", 33)
        return False

    if not PullItems():
        DebugLog("AutoImbue stopped during pre-pull.", 33)
        send_calculator()
        return False
    
    props_to_imbue = []
    for row in state["Rows"]:
        prop = row["Prop"]
        val = row["Val"]
        if prop == "None" or val == 0: continue
        
        if prop in state.get("ScannedProps", {}) and not _suit_row_is_additive_resist(row):
            if val <= state["ScannedProps"][prop]:
                Misc.SendMessage("Skipping {} - Already at {}%!".format(prop, state["ScannedProps"][prop]), 69)
                continue
        props_to_imbue.append(row)
        
    if not props_to_imbue:
        Misc.SendMessage("Item already meets or exceeds all targeted properties!", 69)
        state["Msg"] = "Nothing to imbue."
        DebugLog("AutoImbue: no properties need imbuing after scan.", 55)
        return True

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
                        for step_index in range(steps):
                            DebugLog(
                                "Fallback intensity click {} {}/{} for {}.".format(
                                    "up" if direction == 312 else "down",
                                    step_index + 1,
                                    steps,
                                    target_prop,
                                ),
                                55,
                            )
                            Gumps.SendAction(0xf3e90, direction)
                            Misc.Pause(350)
                        DebugLog("Fallback intensity complete for {}.".format(target_prop), 55)
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
            imbue_attempts = 0
            
            while imbuing:
                imbue_attempts += 1
                if imbue_attempts > 20:
                    DebugLog("Too many imbue attempts for {}; aborting property.".format(target_prop), 33)
                    Misc.SendMessage("Too many imbue attempts for {}.".format(target_prop), 33)
                    abort_sequence = True
                    imbuing = False
                    break
                Journal.Clear()
                
                DebugLog("Imbue attempt {} for {} retry={}.".format(imbue_attempts, target_prop, is_retry), 55)
                if is_retry:
                    Gumps.SendAction(0xf3e93, 4) # Click "Reimbue Last"
                    DebugLog("Waiting for reimbue result gump for {}.".format(target_prop), 55)
                    waited = Gumps.WaitForGump(0xf3e93, 3000)
                else:
                    Gumps.SendAction(0xf3e90, 302) # Click "Imbue Item"
                    DebugLog("Waiting for imbue result gump for {}.".format(target_prop), 55)
                    waited = Gumps.WaitForGump(0xf3e93, 5000)
                DebugLog("Imbue result gump wait for {} returned {}.".format(target_prop, waited), 55)
                
            outcome = None
            for _ in range(16):
                if Journal.Search("successfully imbue"):
                    outcome = "success"
                    break
                if Journal.Search("attempt to imbue the item, but fail"):
                    outcome = "fail"
                    break
                if Journal.Search("do not have enough resources"):
                    outcome = "resources"
                    break
                Misc.Pause(250)

            if outcome == "success":
                Misc.SendMessage("Successfully imbued {}!".format(target_prop), 69)
                DebugLog("Journal reported success for {}.".format(target_prop), 69)
                if _suit_row_is_additive_resist(row):
                    state["ScannedProps"][target_prop] = state["ScannedProps"].get(target_prop, 0) + target_val
                else:
                    state["ScannedProps"][target_prop] = target_val

                imbuing = False
                property_completed = True

            elif outcome == "fail":
                Misc.SendMessage("Failed imbue. Retrying...", 33)
                DebugLog("Journal reported imbue failure for {}; retrying.".format(target_prop), 33)
                is_retry = True

            elif outcome == "resources":
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
                DebugLog("No journal outcome after imbue click for {} retry={}.".format(target_prop, is_retry), 33)
                Misc.SendMessage("Imbuing halted. Check journal/materials.", 33)
                imbuing = False
                abort_sequence = True

    return not abort_sequence

# ---------------------------------------------------------
# --------------------------------------------------------
# SUIT CRAFTING ENGINE
# --------------------------------------------------------

def _suit_copy_rows(rows):
    copied = []
    for row in rows:
        prop = row.get("Prop", "None")
        val = int(row.get("Val", 0) or 0)
        if prop != "None" and val != 0:
            copied_row = {"Prop": prop, "Val": val}
            if row.get("Mode"):
                copied_row["Mode"] = row.get("Mode")
            copied.append(copied_row)
    while len(copied) < SUIT_MAX_ROWS:
        copied.append({"Prop": "None", "Val": 0})
    return copied[:SUIT_MAX_ROWS]


def _suit_row_weight(row):
    prop = row.get("Prop", "None")
    val = int(row.get("Val", 0) or 0)
    if prop == "None" or val == 0:
        return 0
    if prop not in DB_ARMOR or prop not in BASE_PROPS:
        return 0
    dyn_max = DB_ARMOR[prop].get("Max", 0)
    if dyn_max <= 0:
        return 0
    base_weight = DB_ARMOR[prop].get("Weight", BASE_PROPS[prop]["Weight"])
    return int(math.floor((float(val) / float(dyn_max)) * base_weight))


def _suit_rows_weight(rows):
    return sum(_suit_row_weight(row) for row in rows)


def _suit_parse_resists(props):
    resists = dict((name, 0) for name in SUIT_RESISTS)
    for prop_line in props:
        lower = prop_line.lower()
        for resist_name in SUIT_RESISTS:
            if resist_name.lower() not in lower:
                continue
            nums = re.findall(r"-?\d+", prop_line)
            if nums:
                resists[resist_name] = int(nums[-1])
    return resists


def _suit_parse_prop_values(props):
    values = {}
    search_map = {}
    for prop_name in BASE_PROPS.keys():
        if prop_name != "None":
            search_map[prop_name.lower()] = prop_name
    search_map["defence chance increase"] = "Defense Chance Increase"
    search_map["lower requirement"] = "Lower Requirements"
    sorted_keys = sorted(search_map.keys(), key=len, reverse=True)
    skip_list = [
        "physical damage",
        "fire damage",
        "cold damage",
        "poison damage",
        "energy damage",
        "weapon damage",
        "weapon speed",
        "durability",
    ]
    for prop_line in props:
        lower = prop_line.lower()
        if any(skip in lower for skip in skip_list):
            continue
        for search_key in sorted_keys:
            if search_key not in lower:
                continue
            nums = re.findall(r"[-]?\d+", prop_line)
            if nums:
                values[search_map[search_key]] = int(nums[0])
            break
    return values


def _suit_high_resists(resists):
    ranked = sorted(SUIT_RESISTS, key=lambda name: resists.get(name, 0), reverse=True)
    if len(ranked) < SUIT_HIGH_RESIST_COUNT + 1:
        return ()
    second_high = resists.get(ranked[SUIT_HIGH_RESIST_COUNT - 1], 0)
    first_low = resists.get(ranked[SUIT_HIGH_RESIST_COUNT], 0)
    if second_high - first_low < SUIT_HIGH_RESIST_GAP:
        return ()
    return tuple(ranked[:SUIT_HIGH_RESIST_COUNT])


def _suit_high_text(high_resists):
    if not high_resists:
        return "Flat resists"
    return "High " + "/".join(name.replace(" Resist", "") for name in high_resists)


def _suit_high_pair_key(high_resists):
    return tuple(name for name in SUIT_RESISTS if name in high_resists)


def _suit_candidate_score(candidate):
    high_resists = candidate.get("HighResists", ())
    high_values = [candidate["Resists"].get(name, 0) for name in high_resists]
    if not high_values:
        return (0, 0, 0, 0)
    return (
        sum(high_values),
        min(high_values),
        max(high_values),
        sum(candidate["Resists"].values()),
    )


def _suit_is_better_candidate(candidate, current):
    return _suit_candidate_score(candidate) > _suit_candidate_score(current)


def _suit_remove_candidate(candidates_by_slot, candidate):
    slot_name = candidate.get("Slot")
    serial = candidate.get("Serial")
    candidates = candidates_by_slot.get(slot_name, [])
    candidates_by_slot[slot_name] = [
        item for item in candidates if item.get("Serial") != serial
    ]
    return len(candidates_by_slot[slot_name]) != len(candidates)


def _suit_high_counts(combo):
    counts = dict((name, 0) for name in SUIT_RESISTS)
    for candidate in combo:
        for resist_name in candidate.get("HighResists", ()):
            counts[resist_name] += 1
    return counts


def _suit_high_balance_score_from_counts(counts):
    missing = 0
    overflow = 0
    spread = 0
    values = []
    for resist_name in SUIT_RESISTS:
        value = counts.get(resist_name, 0)
        values.append(value)
        missing += max(0, SUIT_HIGH_BALANCE_MIN - value)
        overflow += max(0, value - SUIT_HIGH_BALANCE_MAX)
    if values:
        spread = max(values) - min(values)
    return missing, overflow, spread


def _suit_high_balance_score(combo):
    return _suit_high_balance_score_from_counts(_suit_high_counts(combo))


def _suit_has_balanced_highs(combo):
    missing, overflow, _ = _suit_high_balance_score(combo)
    return missing == 0 and overflow == 0


def _suit_is_exceptional(props):
    return any("exceptional" in prop.lower() for prop in props)


def _suit_read_item(item, slot_name):
    Items.WaitForProps(item, 1000)
    props = Items.GetPropStringList(item)
    item_name = props[0] if props else slot_name
    resists = _suit_parse_resists(props)
    return {
        "Slot": slot_name,
        "Serial": _serial(item),
        "Item": item,
        "Name": item_name,
        "Exceptional": _suit_is_exceptional(props),
        "Resists": resists,
        "HighResists": _suit_high_resists(resists),
        "Rows": [],
    }


def _suit_slot_for_item(item, body):
    Items.WaitForProps(item, 1000)
    props = Items.GetPropStringList(item)
    item_name = props[0].lower() if props else ""
    graphic = getattr(item, "Graphic", 0)
    for slot_name in SUIT_BODY_ITEMS.get(body, ()):
        item_def = SUIT_ITEM_DEFS[slot_name]
        expected_graphic = item_def.get("graphic")
        if expected_graphic is not None and int(expected_graphic) == graphic:
            return slot_name
        expected_name = (item_def.get("name") or "").lower()
        if expected_name and expected_name in item_name:
            return slot_name
    SuitLog("scan skip: item {} graphic={} name={!r} did not match body {}".format(
        _debug_hex(_serial(item)),
        _debug_hex(graphic),
        item_name,
        body,
    ))
    return None


def _suit_load_kept_candidates(body, candidates_by_slot, require_exceptional=True, require_high_resists=True, required=True):
    container = _suit_get_keep_container(required=required)
    if not container:
        SuitLog("scan skipped: no good-piece container selected for body={} required={}".format(body, required))
        return 0
    serial = _serial(container)
    Items.WaitForContents(serial, 500)
    try:
        items = API.ItemsInContainer(serial, True) or []
    except Exception:
        items = []
    SuitLog("scan start: container={} body={} items={} require_exceptional={} require_high_resists={}".format(
        _debug_hex(serial),
        body,
        len(items),
        require_exceptional,
        require_high_resists,
    ))

    known_serials = set()
    for candidates in candidates_by_slot.values():
        for candidate in candidates:
            known_serials.add(candidate.get("Serial"))

    loaded = 0
    for item in items:
        item_serial = _serial(item)
        if item_serial in known_serials:
            SuitLog("scan skip: duplicate serial {}".format(_debug_hex(item_serial)))
            continue
        slot_name = _suit_slot_for_item(item, body)
        if not slot_name:
            continue
        candidate = _suit_read_item(item, slot_name)
        if require_exceptional and not candidate.get("Exceptional"):
            SuitLog("scan reject: {} reason=not exceptional".format(_suit_log_candidate(candidate)))
            continue
        if require_high_resists and len(candidate.get("HighResists", ())) != SUIT_HIGH_RESIST_COUNT:
            SuitLog("scan reject: {} reason=high_resist_count expected={} actual={}".format(
                _suit_log_candidate(candidate),
                SUIT_HIGH_RESIST_COUNT,
                len(candidate.get("HighResists", ())),
            ))
            continue
        candidates_by_slot[slot_name].append(candidate)
        known_serials.add(item_serial)
        loaded += 1
        SuitLog("scan accept: {}".format(_suit_log_candidate(candidate)))
    SuitLog("scan complete: loaded={} counts=[{}]".format(loaded, _suit_log_slot_counts(candidates_by_slot)))
    return loaded


def _suit_best_candidate(candidates):
    if not candidates:
        SuitLog("best candidate: none")
        return None
    best = max(candidates, key=_suit_candidate_score)
    SuitLog("best candidate: selected {} from {} candidate(s)".format(_suit_log_candidate(best), len(candidates)))
    return best


def _suit_scan_good_pieces(body, require_exceptional=False, require_high_resists=False, update_rows=True, required=False):
    slot_names = list(SUIT_BODY_ITEMS.get(body, ()))
    candidates_by_slot = dict((slot_name, []) for slot_name in slot_names)
    SuitLog("scan good pieces: body={} slots={} update_rows={} required={}".format(
        body,
        ",".join(slot_names),
        update_rows,
        required,
    ))
    loaded = _suit_load_kept_candidates(
        body,
        candidates_by_slot,
        require_exceptional=require_exceptional,
        require_high_resists=require_high_resists,
        required=required,
    )
    selected_by_slot = {}
    for slot_name in slot_names:
        selected = _suit_best_candidate(candidates_by_slot.get(slot_name, []))
        if not selected:
            SuitLog("scan choose: slot={} no saved candidate".format(slot_name))
            continue
        selected_by_slot[slot_name] = selected
        SuitLog("scan choose: slot={} {}".format(slot_name, _suit_log_candidate(selected)))
        if update_rows:
            _suit_update_slot(
                slot_name,
                selected["Serial"],
                "Chosen: Saved",
                _suit_resist_text(selected["Resists"]),
                _suit_high_text(selected.get("HighResists", ())),
            )
    SuitLog("scan result: selected={} loaded={} counts=[{}]".format(
        len(selected_by_slot),
        loaded,
        _suit_log_slot_counts(candidates_by_slot),
    ))
    return selected_by_slot, candidates_by_slot, loaded


def _suit_resist_text(resists):
    return "P{}/F{}/C{}/Po{}/E{}".format(
        resists.get("Physical Resist", 0),
        resists.get("Fire Resist", 0),
        resists.get("Cold Resist", 0),
        resists.get("Poison Resist", 0),
        resists.get("Energy Resist", 0),
    )


def _suit_log_candidate(candidate):
    if not candidate:
        return "None"
    return "{} serial={} ex={} resists={} highs={} score={} rows={}".format(
        candidate.get("Slot", "?"),
        _debug_hex(candidate.get("Serial", 0)),
        bool(candidate.get("Exceptional")),
        _suit_resist_text(candidate.get("Resists", {})),
        _suit_high_text(candidate.get("HighResists", ())),
        _suit_candidate_score(candidate),
        _suit_plan_text(candidate.get("Rows", [])),
    )


def _suit_log_slot_counts(candidates_by_slot):
    return ", ".join(
        "{}={}".format(slot_name, len(candidates_by_slot.get(slot_name, [])))
        for slot_name in candidates_by_slot
    )


def _suit_hue_store():
    store = state.get("SuitSelectedItemHues")
    if not isinstance(store, dict):
        store = {}
        state["SuitSelectedItemHues"] = store
    return store


def _suit_restore_item_hue(serial):
    serial = int(serial or 0)
    if not serial:
        return
    store = _suit_hue_store()
    key = str(serial)
    if key not in store:
        return
    original_hue = store.pop(key)
    item = API.FindItem(serial)
    if not item:
        SuitLog("hue restore skipped: missing item serial={}".format(_debug_hex(serial)))
        return
    try:
        item.SetHue(int(original_hue or 0))
        SuitLog("hue restored: serial={} hue={}".format(_debug_hex(serial), original_hue))
    except Exception as exc:
        SuitLog("hue restore failed: serial={} error={}".format(_debug_hex(serial), exc))


def _suit_clear_selected_item_hues(keep_serials=None):
    keep = set(int(serial or 0) for serial in (keep_serials or []))
    for key in list(_suit_hue_store().keys()):
        try:
            serial = int(key)
        except Exception:
            serial = 0
        if serial and serial in keep:
            continue
        _suit_restore_item_hue(serial)


def _suit_set_selected_item_hue(candidate, reason="selected"):
    serial = int((candidate or {}).get("Serial", 0) or 0)
    if not serial:
        return
    item = _suit_refresh_item(candidate) if candidate else API.FindItem(serial)
    if not item:
        SuitLog("hue selected skipped: missing item serial={} reason={}".format(_debug_hex(serial), reason))
        return
    store = _suit_hue_store()
    key = str(serial)
    if key not in store:
        try:
            store[key] = int(getattr(item, "Hue", 0) or 0)
        except Exception:
            store[key] = 0
    try:
        item.SetHue(SUIT_SELECTED_ITEM_HUE)
        SuitLog("hue selected: {} hue={} reason={}".format(
            _suit_log_candidate(candidate),
            SUIT_SELECTED_ITEM_HUE,
            reason,
        ))
    except Exception as exc:
        SuitLog("hue selected failed: serial={} reason={} error={}".format(_debug_hex(serial), reason, exc))


def _suit_empty_resists():
    return dict((name, 0) for name in SUIT_RESISTS)


def _suit_parse_resist_text(text):
    values = _suit_empty_resists()
    if not text:
        return values
    for part in str(text).split("/"):
        part = part.strip()
        match = re.match(r"([A-Za-z]+)\s*(-?\d+)", part)
        if not match:
            continue
        key = match.group(1).lower()
        value = int(match.group(2))
        if key == "p":
            values["Physical Resist"] = value
        elif key == "f":
            values["Fire Resist"] = value
        elif key == "c":
            values["Cold Resist"] = value
        elif key == "po":
            values["Poison Resist"] = value
        elif key == "e":
            values["Energy Resist"] = value
    return values


def _suit_plan_resist_additions(plan_text):
    additions = _suit_empty_resists()
    if not plan_text:
        return additions
    aliases = {
        "phys": "Physical Resist",
        "fire": "Fire Resist",
        "cold": "Cold Resist",
        "pois": "Poison Resist",
        "ener": "Energy Resist",
    }
    for short_name, resist_name in aliases.items():
        match = re.search(r"{}\+(-?\d+)".format(short_name), str(plan_text), re.IGNORECASE)
        if match:
            additions[resist_name] += int(match.group(1))
    return additions


def _suit_expected_row_resists(row):
    values = _suit_parse_resist_text(row.get("Resists", ""))
    if row.get("Status") == "Done":
        return values
    additions = _suit_plan_resist_additions(row.get("Plan", ""))
    for resist_name in SUIT_RESISTS:
        values[resist_name] += additions.get(resist_name, 0)
    return values


def _suit_expected_total_resists(rows):
    totals = _suit_empty_resists()
    for row in rows:
        values = _suit_expected_row_resists(row)
        for resist_name in SUIT_RESISTS:
            totals[resist_name] += values.get(resist_name, 0)
    return totals


def _suit_plan_has_final_expectation(plan_text):
    text = str(plan_text or "").strip()
    if not text or text == "-":
        return False
    lower = text.lower()
    if lower.startswith("high ") or lower == "flat resists":
        return False
    return True


def _suit_row_has_final_expectation(row):
    if not row.get("Serial") or not row.get("Resists"):
        return False
    status = str(row.get("Status", "")).lower()
    if status == "done":
        return True
    if "selected" in status or "imbu" in status:
        return True
    if "chosen" in status and _suit_plan_has_final_expectation(row.get("Plan", "")):
        return True
    return False


def _suit_rows_have_final_expectation(rows):
    active_rows = [row for row in rows if row.get("Slot")]
    return bool(active_rows) and all(_suit_row_has_final_expectation(row) for row in active_rows)


def _suit_prop_short_name(prop):
    return {
        "Lower Mana Cost": "LMC",
        "Lower Reagent Cost": "LRC",
        "Mana Regeneration": "MR",
        "Mana Increase": "MI",
        "Physical Resist": "Phys",
        "Fire Resist": "Fire",
        "Cold Resist": "Cold",
        "Poison Resist": "Pois",
        "Energy Resist": "Ener",
    }.get(prop, prop.replace(" Resist", "R"))


def _suit_plan_text(rows):
    active = [row for row in rows if row.get("Prop") != "None" and row.get("Val", 0)]
    if not active:
        return "-"
    parts = []
    for row in active:
        value = "+{}".format(row["Val"]) if _suit_row_is_additive_resist(row) else str(row["Val"])
        parts.append("{}{}".format(_suit_prop_short_name(row["Prop"]), value))
    return ", ".join(parts)


def _suit_parse_plan_rows(plan_text):
    rows = []
    if not plan_text or str(plan_text).strip() == "-":
        return rows
    aliases = {
        "lmc": "Lower Mana Cost",
        "lrc": "Lower Reagent Cost",
        "mr": "Mana Regeneration",
        "mi": "Mana Increase",
        "phys": "Physical Resist",
        "fire": "Fire Resist",
        "cold": "Cold Resist",
        "pois": "Poison Resist",
        "poison": "Poison Resist",
        "ener": "Energy Resist",
        "energy": "Energy Resist",
    }
    for token in str(plan_text).split(","):
        token = token.strip()
        match = re.match(r"([A-Za-z ]+)([+-]?\d+)$", token)
        if not match:
            continue
        prop = aliases.get(match.group(1).strip().lower())
        if not prop:
            continue
        raw_value = match.group(2)
        row = {"Prop": prop, "Val": int(raw_value)}
        if prop in SUIT_RESISTS and raw_value.startswith("+"):
            row["Mode"] = "Add"
        rows.append(row)
    return rows


def _suit_plan_extra_texts(rows):
    extras = []
    for row in rows:
        prop = row.get("Prop", "None")
        val = int(row.get("Val", 0) or 0)
        if prop == "None" or prop in SUIT_RESISTS or not val:
            continue
        extras.append("{} {}".format(_suit_prop_short_name(prop), val))
    return extras


def _suit_expected_plan_totals(rows):
    totals = {}
    for row in rows:
        for plan_row in _suit_parse_plan_rows(row.get("Plan", "")):
            prop = plan_row.get("Prop", "None")
            if prop == "None" or prop in SUIT_RESISTS:
                continue
            totals[prop] = totals.get(prop, 0) + int(plan_row.get("Val", 0) or 0)
    return totals


def _suit_set_msg(message, hue=55):
    state["SuitMsg"] = message
    state["Msg"] = message
    Misc.SendMessage(message, hue)
    send_calculator()


def _suit_store_msg(message):
    state["SuitMsg"] = message
    state["Msg"] = message


def _suit_should_stop():
    try:
        API.ProcessCallbacks()
    except Exception:
        pass
    return state.get("SuitStop", False) or API.StopRequested


def _suit_init_rows(body):
    _suit_clear_selected_item_hues()
    marked = int(state.get("SuitMarkedSerial", 0) or 0)
    if marked:
        marked_item = API.FindItem(marked)
        if marked_item:
            try:
                marked_item.SetOutlineColor(None)
            except Exception:
                pass
    state["SuitMarkedSerial"] = 0
    state["SuitRows"] = []
    for slot_name in SUIT_BODY_ITEMS[body]:
        state["SuitRows"].append({
            "Slot": slot_name,
            "Serial": 0,
            "Status": "Pending",
            "Resists": "",
            "Plan": "",
        })


def _suit_update_slot(slot_name, serial=0, status=None, resists=None, plan=None):
    for row in state.get("SuitRows", []):
        if row.get("Slot") != slot_name:
            continue
        if serial:
            row["Serial"] = serial
        if status is not None:
            row["Status"] = status
        if resists is not None:
            row["Resists"] = resists
        if plan is not None:
            row["Plan"] = plan
        if serial and status is not None:
            status_lower = str(status).lower()
            if (
                "chosen" in status_lower
                or "selected" in status_lower
                or status_lower == "done"
                or status_lower == "crafted"
            ):
                _suit_set_selected_item_hue(
                    {
                        "Slot": slot_name,
                        "Serial": serial,
                        "Resists": _suit_parse_resist_text(row.get("Resists", "")),
                        "Rows": [],
                    },
                    "slot-status {}".format(status),
                )
        break
    send_calculator()


def _suit_get_craft():
    serial = state.get("MatCont", 0)
    if not serial:
        raise Exception("Select material container first.")
    resource_chest = API.FindItem(serial)
    if not resource_chest:
        raise Exception("Material container not found.")
    return Craft(None, TAILORING_CRAFTING_INFO, resource_chest)


def _suit_get_keep_container(required=False):
    serial = state.get("SuitKeepCont", 0)
    if not serial:
        if required:
            raise Exception("Select good-piece container first.")
        return None
    container = API.FindItem(serial)
    if not container:
        raise Exception("Good-piece container not found.")
    Items.WaitForContents(serial, 500)
    return container


def _suit_refresh_item(candidate):
    item = API.FindItem(candidate.get("Serial", 0))
    if item:
        candidate["Item"] = item
    return candidate.get("Item")


def _suit_move_candidate(candidate, destination):
    SuitLog("move begin: {} destination={}".format(_suit_log_candidate(candidate), _debug_hex(destination)))
    item = _suit_refresh_item(candidate)
    if not item:
        SuitLog("move failed: missing item {}".format(_suit_log_candidate(candidate)))
        return False
    if not Items.Move(item, destination, 0):
        SuitLog("move failed: API move false {}".format(_suit_log_candidate(candidate)))
        return False
    Misc.Pause(1000)
    _suit_refresh_item(candidate)
    SuitLog("move complete: {}".format(_suit_log_candidate(candidate)))
    return True


def _suit_keep_candidate(candidate):
    container = _suit_get_keep_container(required=True)
    kept = _suit_move_candidate(candidate, _serial(container))
    SuitLog("keep candidate: kept={} {}".format(kept, _suit_log_candidate(candidate)))
    return kept


def _suit_prepare_piece_for_imbue(piece):
    SuitLog("prepare imbue: {}".format(_suit_log_candidate(piece)))
    item = _suit_refresh_item(piece)
    if not item:
        SuitLog("prepare failed: missing item {}".format(_suit_log_candidate(piece)))
        _suit_set_msg("Could not find {} for imbuing.".format(piece["Slot"]), 33)
        return False
    if _serial(getattr(item, "Container", Player.Backpack.Serial)) != Player.Backpack.Serial:
        if not _suit_move_candidate(piece, Player.Backpack.Serial):
            SuitLog("prepare failed: could not move to backpack {}".format(_suit_log_candidate(piece)))
            _suit_set_msg("Could not move {} to backpack.".format(piece["Slot"]), 33)
            return False
    SuitLog("prepare complete: {}".format(_suit_log_candidate(piece)))
    return True


def _suit_craft_piece(craft, slot_name, require_exceptional):
    SuitLog("craft begin: slot={} require_exceptional={}".format(slot_name, require_exceptional))
    item_def = SUIT_ITEM_DEFS[slot_name]
    crafted = craft.craft_item(
        item_def,
        SUIT_NORMAL_LEATHER_HUE,
        SUIT_NORMAL_LEATHER_MATERIAL,
        require_exceptional=require_exceptional,
        recycle_rejected=True,
    )
    if not crafted:
        SuitLog("craft failed: slot={} no crafted item".format(slot_name))
        return None
    candidate = _suit_read_item(crafted, slot_name)
    SuitLog("craft result: {}".format(_suit_log_candidate(candidate)))
    return candidate


def _suit_max_weight(exceptional):
    return 500 if exceptional else 450


def _suit_resist_row_count(rows):
    return sum(1 for row in rows if row.get("Prop") in SUIT_RESISTS and row.get("Val", 0))


def _suit_try_add_row(rows, prop, val, exceptional=True, mode=None):
    if val <= 0:
        return True
    active_rows = [row for row in rows if row.get("Prop") != "None" and row.get("Val", 0)]
    if any(row["Prop"] == prop for row in active_rows):
        return False
    if prop in SUIT_RESISTS and _suit_resist_row_count(active_rows) >= SUIT_MAX_RESIST_ROWS:
        return False
    if len(active_rows) >= SUIT_MAX_ROWS:
        return False
    new_row = {"Prop": prop, "Val": val}
    if mode:
        new_row["Mode"] = mode
    candidate = active_rows + [new_row]
    if _suit_rows_weight(candidate) > _suit_max_weight(exceptional):
        return False
    rows[:] = candidate
    return True


def _suit_choose_optional(rows, exceptional=True):
    active_rows = [row for row in rows if row.get("Prop") != "None" and row.get("Val", 0)]
    optional_props = (("Mana Increase", 8, 0), ("Mana Regeneration", 2, 1))
    while len(active_rows) < SUIT_MAX_ROWS:
        existing_props = set(row.get("Prop") for row in active_rows)
        best = None
        for prop, max_val, prefer in optional_props:
            if prop in existing_props:
                continue
            for val in range(max_val, 0, -1):
                candidate = active_rows + [{"Prop": prop, "Val": val}]
                weight = _suit_rows_weight(candidate)
                if weight > _suit_max_weight(exceptional):
                    continue
                diff = abs(_suit_max_weight(exceptional) - weight)
                score = (diff, prefer, -val)
                if best is None or score < best[0]:
                    best = (score, {"Prop": prop, "Val": val})
        if not best:
            break
        active_rows.append(best[1])
    return active_rows


def _suit_distribute_values(total, count, preferred_value):
    if count <= 0:
        return []
    total = max(0, int(total or 0))
    preferred_value = max(0, int(preferred_value or 0))
    values = [min(preferred_value, total // count) for _ in range(count)]
    remaining = total - sum(values)
    index = 0
    while remaining > 0 and values:
        if values[index] < preferred_value:
            values[index] += 1
            remaining -= 1
        index = (index + 1) % len(values)
        if all(value >= preferred_value for value in values):
            break
    return values


def _suit_mage_required_rows_by_piece(count):
    rows_by_piece = [[] for _ in range(count)]
    for row in SUIT_MAGE_REQUIRED_ROWS:
        prop = row.get("Prop")
        preferred_value = int(row.get("Val", 0) or 0)
        total = SUIT_MAGE_STAT_CAPS.get(prop, preferred_value * count)
        values = _suit_distribute_values(total, count, preferred_value)
        for index, value in enumerate(values):
            if value > 0:
                rows_by_piece[index].append({"Prop": prop, "Val": value})
    return rows_by_piece


def _suit_allocate_mage_rows(candidates):
    planned = []
    required_rows_by_piece = _suit_mage_required_rows_by_piece(len(candidates))
    totals = dict((name, 0) for name in SUIT_RESISTS)
    for index, candidate in enumerate(candidates):
        candidate["Rows"] = [dict(row) for row in required_rows_by_piece[index]]
        for resist_name in SUIT_RESISTS:
            totals[resist_name] += candidate["Resists"].get(resist_name, 0)
        planned.append(candidate)

    deficits = dict((name, max(0, SUIT_RESIST_TARGET - totals[name])) for name in SUIT_RESISTS)
    seen = set()

    def snapshot():
        return tuple(
            (
                tuple(deficits[name] for name in SUIT_RESISTS),
                tuple(
                    tuple((row.get("Prop"), row.get("Val"), row.get("Mode")) for row in item["Rows"])
                    for item in planned
                ),
            )
        )

    def search():
        if all(deficits[name] <= 0 for name in SUIT_RESISTS):
            return True

        key = snapshot()
        if key in seen:
            return False
        seen.add(key)

        resist_name = max(SUIT_RESISTS, key=lambda name: deficits[name])
        if deficits[resist_name] <= 0:
            return True

        pieces = sorted(
            enumerate(planned),
            key=lambda indexed: (
                _suit_resist_row_count(indexed[1]["Rows"]),
                _suit_rows_weight(indexed[1]["Rows"]),
                indexed[1]["Resists"].get(resist_name, 0),
            ),
        )
        for index, item in pieces:
            if any(row["Prop"] == resist_name for row in item["Rows"]):
                continue
            max_add = min(15, deficits[resist_name])
            for val in range(max_add, 0, -1):
                rows = [dict(row) for row in item["Rows"]]
                if not _suit_try_add_row(rows, resist_name, val, True, mode="Add"):
                    continue
                previous_rows = item["Rows"]
                item["Rows"] = rows
                deficits[resist_name] -= val
                if search():
                    return True
                deficits[resist_name] += val
                item["Rows"] = previous_rows
        return False

    if not search():
        return None

    for item in planned:
        item["Rows"] = _suit_choose_optional(item["Rows"], True)
        if len(item["Rows"]) > SUIT_MAX_ROWS:
            return None
        if _suit_rows_weight(item["Rows"]) > _suit_max_weight(True):
            return None
    return planned


def _suit_combo_totals(combo):
    totals = dict((name, 0) for name in SUIT_RESISTS)
    for candidate in combo:
        for resist_name in SUIT_RESISTS:
            totals[resist_name] += candidate["Resists"].get(resist_name, 0)
    return totals


def _suit_missing_score(totals):
    missing = [max(0, SUIT_RESIST_TARGET - totals[name]) for name in SUIT_RESISTS]
    return sum(missing), max(missing), tuple(missing)


def _suit_trim_states(states, limit=50000):
    if len(states) <= limit:
        return states
    ranked = sorted(
        states.items(),
        key=lambda item: (
            _suit_missing_score(dict(zip(SUIT_RESISTS, item[0][0]))),
            _suit_high_balance_score_from_counts(dict(zip(SUIT_RESISTS, item[0][1]))),
        ),
    )
    return dict(ranked[:limit])


def _suit_solve_mage(candidates_by_slot):
    SuitLog("mage solve start: counts=[{}]".format(_suit_log_slot_counts(candidates_by_slot)))
    missing_slots = [slot for slot in candidates_by_slot if not candidates_by_slot.get(slot)]
    if missing_slots:
        SuitLog("mage solve blocked: missing slots={}".format(", ".join(missing_slots)))
        return None

    empty_totals = tuple(0 for _ in SUIT_RESISTS)
    empty_highs = tuple(0 for _ in SUIT_RESISTS)
    states = {(empty_totals, empty_highs, ()): []}
    for slot_name in candidates_by_slot:
        new_states = {}
        previous_state_count = len(states)
        for state_key, combo in states.items():
            totals_key, highs_key = state_key[:2]
            for candidate in candidates_by_slot[slot_name]:
                next_totals = []
                for index, resist_name in enumerate(SUIT_RESISTS):
                    value = totals_key[index] + candidate["Resists"].get(resist_name, 0)
                    next_totals.append(min(SUIT_RESIST_TARGET, value))

                next_highs = list(highs_key)
                for high_resist in candidate.get("HighResists", ()):
                    if high_resist in SUIT_RESISTS:
                        next_highs[SUIT_RESISTS.index(high_resist)] += 1
                if any(value > SUIT_HIGH_BALANCE_MAX for value in next_highs):
                    continue

                next_combo = combo + [candidate]
                next_serials = tuple(item.get("Serial") for item in next_combo)
                next_key = (tuple(next_totals), tuple(next_highs), next_serials)
                if next_key not in new_states:
                    new_states[next_key] = next_combo
        states = _suit_trim_states(new_states)
        SuitLog("mage solve slot={} candidates={} states {}->{}".format(
            slot_name,
            len(candidates_by_slot.get(slot_name, [])),
            previous_state_count,
            len(states),
        ))

    ranked_combos = sorted(
        states.values(),
        key=lambda combo: (
            _suit_missing_score(_suit_combo_totals(combo)),
            _suit_high_balance_score(combo),
            -sum(sum(item["Resists"].values()) for item in combo),
        ),
    )
    for combo in ranked_combos:
        if not _suit_has_balanced_highs(combo):
            continue
        plan = _suit_allocate_mage_rows([dict(item) for item in combo])
        if plan:
            totals = _suit_combo_totals(plan)
            SuitLog("mage solve success: totals={} high_counts={} plan={}".format(
                _suit_resist_text(totals),
                _suit_high_count_text(_suit_high_counts(plan)),
                " | ".join(_suit_log_candidate(piece) for piece in plan),
            ))
            return plan
    SuitLog("mage solve failed: ranked_combos={} no balanced/allocation fit".format(len(ranked_combos)))
    return None


def _suit_select_plan(plan, active_by_slot=None):
    SuitLog("select plan: pieces={} totals={}".format(
        len(plan),
        _suit_resist_text(_suit_combo_totals(plan)),
    ))
    keep_serials = [piece.get("Serial", 0) for piece in plan]
    _suit_clear_selected_item_hues(keep_serials)
    for piece in plan:
        slot_name = piece.get("Slot")
        if active_by_slot is not None and slot_name:
            active_by_slot[slot_name] = piece
        SuitLog("select plan piece: {}".format(_suit_log_candidate(piece)))
        _suit_set_selected_item_hue(piece, "selected-plan")
        _suit_update_slot(
            slot_name,
            piece["Serial"],
            "Selected",
            _suit_resist_text(piece["Resists"]),
            _suit_plan_text(piece.get("Rows", [])),
        )


def _suit_scan_saved_mage_plan(body, update_rows=True, required=True):
    slot_names = list(SUIT_BODY_ITEMS.get(body, ()))
    candidates_by_slot = dict((slot_name, []) for slot_name in slot_names)
    loaded = _suit_load_kept_candidates(
        body,
        candidates_by_slot,
        require_exceptional=True,
        require_high_resists=True,
        required=required,
    )
    SuitLog("mage scan solve: loaded={} counts=[{}]".format(
        loaded,
        _suit_log_slot_counts(candidates_by_slot),
    ))

    plan = _suit_solve_mage(candidates_by_slot)
    if not plan:
        SuitLog("mage scan solve failed: no README-valid six-piece plan loaded={} counts=[{}]".format(
            loaded,
            _suit_log_slot_counts(candidates_by_slot),
        ))
        preview = _suit_preview_mage_candidates(candidates_by_slot, slot_names, update_rows)
        if preview:
            SuitLog("mage scan preview: highs={} totals={} pieces={}".format(
                _suit_high_count_text(_suit_high_counts(preview)),
                _suit_resist_text(_suit_combo_totals(preview)),
                " | ".join(_suit_log_candidate(piece) for piece in preview),
            ))
        return {}, candidates_by_slot, loaded, None

    counts = _suit_high_counts(plan)
    missing, overflow, spread = _suit_high_balance_score(plan)
    if missing or overflow:
        SuitLog("mage scan solve rejected: unbalanced highs={} missing={} overflow={} spread={}".format(
            _suit_high_count_text(counts),
            missing,
            overflow,
            spread,
        ))
        _suit_preview_mage_candidates(candidates_by_slot, slot_names, update_rows)
        return {}, candidates_by_slot, loaded, None

    selected_by_slot = dict((piece.get("Slot"), piece) for piece in plan)
    SuitLog("mage scan solve selected: selected={} highs={} totals={} pieces={}".format(
        len(selected_by_slot),
        _suit_high_count_text(counts),
        _suit_resist_text(_suit_combo_totals(plan)),
        " | ".join(_suit_log_candidate(piece) for piece in plan),
    ))
    if update_rows:
        _suit_select_plan(plan, None)
    return selected_by_slot, candidates_by_slot, loaded, plan


def _suit_recycle_candidates(craft, candidates_by_slot, keep_serials=None):
    keep_serials = keep_serials or set()
    _suit_get_keep_container(required=False)
    for candidates in candidates_by_slot.values():
        for candidate in candidates:
            if candidate.get("Serial") in keep_serials:
                continue
            craft.dispose_item(_suit_refresh_item(candidate), SUIT_ITEM_DEFS[candidate["Slot"]])


def _suit_verify_piece(piece, quiet=False):
    SuitLog("verify start: quiet={} {}".format(quiet, _suit_log_candidate(piece)))
    item = _suit_refresh_item(piece)
    if not item:
        SuitLog("verify failed: missing item {}".format(_suit_log_candidate(piece)))
        if not quiet:
            _suit_set_msg("Could not verify {} after imbuing.".format(piece["Slot"]), 33)
        return False
    Items.WaitForProps(item, 1000)
    props = Items.GetPropStringList(item)
    if not props:
        SuitLog("verify failed: no props {}".format(_suit_log_candidate(piece)))
        if not quiet:
            _suit_set_msg("Could not read {} after imbuing.".format(piece["Slot"]), 33)
        return False

    final_resists = _suit_parse_resists(props)
    final_props = _suit_parse_prop_values(props)
    incomplete = []
    for row in piece.get("Rows", []):
        prop = row.get("Prop", "None")
        val = int(row.get("Val", 0) or 0)
        if prop == "None" or val <= 0:
            continue
        if prop in SUIT_RESISTS:
            required = val
            if _suit_row_is_additive_resist(row):
                required = piece["Resists"].get(prop, 0) + val
            current = final_resists.get(prop, 0)
        else:
            required = val
            current = final_props.get(prop, 0)
        if current < required:
            incomplete.append("{} {}/{}".format(prop.replace(" Resist", "R"), current, required))

    if incomplete:
        SuitLog("verify incomplete: {} missing={}".format(_suit_log_candidate(piece), ", ".join(incomplete)))
        if not quiet:
            _suit_set_msg(
                "{} incomplete after imbuing: {}".format(piece["Slot"], ", ".join(incomplete)),
                33,
            )
        return False

    piece["Resists"] = final_resists
    SuitLog("verify success: {} final_resists={}".format(piece.get("Slot"), _suit_resist_text(final_resists)))
    return True


def _suit_imbue_piece(piece):
    SuitLog("imbue begin: {}".format(_suit_log_candidate(piece)))
    state["Category"] = "Armor"
    state["ItemGroup"] = "Armor"
    state["ItemName"] = piece["Slot"]
    state["Exceptional"] = bool(piece.get("Exceptional", True))
    state["Whetstone"] = False
    state["CustomMode"] = False
    state["SelectedPreset"] = PRESET_CUSTOM
    state["Rows"] = _suit_copy_rows(piece["Rows"])
    state["ImbueTarget"] = piece["Serial"]
    result = AutoImbue()
    SuitLog("imbue result: slot={} serial={} result={}".format(
        piece.get("Slot"),
        _debug_hex(piece.get("Serial", 0)),
        result,
    ))
    return result


def _suit_imbue_plan(plan, verify_resist_target=False):
    for piece in plan:
        if _suit_should_stop():
            _suit_set_msg("Suit crafting stopped.", 33)
            return False
        if not _suit_prepare_piece_for_imbue(piece):
            return False
        if _suit_verify_piece(piece, quiet=True):
            SuitLog("imbue skip: already satisfies plan {}".format(_suit_log_candidate(piece)))
            _suit_update_slot(piece["Slot"], piece["Serial"], "Done", _suit_resist_text(piece["Resists"]), _suit_plan_text(piece["Rows"]))
            continue
        _suit_update_slot(piece["Slot"], piece["Serial"], "Imbuing", _suit_resist_text(piece["Resists"]), _suit_plan_text(piece["Rows"]))
        if not _suit_imbue_piece(piece):
            SuitLog("imbue failed: {}".format(_suit_log_candidate(piece)))
            _suit_set_msg("{} imbuing failed.".format(piece["Slot"]), 33)
            return False
        if not _suit_verify_piece(piece):
            return False
        if _suit_should_stop():
            _suit_set_msg("Suit crafting stopped.", 33)
            return False
        _suit_update_slot(piece["Slot"], piece["Serial"], "Done", _suit_resist_text(piece["Resists"]), _suit_plan_text(piece["Rows"]))
        SuitLog("imbue done: {}".format(_suit_log_candidate(piece)))

    if verify_resist_target:
        totals = _suit_combo_totals(plan)
        short = [
            "{} {}".format(name.replace(" Resist", ""), max(0, SUIT_RESIST_TARGET - totals[name]))
            for name in SUIT_RESISTS
            if totals[name] < SUIT_RESIST_TARGET
        ]
        if short:
            _suit_set_msg("Mage suit short after imbuing: {}".format(", ".join(short)), 33)
            return False
    return True


def _suit_active_combo(active_by_slot, slot_names):
    return [active_by_slot.get(slot_name) for slot_name in slot_names if active_by_slot.get(slot_name)]


def _suit_active_candidates_by_slot(active_by_slot, slot_names):
    return dict((slot_name, [active_by_slot[slot_name]]) for slot_name in slot_names if active_by_slot.get(slot_name))


def _suit_high_count_text(counts):
    labels = (
        ("P", "Physical Resist"),
        ("F", "Fire Resist"),
        ("C", "Cold Resist"),
        ("Po", "Poison Resist"),
        ("E", "Energy Resist"),
    )
    return "/".join("{}{}".format(label, counts.get(name, 0)) for label, name in labels)


def _suit_missing_high_text(counts):
    missing = []
    for label, name in (
        ("P", "Physical Resist"),
        ("F", "Fire Resist"),
        ("C", "Cold Resist"),
        ("Po", "Poison Resist"),
        ("E", "Energy Resist"),
    ):
        needed = max(0, SUIT_HIGH_BALANCE_MIN - counts.get(name, 0))
        if needed:
            missing.append("{}+{}".format(label, needed))
    return ", ".join(missing)


def _suit_mage_incomplete_message(candidates_by_slot, loaded):
    slot_names = list(candidates_by_slot.keys())
    next_text = _suit_next_mage_craft_text(candidates_by_slot, slot_names)
    combo = _suit_best_available_mage_combo(candidates_by_slot, slot_names)
    if combo:
        counts = _suit_high_counts(combo)
        missing = _suit_missing_high_text(counts)
        if missing:
            return "No Mage suit yet: need highs {}.{}".format(
                missing,
                next_text,
            )
        return "No Mage suit yet: highs {}.{}".format(
            _suit_high_count_text(counts),
            next_text,
        )

    missing_slots = [
        slot_name for slot_name in slot_names
        if not candidates_by_slot.get(slot_name)
    ]
    if missing_slots:
        return "No Mage suit yet: missing {}.{}".format(
            ", ".join(missing_slots[:2]) + ("..." if len(missing_slots) > 2 else ""),
            next_text,
        )
    return "No Mage suit yet.{}".format(next_text)


def _suit_next_mage_craft_text(candidates_by_slot, slot_names=None):
    slot_names = list(slot_names or candidates_by_slot.keys())
    if not slot_names:
        return ""
    active_by_slot = dict((slot_name, None) for slot_name in slot_names)
    combo = _suit_best_available_mage_combo(candidates_by_slot, slot_names)
    for piece in combo:
        active_by_slot[piece.get("Slot")] = piece
    slot_name, reason = _suit_choose_next_mage_craft_slot(
        candidates_by_slot,
        active_by_slot,
        slot_names,
    )
    if not slot_name:
        return ""
    SuitLog("mage incomplete next craft: slot={} reason={}".format(slot_name, reason))
    return " Next craft: {}.".format(slot_name)


def _suit_preview_mage_candidates(candidates_by_slot, slot_names, update_rows=True):
    combo = _suit_best_available_mage_combo(candidates_by_slot, slot_names)
    if not update_rows:
        return combo
    for piece in combo:
        slot_name = piece.get("Slot")
        _suit_update_slot(
            slot_name,
            piece["Serial"],
            "Saved candidate",
            _suit_resist_text(piece["Resists"]),
            _suit_high_text(piece.get("HighResists", ())),
        )
    return combo


def _suit_combo_rank_key(combo):
    totals = _suit_combo_totals(combo)
    return (
        _suit_high_balance_score(combo),
        _suit_missing_score(totals),
        -sum(_suit_candidate_score(piece)[0] for piece in combo),
        -sum(sum(piece["Resists"].values()) for piece in combo),
        tuple(piece.get("Serial", 0) for piece in combo),
    )


def _suit_best_available_mage_combo(candidates_by_slot, slot_names):
    active_slots = [slot_name for slot_name in slot_names if candidates_by_slot.get(slot_name)]
    if not active_slots:
        return []

    empty_totals = tuple(0 for _ in SUIT_RESISTS)
    empty_highs = tuple(0 for _ in SUIT_RESISTS)
    states = {(empty_totals, empty_highs, ()): []}
    for slot_name in active_slots:
        new_states = {}
        for state_key, combo in states.items():
            totals_key, highs_key = state_key[:2]
            for candidate in candidates_by_slot.get(slot_name, []):
                next_totals = []
                for index, resist_name in enumerate(SUIT_RESISTS):
                    value = totals_key[index] + candidate["Resists"].get(resist_name, 0)
                    next_totals.append(min(SUIT_RESIST_TARGET, value))

                next_highs = list(highs_key)
                for high_resist in candidate.get("HighResists", ()):
                    if high_resist in SUIT_RESISTS:
                        next_highs[SUIT_RESISTS.index(high_resist)] += 1

                next_combo = combo + [candidate]
                next_serials = tuple(item.get("Serial") for item in next_combo)
                next_key = (tuple(next_totals), tuple(next_highs), next_serials)
                previous = new_states.get(next_key)
                if previous is None or _suit_combo_rank_key(next_combo) < _suit_combo_rank_key(previous):
                    new_states[next_key] = next_combo
        if len(new_states) > 50000:
            ranked = sorted(new_states.items(), key=lambda item: _suit_combo_rank_key(item[1]))
            new_states = dict(ranked[:50000])
        states = new_states
        if not states:
            return []

    return min(states.values(), key=_suit_combo_rank_key)


def _suit_refresh_active_mage_combo(candidates_by_slot, active_by_slot, slot_names):
    combo = _suit_best_available_mage_combo(candidates_by_slot, slot_names)
    for slot_name in slot_names:
        active_by_slot[slot_name] = None
    for piece in combo:
        active_by_slot[piece.get("Slot")] = piece
    if combo:
        SuitLog("mage active preview: highs={} totals={} pieces={}".format(
            _suit_high_count_text(_suit_high_counts(combo)),
            _suit_resist_text(_suit_combo_totals(combo)),
            " | ".join(_suit_log_candidate(piece) for piece in combo),
        ))
    return combo


def _suit_choose_next_mage_craft_slot(candidates_by_slot, active_by_slot, slot_names):
    missing_active = [slot_name for slot_name in slot_names if not active_by_slot.get(slot_name)]
    if missing_active:
        slot_name = missing_active[0]
        return slot_name, "Missing active slot"

    recraft_slots, reason = _suit_select_recraft_slots(active_by_slot, slot_names)
    if recraft_slots:
        return recraft_slots[0], reason

    ranked = sorted((len(candidates_by_slot.get(slot_name, [])), slot_name) for slot_name in slot_names)
    if ranked:
        return ranked[0][1], "Fewest saved candidates"
    return None, "No suit slots"


def _suit_select_recraft_slots(active_by_slot, slot_names):
    combo = _suit_active_combo(active_by_slot, slot_names)
    if not combo:
        return [slot_names[0]], "No active pieces"

    counts = _suit_high_counts(combo)
    under = set(name for name in SUIT_RESISTS if counts.get(name, 0) < SUIT_HIGH_BALANCE_MIN)
    over = set(name for name in SUIT_RESISTS if counts.get(name, 0) > SUIT_HIGH_BALANCE_MAX)
    totals = _suit_combo_totals(combo)
    deficits = set(name for name in SUIT_RESISTS if totals.get(name, 0) < SUIT_RESIST_TARGET)

    ranked = []
    for slot_name in slot_names:
        item = active_by_slot.get(slot_name)
        if not item:
            continue
        highs = set(item.get("HighResists", ()))
        score = _suit_candidate_score(item)
        total = sum(item["Resists"].values())

        if over:
            over_hits = len(highs & over)
            if not over_hits:
                continue
            under_hits = len(highs & under)
            ranked.append(((-over_hits, under_hits, score, total), slot_name))
        elif under:
            under_hits = len(highs & under)
            if under_hits:
                continue
            ranked.append(((0, score, total), slot_name))
        else:
            deficit_highs = len(highs & deficits)
            deficit_total = sum(item["Resists"].get(name, 0) for name in deficits)
            ranked.append(((deficit_highs, deficit_total, score, total), slot_name))

    if not ranked:
        ranked = [
            ((_suit_candidate_score(active_by_slot[slot_name]), sum(active_by_slot[slot_name]["Resists"].values())), slot_name)
            for slot_name in slot_names
            if active_by_slot.get(slot_name)
        ]

    ranked.sort()
    needed = 1
    if over:
        needed = sum(max(0, counts.get(name, 0) - SUIT_HIGH_BALANCE_MAX) for name in over)
    elif under:
        needed = sum(max(0, SUIT_HIGH_BALANCE_MIN - counts.get(name, 0)) for name in under)
    selected = [slot_name for _, slot_name in ranked[:max(1, min(2, needed, len(ranked)))]]

    if over or under:
        reason = "High balance {}".format(_suit_high_count_text(counts))
    else:
        reason = "Resist/imbue fit"
    return selected, reason


def ScanSuitGoodPieces():
    if state.get("SuitRunning"):
        SuitLog("manual scan ignored: suit crafting already running")
        _suit_set_msg("Stop suit crafting before scanning saved pieces.", 33)
        return

    body = state.get("SuitBody", "Male")
    preset = _suit_current_preset()
    keep_serial = state.get("SuitKeepCont", 0)
    SuitLog("manual scan start: body={} preset={} preset_class={} keep={}".format(
        body,
        preset.key,
        preset.__class__.__name__,
        _debug_hex(keep_serial),
    ))

    try:
        _suit_get_keep_container(required=True)
        _suit_init_rows(body)
        preset.scan_good_pieces(body, required=True, notify=True)
    except Exception as exc:
        SuitLog("manual scan error: {}".format(exc))
        _suit_set_msg(str(exc), 33)



def CraftSuit():
    if state.get("SuitRunning"):
        SuitLog("craft suit ignored: already running")
        _suit_set_msg("Suit crafting already running.", 33)
        return

    body = state.get("SuitBody", "Male")
    preset = _suit_current_preset()
    SuitLog("craft suit start: body={} preset={} preset_class={} keep={} resource={}".format(
        body,
        preset.key,
        preset.__class__.__name__,
        _debug_hex(state.get("SuitKeepCont", 0)),
        _debug_hex(state.get("MatCont", 0)),
    ))

    if preset.placeholder:
        preset.craft(body)
        return

    state["SuitRunning"] = True
    state["SuitStop"] = False
    _suit_init_rows(body)
    try:
        preset.craft(body)
    finally:
        SuitLog("craft suit end: running reset")
        state["SuitRunning"] = False
        send_calculator()


def StopSuitCraft():
    state["SuitStop"] = True
    state["SuitMsg"] = "Stop requested."
    state["Msg"] = "Stop requested."
    send_calculator()


class MysticLlamasCalculator(GumpControlMixin):
    Gump = Gump
    GUMP_ID = 998880
    WEAPON_CATEGORIES = ["One-Handed Melee", "Two-Handed Melee", "Ranged Weapon"]
    TAB_WIDTH = 144
    PAGE_WIDTH = 656
    PANEL_WIDTH = PAGE_WIDTH - 16
    MATERIAL_ROWS_VISIBLE = 3
    WIDTH = TAB_WIDTH
    HEIGHT = 772

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
        self.suitRowControls = []
        self.suitExpectedControls = {}
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
            self._update_suits()
        self._update_picker()
        self._set_status(state.get("Msg", ""))

    def _make_ui_snapshot(self):
        rows = tuple((row.get("Prop"), row.get("Val")) for row in state.get("Rows", []))
        suit_rows = tuple(
            (
                row.get("Slot"),
                row.get("Serial"),
                row.get("Status"),
                row.get("Resists"),
                row.get("Plan"),
            )
            for row in state.get("SuitRows", [])
        )
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
            state.get("SuitBody", "Male"),
            state.get("SuitPreset", SUIT_PRESET_BASIC),
            state.get("SuitKeepCont", 0),
            state.get("SuitMsg", ""),
            state.get("SuitRunning", False),
            state.get("SuitMarkedSerial", 0),
            suit_rows,
            rows,
            materials,
        )





    def _run_action(self, fn):
        try:
            self._sync_inputs()
            state["Msg"] = ""
            fn()
        except Exception as e:
            state["Msg"] = "Error: {}".format(e)
            API.SysMsg(traceback.format_exc(), 33)
        self.updateControls()

















    def _suit_status_display(self, status):
        compact = {
            "Craft failed": "Craft fail",
            "Flat rejected": "Flat reject",
            "Pair rejected": "Pair reject",
            "Keep failed": "Keep fail",
            "Recrafting": "Recraft",
        }
        return self._truncate_text(compact.get(status, status), 12)


    def _suit_row_detail_display(self, row):
        parts = []
        serial = row.get("Serial", 0)
        if serial:
            parts.append("0x{:X}".format(serial))
        plan = str(row.get("Plan", "") or "")
        if plan and plan != "-":
            parts.append(plan)
        return self._truncate_text(" - ".join(parts), 56)


    def _suit_slot_graphic(self, slot_name, index):
        fallback = SUIT_GEAR_FALLBACK_GRAPHICS[index % len(SUIT_GEAR_FALLBACK_GRAPHICS)]
        item_def = SUIT_ITEM_DEFS.get(slot_name, {})
        return item_def.get("graphic") or fallback


    def _add_suit_resist_table(self, x, y, width, height, compact=True):
        ui = self._ui_gump()
        elements = []
        labels = {}
        rows = (
            (
                ("Physical Resist", "Phys", "#d8c6a0"),
                ("Fire Resist", "Fire", "#d35c4c"),
                ("Cold Resist", "Cold", "#63b9d7"),
            ),
            (
                ("Poison Resist", "Pois", "#74c95c"),
                ("Energy Resist", "Ener", "#b07ad8"),
            ),
        )
        if compact:
            cell_h = 20
            cell_gap = 3
            row_gap = 5
            start_y = y + 18
            usable_x = x + 5
            usable_w = width - 10
            font_size = 9
            text_pad = 1
            cell_bg_opacity = 0.55
            line_opacity = 0.46
            row_data = rows
            for row_index, row in enumerate(row_data):
                row_w = usable_w
                cell_w = (row_w - (len(row) - 1) * cell_gap) // len(row)
                row_x = usable_x + (usable_w - (len(row) * cell_w + (len(row) - 1) * cell_gap)) // 2
                row_y = start_y + row_index * (cell_h + row_gap)
                for resist_name, label, color in row:
                    elements.append(ui.addColorBox(row_x, row_y, cell_h, cell_w, Gump.theme["row"], cell_bg_opacity, withTexture=False))
                    elements.append(ui.addColorBox(row_x, row_y + cell_h - 1, 1, cell_w, "#000000", line_opacity, withTexture=False))
                    labels[resist_name] = self._addBoundedLabel(
                        "",
                        row_x + text_pad,
                        row_y,
                        cell_w - text_pad * 2,
                        cell_h,
                        font_size,
                        color,
                        group="suit",
                        align="center",
                    )
                    row_x += cell_w + cell_gap
            return {"elements": elements, "labels": labels}

        cell_h = 23
        cell_gap = 4
        row_gap = 7
        font_size = 10
        start_y = y + 4
        for row_index, row in enumerate(rows):
            cell_w = (width - (len(row) - 1) * cell_gap) // len(row)
            row_w = len(row) * cell_w + (len(row) - 1) * cell_gap
            row_x = x + (width - row_w) // 2
            row_y = start_y + row_index * (cell_h + row_gap)
            for resist_name, label, color in row:
                elements.append(ui.addColorBox(row_x, row_y, cell_h, cell_w, Gump.theme["row"], 0.55, withTexture=False))
                elements.append(ui.addColorBox(row_x, row_y + cell_h - 1, 1, cell_w, "#000000", 0.46, withTexture=False))
                labels[resist_name] = self._addBoundedLabel(
                    "",
                    row_x + 1,
                    row_y,
                    cell_w - 2,
                    cell_h,
                    font_size,
                    color,
                    group="suit",
                    align="center",
                )
                row_x += cell_w + cell_gap
        return {"elements": elements, "labels": labels}


    def _set_suit_resist_table(self, labels, resists, empty=False, expected=False):
        if not labels:
            return
        for resist_name, _, _, display_name in SUIT_RESIST_DISPLAY:
            value = "--" if empty else str(resists.get(resist_name, 0))
            text = "{}: {}".format(display_name, value)
            self._set_text(labels.get(resist_name), text)


    def _add_suit_resist_column_table(self, x, y, width, height):
        ui = self._ui_gump()
        elements = []
        labels = {}
        row_h = 19
        row_gap = 4
        start_y = y + 4
        for index, (resist_name, _, color, display_name) in enumerate(SUIT_RESIST_DISPLAY):
            row_y = start_y + index * (row_h + row_gap)
            elements.append(ui.addColorBox(x, row_y, row_h, width, Gump.theme["row"], 0.55, withTexture=False))
            elements.append(ui.addColorBox(x, row_y + row_h - 1, 1, width, "#000000", 0.46, withTexture=False))
            labels[resist_name] = self._addBoundedLabel(
                "",
                x + 2,
                row_y,
                width - 4,
                row_h,
                9,
                color,
                group="suit",
                align="center",
            )
        return {"elements": elements, "labels": labels}

    def _add_suit_resist_value_group(self, x, y, width, height):
        ui = self._ui_gump()
        elements = []
        labels = {}
        cell_gap = 2
        cell_h = max(18, min(22, height))
        cell_w = max(18, (width - (len(SUIT_RESIST_DISPLAY) - 1) * cell_gap) // len(SUIT_RESIST_DISPLAY))
        row_w = len(SUIT_RESIST_DISPLAY) * cell_w + (len(SUIT_RESIST_DISPLAY) - 1) * cell_gap
        cell_x = x + max(0, (width - row_w) // 2)
        for resist_name, _, color, _ in SUIT_RESIST_DISPLAY:
            elements.append(ui.addColorBox(cell_x, y, cell_h, cell_w, Gump.theme["row"], 0.55, withTexture=False))
            elements.append(ui.addColorBox(cell_x, y + cell_h - 1, 1, cell_w, "#000000", 0.46, withTexture=False))
            labels[resist_name] = self._addBoundedLabel(
                "",
                cell_x,
                y + 1,
                cell_w,
                cell_h - 2,
                9,
                color,
                group="suit",
                align="center",
            )
            cell_x += cell_w + cell_gap
        return {"elements": elements, "labels": labels}

    def _set_suit_resist_value_group(self, labels, resists, empty=False, mode="value"):
        if not labels:
            return
        for resist_name, _, _, _ in SUIT_RESIST_DISPLAY:
            value = int(resists.get(resist_name, 0) or 0)
            if empty:
                text = "--"
            elif mode == "add":
                text = "+{}".format(value)
            else:
                text = str(value)
            self._set_text(labels.get(resist_name), text)

    def _suit_resist_summary_text(self, resists, empty=False):
        if empty:
            return "P-- F-- C-- Po-- E--"
        return "P{} F{} C{} Po{} E{}".format(
            resists.get("Physical Resist", 0),
            resists.get("Fire Resist", 0),
            resists.get("Cold Resist", 0),
            resists.get("Poison Resist", 0),
            resists.get("Energy Resist", 0),
        )

    def _add_suit_expected_outcome_panel(self, x, y, width, height):
        ui = self._ui_gump()
        elements = [
            ui.addColorBox(x - 2, y - 2, height + 4, width + 4, Gump.theme["frameOuter"], 1, withTexture=False),
            ui.addColorBox(x, y, height, width, Gump.theme["bgInset"], 0.98, withTexture=True),
            ui.addColorBox(x + 2, y + 2, 1, width - 4, "#ffffff", 0.12, withTexture=False),
            ui.addColorBox(x + 2, y + height - 2, 1, width - 4, "#000000", 0.56, withTexture=False),
            ui.addColorBox(x + 10, y + 24, 1, width - 20, Gump.theme["grainLine"], 0.28, withTexture=False),
        ]
        title = self._addBoundedLabel("Expected Outcome", x + 8, y + 5, width - 16, 16, 14, Gump.theme["buttonText"], group="suit", align="center")
        table_x = x + 10
        table_w = width - 20
        col_gap = 3
        resist_w = 42
        current_w = 34
        final_w = 42
        delta_w = table_w - resist_w - current_w - final_w - col_gap * 3
        resist_x = table_x
        current_x = resist_x + resist_w + col_gap
        final_x = current_x + current_w + col_gap
        delta_x = final_x + final_w + col_gap
        header_y = y + 30
        self._addBoundedLabel("Resist", resist_x, header_y, resist_w, 12, 12, "#9e9483", group="suit", align="left")
        self._addBoundedLabel("Cur", current_x, header_y, current_w, 12, 12, "#9e9483", group="suit", align="center")
        self._addBoundedLabel("Final", final_x, header_y, final_w, 12, 12, "#9e9483", group="suit", align="center")
        self._addBoundedLabel("+/-", delta_x, header_y, delta_w, 12, 12, "#9e9483", group="suit", align="center")

        resist_labels = {}
        row_h = 19
        row_gap = 1
        first_row_y = y + 46
        for row_index, (resist_name, short_name, color, _) in enumerate(SUIT_RESIST_DISPLAY):
            row_y = first_row_y + row_index * (row_h + row_gap)
            elements.append(ui.addColorBox(table_x - 2, row_y, row_h, table_w + 4, Gump.theme["row"], 0.42, withTexture=False))
            elements.append(ui.addColorBox(table_x - 2, row_y + row_h - 1, 1, table_w + 4, "#000000", 0.32, withTexture=False))
            self._addBoundedLabel(short_name, resist_x, row_y + 1, resist_w, row_h - 2, 13, color, group="suit", align="left")
            resist_labels[resist_name] = {
                "current": self._addBoundedLabel("", current_x, row_y + 1, current_w, row_h - 2, 13, color, group="suit", align="center"),
                "final": self._addBoundedLabel("", final_x, row_y + 1, final_w, row_h - 2, 13, color, group="suit", align="center"),
                "delta": self._addBoundedLabel("", delta_x, row_y + 1, delta_w, row_h - 2, 13, color, group="suit", align="center"),
            }

        stats_y = first_row_y + len(SUIT_RESIST_DISPLAY) * (row_h + row_gap) + 8
        elements.append(ui.addColorBox(x + 10, stats_y - 3, 1, width - 20, Gump.theme["grainLine"], 0.24, withTexture=False))
        self._addBoundedLabel("Planned Stats", x + 10, stats_y + 3, width - 20, 14, 13, "#9e9483", group="suit", align="center")
        prop_labels = []
        for index in range(8):
            row_y = stats_y + 23 + index * 17
            elements.append(ui.addColorBox(table_x - 2, row_y, 16, table_w + 4, Gump.theme["row"], 0.32, withTexture=False))
            prop_labels.append(self._addBoundedLabel("", table_x, row_y + 1, table_w, 14, 13, "#c9bea7", group="suit", align="center"))

        note = self._addBoundedLabel("", x + 10, y + height - 20, width - 20, 14, 12, "#f6f2cf", group="suit", align="center")
        return {"elements": elements, "title": title, "resists": resist_labels, "props": prop_labels, "note": note}

    def _set_suit_expected_outcome(self, controls, rows):
        if not controls:
            return
        current_total = _suit_empty_resists()
        final_total = _suit_empty_resists()
        has_current_total = False
        for row in rows:
            if not row.get("Resists"):
                continue
            has_current_total = True
            current_row = _suit_parse_resist_text(row.get("Resists", ""))
            final_row = _suit_expected_row_resists(row)
            for resist_name in SUIT_RESISTS:
                current_total[resist_name] += current_row.get(resist_name, 0)
                final_total[resist_name] += final_row.get(resist_name, 0)

        for resist_name, _, _, _ in SUIT_RESIST_DISPLAY:
            row_controls = controls.get("resists", {}).get(resist_name, {})
            if has_current_total:
                current_value = current_total.get(resist_name, 0)
                final_value = final_total.get(resist_name, 0)
                delta_value = final_value - current_value
                self._set_text(row_controls.get("current"), current_value)
                self._set_text(row_controls.get("final"), final_value)
                self._set_text(row_controls.get("delta"), "{:+d}".format(delta_value))
            else:
                self._set_text(row_controls.get("current"), "--")
                self._set_text(row_controls.get("final"), "--")
                self._set_text(row_controls.get("delta"), "--")

        prop_totals = _suit_expected_plan_totals(rows)
        prop_order = ["Lower Reagent Cost", "Lower Mana Cost", "Mana Increase", "Mana Regeneration"]
        ordered_props = [prop for prop in prop_order if prop_totals.get(prop)]
        ordered_props.extend(sorted(prop for prop in prop_totals if prop not in ordered_props))
        prop_texts = ["{} {}".format(_suit_prop_short_name(prop), prop_totals[prop]) for prop in ordered_props]
        for index, label in enumerate(controls.get("props", [])):
            self._set_text(label, prop_texts[index] if index < len(prop_texts) else "")
        if has_current_total:
            self._set_text(controls.get("note"), "Outcome from selected pieces")
        else:
            self._set_text(controls.get("note"), "Scan or select suit pieces first")

    def _set_suit_plan_details(self, controls, plan_rows):
        prop_labels = controls.get("props") or []
        extras = _suit_plan_extra_texts(plan_rows)
        for index, label in enumerate(prop_labels):
            self._set_text(label, extras[index] if index < len(extras) else "")
        if controls.get("plan"):
            if extras:
                plan_text = " ".join(extras)
            elif plan_rows:
                plan_text = "Resists only"
            else:
                plan_text = "--"
            self._set_text(controls.get("plan"), self._truncate_text(plan_text, 24))
        if plan_rows:
            self._set_text(
                controls.get("weight"),
                "Wt {}/{}".format(_suit_rows_weight(plan_rows), _suit_max_weight(True)),
            )
        else:
            self._set_text(controls.get("weight"), "Wt --")

    def _set_suit_icon_graphic(self, control, graphic):
        if not control:
            return
        try:
            control.Graphic = graphic
        except Exception:
            pass


    def _suit_card_status(self, status):
        status_text = str(status or "Pending")
        lower = status_text.lower()
        if lower == "done":
            return "Complete", "chosen"
        if "saved" in lower:
            return "Saved", "chosen"
        if "chosen" in lower or "select" in lower or lower.startswith("good "):
            return self._suit_status_display(status_text), "chosen"
        if "fail" in lower or "reject" in lower:
            return "Failed", "failed"
        if "imbu" in lower:
            return "Imbuing", "working"
        if "craft" in lower:
            return "Crafting", "working"
        return self._suit_status_display(status_text), "idle"


    def _add_suit_gear_slot_card(self, x, y, width, height, index):
        ui = self._ui_gump()
        frame = [
            ui.addColorBox(x - 4, y - 4, height + 8, width + 8, Gump.theme["frameOuter"], 1, withTexture=False),
            ui.addColorBox(x - 2, y - 2, height + 4, width + 4, Gump.theme["buttonFrame"], 0.92, withTexture=False),
            ui.addColorBox(x, y, height, width, Gump.theme["bgInset"], 0.98, withTexture=True),
            ui.addColorBox(x + 3, y + 3, 1, width - 6, "#ffffff", 0.12, withTexture=False),
            ui.addColorBox(x + 3, y + height - 4, 1, width - 6, "#000000", 0.56, withTexture=False),
        ]
        table = self._add_suit_resist_value_group(x + 6, y + 34, width - 12, 22)
        icon = None
        selected = [
            ui.addColorBox(x - 5, y - 5, 2, width + 10, "#69be37", 0.94, withTexture=False),
            ui.addColorBox(x - 5, y + height + 3, 2, width + 10, "#69be37", 0.94, withTexture=False),
            ui.addColorBox(x - 5, y - 5, height + 10, 2, "#69be37", 0.94, withTexture=False),
            ui.addColorBox(x + width + 3, y - 5, height + 10, 2, "#69be37", 0.94, withTexture=False),
        ]
        for element in selected:
            element.IsVisible = False
        status_borders = {}
        for key, color in (("chosen", "#69be37"), ("working", "#2da8ff"), ("failed", "#d35c4c")):
            borders = [
                ui.addColorBox(x - 3, y - 3, 2, width + 6, color, 0.95, withTexture=False),
                ui.addColorBox(x - 3, y + height + 1, 2, width + 6, color, 0.95, withTexture=False),
                ui.addColorBox(x - 3, y - 3, height + 6, 2, color, 0.95, withTexture=False),
                ui.addColorBox(x + width + 1, y - 3, height + 6, 2, color, 0.95, withTexture=False),
            ]
            for border in borders:
                border.IsVisible = False
            status_borders[key] = borders
        detail_y = y + height - 48
        detail_w = (width - 18) // 2
        props = [
            self._addBoundedLabel("", x + 7, detail_y, detail_w, 10, 8, "#c9bea7", group="suit", align="left"),
            self._addBoundedLabel("", x + 11 + detail_w, detail_y, detail_w, 10, 8, "#c9bea7", group="suit", align="left"),
            self._addBoundedLabel("", x + 7, detail_y + 11, detail_w, 10, 8, "#c9bea7", group="suit", align="left"),
            self._addBoundedLabel("", x + 11 + detail_w, detail_y + 11, detail_w, 10, 8, "#c9bea7", group="suit", align="left"),
        ]
        weight = self._addBoundedLabel("", x + 8, detail_y + 24, width - 16, 10, 8, "#f0d080", group="suit", align="center")
        status = self._addBoundedLabel("", x + 8, y + height - 13, width - 16, 12, 8, "#f6f2cf", group="suit", align="center")
        name = self._addBoundedLabel("", x - 10, y - 18, width + 20, 14, 8, Gump.theme["buttonText"], group="suit", align="center")
        selector = self._addNativeCircleButton("radioBlue", x + 2, y + 2, lambda idx=index: self._mark_suit_slot(idx), group=None)
        return {
            "row": frame,
            "table": table,
            "icon": icon,
            "name": name,
            "props": props,
            "statusBorders": status_borders,
            "selected": selected,
            "select": selector,
            "status": status,
            "weight": weight,
        }

    def _add_suit_gear_slot_table(self, x, y, width, height, index):
        ui = self._ui_gump()
        frame = [
            ui.addColorBox(x - 2, y - 2, height + 4, width + 4, Gump.theme["frameOuter"], 1, withTexture=False),
            ui.addColorBox(x, y, height, width, Gump.theme["bgInset"], 0.98, withTexture=True),
            ui.addColorBox(x + 2, y + 2, 1, width - 4, "#ffffff", 0.12, withTexture=False),
            ui.addColorBox(x + 2, y + height - 2, 1, width - 4, "#000000", 0.56, withTexture=False),
        ]
        selected = [
            ui.addColorBox(x - 3, y - 3, 2, width + 6, "#69be37", 0.94, withTexture=False),
            ui.addColorBox(x - 3, y + height + 1, 2, width + 6, "#69be37", 0.94, withTexture=False),
            ui.addColorBox(x - 3, y - 3, height + 6, 2, "#69be37", 0.94, withTexture=False),
            ui.addColorBox(x + width + 1, y - 3, height + 6, 2, "#69be37", 0.94, withTexture=False),
        ]
        for element in selected:
            element.IsVisible = False

        status_borders = {}
        for key, color in (("chosen", "#69be37"), ("working", "#2da8ff"), ("failed", "#d35c4c")):
            borders = [
                ui.addColorBox(x - 2, y - 2, 2, width + 4, color, 0.95, withTexture=False),
                ui.addColorBox(x - 2, y + height, 2, width + 4, color, 0.95, withTexture=False),
                ui.addColorBox(x - 2, y - 2, height + 4, 2, color, 0.95, withTexture=False),
                ui.addColorBox(x + width, y - 2, height + 4, 2, color, 0.95, withTexture=False),
            ]
            for border in borders:
                border.IsVisible = False
            status_borders[key] = borders

        piece_w = 144
        plan_w = 130
        group_gap = 6
        group_w = max(100, (width - piece_w - plan_w - group_gap * 4) // 3)
        current_x = x + piece_w + group_gap
        add_x = current_x + group_w + group_gap
        final_x = add_x + group_w + group_gap
        plan_x = final_x + group_w + group_gap
        value_y = y + max(10, (height - 22) // 2)

        selector = self._addNativeCircleButton(
            "radioBlue",
            x + 6,
            y + height // 2 - 9,
            lambda idx=index: self._mark_suit_slot(idx),
            group=None,
        )
        name = self._addBoundedLabel("", x + 30, y + 4, piece_w - 34, 13, 9, Gump.theme["buttonText"], group="suit")
        status = self._addBoundedLabel("", x + 30, y + 19, piece_w - 34, 12, 8, "#f6f2cf", group="suit")
        serial = self._addBoundedLabel("", x + 30, y + 32, piece_w - 34, 10, 8, "#9e9483", group="suit")
        current = self._add_suit_resist_value_group(current_x, value_y, group_w, 22)
        added = self._add_suit_resist_value_group(add_x, value_y, group_w, 22)
        final = self._add_suit_resist_value_group(final_x, value_y, group_w, 22)
        plan = self._addBoundedLabel("", plan_x, y + 8, plan_w, 14, 8, "#c9bea7", group="suit")
        weight = self._addBoundedLabel("", plan_x, y + 25, plan_w, 13, 8, "#f0d080", group="suit")

        return {
            "row": frame,
            "current": current,
            "add": added,
            "final": final,
            "name": name,
            "serial": serial,
            "plan": plan,
            "statusBorders": status_borders,
            "selected": selected,
            "select": selector,
            "status": status,
            "weight": weight,
        }


    def _add_suit_gear_slot(self, x, y, width, height, index):
        ui = self._ui_gump()
        frame = [
            ui.addColorBox(x - 2, y - 2, height + 4, width + 4, Gump.theme["frameOuter"], 1, withTexture=False),
            ui.addColorBox(x, y, height, width, Gump.theme["bgInset"], 0.98, withTexture=True),
            ui.addColorBox(x + 2, y + 2, 1, width - 4, "#ffffff", 0.12, withTexture=False),
            ui.addColorBox(x + 2, y + height - 2, 1, width - 4, "#000000", 0.56, withTexture=False),
            ui.addColorBox(x + 10, y + 23, 1, width - 20, Gump.theme["grainLine"], 0.26, withTexture=False),
            ui.addColorBox(x + 10, y + height - 21, 1, width - 20, Gump.theme["grainLine"], 0.22, withTexture=False),
        ]

        status_borders = {}
        for key, color in (("chosen", "#69be37"), ("working", "#2da8ff"), ("failed", "#d35c4c")):
            borders = [
                ui.addColorBox(x - 2, y - 2, 2, width + 4, color, 0.95, withTexture=False),
                ui.addColorBox(x - 2, y + height, 2, width + 4, color, 0.95, withTexture=False),
                ui.addColorBox(x - 2, y - 2, height + 4, 2, color, 0.95, withTexture=False),
                ui.addColorBox(x + width, y - 2, height + 4, 2, color, 0.95, withTexture=False),
            ]
            for border in borders:
                border.IsVisible = False
            status_borders[key] = borders

        table_w = width - 20
        table_x = x + (width - table_w) // 2
        col_gap = 2
        resist_w = 30
        current_w = 34
        add_w = 42
        final_w = table_w - resist_w - current_w - add_w - col_gap * 3
        resist_x = table_x
        current_x = resist_x + resist_w + col_gap
        add_x = current_x + current_w + col_gap
        final_x = add_x + add_w + col_gap

        name = self._addBoundedLabel("", x + 8, y + 4, width - 16, 16, 14, Gump.theme["buttonText"], group="suit", align="center")
        header_y = y + 23
        self._addBoundedLabel("R", resist_x, header_y, resist_w, 12, 12, "#9e9483", group="suit", align="center")
        self._addBoundedLabel("Cur", current_x, header_y, current_w, 12, 12, "#9e9483", group="suit", align="center")
        self._addBoundedLabel("Add", add_x, header_y, add_w, 12, 12, "#9e9483", group="suit", align="center")
        self._addBoundedLabel("Final", final_x, header_y, final_w, 12, 12, "#9e9483", group="suit", align="center")

        current_labels = {}
        add_labels = {}
        final_labels = {}
        row_h = 13
        row_gap = 0
        first_row_y = y + 36
        for row_index, (resist_name, short_name, color, _) in enumerate(SUIT_RESIST_DISPLAY):
            row_y = first_row_y + row_index * (row_h + row_gap)
            frame.append(ui.addColorBox(table_x - 2, row_y, row_h, table_w + 4, Gump.theme["row"], 0.42, withTexture=False))
            frame.append(ui.addColorBox(table_x - 2, row_y + row_h - 1, 1, table_w + 4, "#000000", 0.32, withTexture=False))
            self._addBoundedLabel(short_name, resist_x, row_y, resist_w, row_h, 13, color, group="suit", align="center")
            current_labels[resist_name] = self._addBoundedLabel("", current_x, row_y, current_w, row_h, 13, color, group="suit", align="center")
            add_labels[resist_name] = self._addBoundedLabel("", add_x, row_y, add_w, row_h, 13, color, group="suit", align="center")
            final_labels[resist_name] = self._addBoundedLabel("", final_x, row_y, final_w, row_h, 13, color, group="suit", align="center")

        plan = self._addBoundedLabel("", x + 10, y + height - 19, width - 20, 10, 12, "#c9bea7", group="suit", align="center")
        weight = self._addBoundedLabel("", x + 10, y + height - 9, (width - 24) // 2, 9, 12, "#f0d080", group="suit", align="center")
        status = self._addBoundedLabel("", x + width // 2, y + height - 9, (width - 24) // 2, 9, 12, "#f6f2cf", group="suit", align="center")

        hit_target = API.CreateGumpColorBox(0.01, "#000000")
        hit_target.SetX(x)
        hit_target.SetY(y)
        hit_target.SetWidth(width)
        hit_target.SetHeight(height)
        API.AddControlOnClick(hit_target, self._callback(lambda idx=index: self._mark_suit_slot(idx)))
        ui.gump.Add(hit_target)

        return {
            "row": frame,
            "current": {"labels": current_labels},
            "add": {"labels": add_labels},
            "final": {"labels": final_labels},
            "name": name,
            "serial": None,
            "plan": plan,
            "statusBorders": status_borders,
            "selected": [],
            "select": hit_target,
            "status": status,
            "weight": weight,
        }


    def _mark_suit_slot(self, index):
        rows = state.get("SuitRows", [])
        if index >= len(rows):
            _suit_set_msg("No suit piece in that slot yet.", 33)
            return
        row = rows[index]
        serial = int(row.get("Serial", 0) or 0)
        if not serial:
            _suit_set_msg("That suit slot has no item to mark yet.", 33)
            return

        previous = int(state.get("SuitMarkedSerial", 0) or 0)
        if previous and previous != serial:
            previous_item = API.FindItem(previous)
            if previous_item:
                try:
                    previous_item.SetOutlineColor(None)
                except Exception:
                    pass

        item = API.FindItem(serial)
        if not item:
            _suit_set_msg("Could not find suit piece 0x{:X}.".format(serial), 33)
            return
        try:
            item.SetOutlineColor("#69be37")
        except Exception:
            pass
        _suit_set_selected_item_hue(
            {
                "Slot": row.get("Slot", "Suit Piece"),
                "Serial": serial,
                "Resists": _suit_parse_resist_text(row.get("Resists", "")),
                "Rows": [],
            },
            "manual-mark",
        )
        try:
            API.HeadMsg("Selected", serial, 87)
        except Exception:
            pass
        state["SuitMarkedSerial"] = serial
        _suit_set_msg("Marked suit piece 0x{:X}.".format(serial), 87)



    def _set_button_text(self, control, text):
        if control:
            self._set_text(control.get("label"), text)






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




    def _recalculate_materials(self):
        state["MaterialScroll"] = 0
        state["Msg"] = "Material costs recalculated."


    def _set_suit_body(self, body):
        state["SuitBody"] = body
        _suit_init_rows(body)


    def _set_suit_preset(self, preset):
        state["SuitPreset"] = _suit_preset_for_key(preset).key


    def _update_speed_calc(self):
        self._set_button_text(self.controls["weaponButton"], state.get("CalcWeaponName", "Select Weapon"))
        self._set_input_text(self.staminaInput, state.get("StaminaInput", "") or "0")
        self._set_input_text(self.ssiInput, state.get("SSIInput", "") or "0")
        self._set_text(self.controls["ticksLabel"], state["CalcTicks"])
        self._set_text(self.controls["speedLabel"], state["CalcSpeed"])


    def _update_suits(self):
        self._set_checked(self.controls.get("suitBodyMale"), state.get("SuitBody") == "Male")
        self._set_checked(self.controls.get("suitBodyFemale"), state.get("SuitBody") == "Female")
        self._set_checked(self.controls.get("suitBodyGargoyle"), state.get("SuitBody") == "Gargoyle")
        selected_preset = _suit_current_preset().key
        for preset in SUIT_PRESETS:
            self._set_checked(self.controls.get(preset.control_key), selected_preset == preset.key)
        self._set_button_text(
            self.controls.get("suitMatButton"),
            self._container_text("Resource", state.get("MatCont", 0)),
        )
        self._set_button_text(
            self.controls.get("suitKeepButton"),
            self._container_text("Good pieces", state.get("SuitKeepCont", 0)),
        )
        self._set_text(self.controls.get("suitStatusLabel"), self._truncate_text(state.get("SuitMsg", ""), 82))

        rows = state.get("SuitRows", [])
        if not rows:
            body = state.get("SuitBody", "Male")
            rows = [
                {"Slot": slot, "Serial": 0, "Status": "Pending", "Resists": "", "Plan": ""}
                for slot in SUIT_BODY_ITEMS.get(body, ())
            ]
        for index, controls in enumerate(self.suitRowControls):
            has_row = index < len(rows)
            for key in ("row", "current", "add", "final", "name", "serial", "plan", "select", "status", "weight"):
                self._set_visible(controls.get(key), has_row)
            for borders in controls.get("statusBorders", {}).values():
                self._set_visible(borders, False)
            if not has_row:
                self._set_visible(controls.get("selected"), False)
                continue
            row = rows[index]
            serial = int(row.get("Serial", 0) or 0)
            resists_text = row.get("Resists", "")
            plan_text = row.get("Plan", "")
            plan_rows = _suit_parse_plan_rows(plan_text)
            current_resists = _suit_parse_resist_text(resists_text)
            additions = _suit_plan_resist_additions(plan_text)
            final_resists = _suit_expected_row_resists(row) if resists_text else _suit_empty_resists()
            has_plan = bool(plan_rows) or _suit_plan_has_final_expectation(plan_text)
            self._set_suit_resist_value_group(
                controls.get("current", {}).get("labels"),
                current_resists,
                empty=not bool(resists_text),
            )
            self._set_suit_resist_value_group(
                controls.get("add", {}).get("labels"),
                additions,
                empty=not has_plan,
                mode="add",
            )
            self._set_suit_resist_value_group(
                controls.get("final", {}).get("labels"),
                final_resists,
                empty=not bool(resists_text),
            )
            self._set_suit_plan_details(controls, plan_rows)
            self._set_text(controls.get("name"), self._truncate_text(row.get("Slot", ""), 20))
            self._set_text(controls.get("serial"), "0x{:X}".format(serial) if serial else "No item")
            status_text, status_key = self._suit_card_status(row.get("Status", ""))
            is_marked = bool(serial and serial == state.get("SuitMarkedSerial", 0))
            if is_marked and status_key not in ("working", "failed"):
                status_text, status_key = "Marked", "chosen"
            self._set_visible(controls.get("selected"), bool(serial and status_key == "chosen"))
            self._set_text(controls["status"], status_text)
            self._set_visible(controls.get("statusBorders", {}).get(status_key), True)

        self._set_suit_expected_outcome(self.suitExpectedControls, rows)


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
            if key == "SuitKeepCont" and not state.get("SuitRunning"):
                body = state.get("SuitBody", "Male")
                preset = _suit_current_preset()
                SuitLog("ui scan trigger: selected good-piece container={} body={} preset={} preset_class={}".format(
                    _debug_hex(target),
                    body,
                    preset.key,
                    preset.__class__.__name__,
                ))
                _suit_init_rows(body)
                preset.scan_good_pieces(body, required=False, notify=False)
                send_calculator()
        else:
            state["Msg"] = "Targeting canceled."

    def _container_text(self, label, serial):
        if label == "Mats":
            return "Selected material container (0x{:X})".format(serial) if serial else "Select material container"
        if label == "Gems":
            return "Selected gem container (0x{:X})".format(serial) if serial else "Select gem container"
        if label == "Resource":
            return "Resource container (0x{:X})".format(serial) if serial else "Select resource container"
        if label == "Good pieces":
            return "Good pieces container (0x{:X})".format(serial) if serial else "Select good-piece container"
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













    def _draw_item_properties(self, g):
        panel = self._addSectionPanel(1, "Select Item", 8, 44, self.PANEL_WIDTH, 124)
        x = panel["x"] + 10
        y = panel["y"] + 22
        row_w = panel["width"] - 20
        for row_y in (y - 2, y + 25, y + 47, y + 69):
            self._addFlatRow(x - 6, row_y, row_w, 21, "main")
        self._addSettingAction("Select item", x + 4, y, AutoReadItem, group="main")
        self.controls["targetLabel"] = self._addLabel("", x + 170, y + 3, Gump.hues["muted"])

        type_y = y + 27
        value_x = x + 100
        check_x = x + 292
        self._addLabel("Category", x, type_y, Gump.hues["muted"])
        self.controls["categoryLabel"] = self._addLabel("", value_x, type_y, Gump.hues["text"])
        self._addLabel("Group", x, type_y + 22, Gump.hues["muted"])
        self.controls["groupLabel"] = self._addLabel("", value_x, type_y + 22, Gump.hues["text"])
        self._addLabel("Base Item", x, type_y + 44, Gump.hues["muted"])
        self.controls["itemLabel"] = self._addLabel("", value_x, type_y + 44, Gump.hues["text"])
        self.controls["customCheck"] = self._addReadOnlyRadio("Custom", check_x, type_y, state.get("CustomMode", False), Gump.hues["muted"])
        self.controls["exceptionalCheck"] = self._addReadOnlyRadio("Exceptional", check_x, type_y + 22, state.get("Exceptional", False), Gump.hues["muted"])
        self.controls["whetstoneCheck"] = self._addReadOnlyRadio("Whetstone", check_x, type_y + 44, state.get("Whetstone", False), Gump.hues["muted"])

    def _draw_settings(self, g):
        panel = self._addSectionPanel(2, "Settings", 8, 172, self.PANEL_WIDTH, 110)
        x = panel["x"] + 10
        y = panel["y"] + 22
        row_w = panel["width"] - 20
        for row_y in (y - 2, y + 26, y + 52):
            self._addFlatRow(x - 6, row_y, row_w, 21, "main")
        self._addLabel("Reserve", x, y + 3, Gump.hues["muted"])
        self.bufferInput = self._addInput(str(state.get("GemBuffer", "0") or "0"), x + 88, y - 1, 0, 999, width=72, height=24)
        self.controls["matButton"] = self._addSettingAction("Select material container", x + 4, y + 29, lambda: self._target_container("MatCont", "Select Material Container"), group="main")
        self.controls["gemButton"] = self._addSettingAction("Select gem container", x + 4, y + 55, lambda: self._target_container("GemCont", "Select Gem Container"), group="main")




    def _draw_speed_calc(self, g):
        panel = self._addSectionPanel(1, "Swing Speed", 8, 44, self.PANEL_WIDTH, 178, group="speed")
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

    def _draw_suits(self, g):
        col_w = (self.PANEL_WIDTH - 6) // 2
        gender = self._addSectionPanel(1, "Gender", 8, 44, col_w, 150, group="suit")
        presets = self._addSectionPanel(2, "Presets", 14 + col_w, 44, col_w, 150, group="suit")

        gx = gender["x"] + 10
        gy = gender["y"] + 36
        grow_w = gender["width"] - 20
        for row_y in (gy - 2, gy + 24, gy + 50):
            self._addFlatRow(gx - 6, row_y, grow_w, 22, "suit")
        self.controls["suitBodyMale"] = self._addRadio("Male", gx + 4, gy, state.get("SuitBody") == "Male", lambda: self._set_suit_body("Male"), group="suit")
        self.controls["suitBodyFemale"] = self._addRadio("Female", gx + 4, gy + 26, state.get("SuitBody") == "Female", lambda: self._set_suit_body("Female"), group="suit")
        self.controls["suitBodyGargoyle"] = self._addRadio("Gargoyle", gx + 4, gy + 52, state.get("SuitBody") == "Gargoyle", lambda: self._set_suit_body("Gargoyle"), group="suit")

        px = presets["x"] + 10
        py = presets["y"] + 36
        prow_w = presets["width"] - 20
        for index, preset in enumerate(SUIT_PRESETS):
            row_y = py - 2 + index * 24
            self._addFlatRow(px - 6, row_y, prow_w, 22, "suit")
            self.controls[preset.control_key] = self._addRadio(
                preset.label,
                px + 4,
                py + index * 24,
                state.get("SuitPreset") == preset.key,
                lambda preset_key=preset.key: self._set_suit_preset(preset_key),
                group="suit",
            )

        settings = self._addSectionPanel(3, "Settings", 8, 202, self.PANEL_WIDTH, 74, group="suit")
        settings_x = settings["x"] + 10
        settings_y = settings["y"] + 18
        settings_w = settings["width"] - 20
        self.controls["suitMatButton"] = self._addSettingAction(
            "Select resource container",
            settings_x,
            settings_y,
            lambda: self._target_container("MatCont", "Select Resource Container"),
            group="suit",
            width=settings_w,
        )
        self.controls["suitKeepButton"] = self._addSettingAction(
            "Select good-piece container",
            settings_x,
            settings_y + 24,
            lambda: self._target_container("SuitKeepCont", "Select Good Piece Container"),
            group="suit",
            width=settings_w,
        )

        gear = self._addSectionPanel(4, "Pieces", 8, 284, self.PANEL_WIDTH, 420, group="suit")
        gear_x = gear["x"]
        gear_y = gear["y"] + 30
        gear_w = gear["width"]
        content_x = gear_x + 8
        content_w = gear_w - 16
        expected_w = 216
        expected_gap = 10
        card_gap = 8
        card_h = 126
        card_w = (content_w - expected_w - expected_gap - card_gap) // 2
        expected_x = content_x + card_w * 2 + card_gap + expected_gap
        row_gap = 6
        self.suitRowControls = []

        max_slots = max(len(items) for items in SUIT_BODY_ITEMS.values())
        for index in range(max_slots):
            slot_x = content_x + (index % 2) * (card_w + card_gap)
            slot_y = gear_y + (index // 2) * (card_h + row_gap)
            self.suitRowControls.append(self._add_suit_gear_slot(slot_x, slot_y, card_w, card_h, index))

        outcome_h = max_slots // 2 * card_h + (max_slots // 2 - 1) * row_gap
        self.suitExpectedControls = self._add_suit_expected_outcome_panel(expected_x, gear_y, expected_w, outcome_h)

        ax = 16 + (self.PANEL_WIDTH - 32 - 304) // 2
        ay = 730
        self._addFlatRow(ax - 8, ay - 6, 304, 34, "suit")
        self._addButton("Scan", ax, ay, 70, height=24, callback=ScanSuitGoodPieces, group="suit")
        self._addButton("Start", ax + 82, ay, 116, height=24, callback=CraftSuit, group="suit")
        self._addButton("Stop", ax + 216, ay, 74, height=24, callback=StopSuitCraft, group="suit")
        self.controls["suitStatusLabel"] = self._addBoundedLabel("", 16, 704, self.PANEL_WIDTH - 32, 20, 10, "#f6f2cf", group="suit")

    def _draw_picker(self, g):
        self.pickerSlots = []
        panel = self._addSectionPanel("", "Select", 8, 44, self.PANEL_WIDTH, 548, group="picker")
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

        imbueGump = g.addTabButton("Imbuing", "caster", self.PAGE_WIDTH, yOffset=52, withStatus=False, tabStyle="list")
        self._drawGump = imbueGump
        imbueGump.addTitle("MYSTIC LLAMAS IMBUING", hue=Gump.hues["text"])
        self._draw_item_properties(imbueGump)
        self._draw_settings(imbueGump)
        self._draw_rows(imbueGump)
        self._draw_material_costs(imbueGump)

        speedGump = g.addTabButton("Swing Speed", "bard", self.PAGE_WIDTH, yOffset=52, withStatus=False, tabStyle="list")
        self._drawGump = speedGump
        speedGump.addTitle("SWING SPEED INCREASE", hue=Gump.hues["text"])
        self._draw_speed_calc(speedGump)

        suitGump = g.addTabButton("Suits", "caster", self.PAGE_WIDTH, yOffset=52, withStatus=False, label="Suit Builder", tabStyle="list")
        self._drawGump = suitGump
        suitGump.addTitle("SUIT CRAFTING", hue=Gump.hues["text"])
        self._draw_suits(suitGump)

        pickerGump = g.createSubGump(self.PAGE_WIDTH, self.HEIGHT, "right", withStatus=False, alwaysVisible=False)
        pickerGump.gump.IsVisible = False
        g.tabGumps["Picker"] = pickerGump
        self._drawGump = pickerGump
        self._draw_picker(pickerGump)
        self._drawGump = None

        g.setActiveTab("Imbuing")
        self._set_status(state.get("Msg", ""))
        g.create()
        self._position_gumps_side_by_side()

    def _position_gumps_side_by_side(self):
        if not self.gump:
            return
        try:
            main = self.gump.gump
            x = max(12, int(main.GetX()))
            y = max(36, int(main.GetY()))
            main.SetX(x)
            main.SetY(y)
            for sub_gump, position, _ in getattr(self.gump, "subGumps", []):
                if position == "right":
                    sub_gump.gump.SetX(x + self.WIDTH)
                    sub_gump.gump.SetY(y)
            self.gump.tickSubGumps()
        except Exception:
            pass




    def _draw_rows(self, g):
        panel = self._addSectionPanel(3, "Properties", 8, 286, self.PANEL_WIDTH, 206)
        x = panel["x"] + 10
        y = panel["y"] + 20
        row_w = panel["width"] - 20
        self._addLabel("Property", x + 88, y, Gump.hues["muted"])
        self._addLabel("Val", x + 236, y, Gump.hues["muted"])
        self._addLabel("Weight", x + 312, y, Gump.hues["muted"])
        self._addButton("Calc", x + row_w - 40, y - 2, 36, height=20, callback=self._recalculate_materials, fontSize=9, group="main")
        for i, row in enumerate(state["Rows"]):
            row_y = y + 22 + i * 21
            row_control = {
                "row": self._addFlatRow(x - 6, row_y - 1, row_w, 20, "main"),
                "select": self._addButton("", x + 8, row_y - 1, 204, height=20, callback=lambda idx=i: self._open_property_picker(idx), fontSize=9, group=None),
                "locked": self._addLabel("", x + 12, row_y, Gump.hues["muted"], group=None),
                "input": self._addInput(str(row["Val"]), x + 230, row_y - 1, 0, 999, width=50, height=20, group=None),
                "max": self._addMaxButton(x + 292, row_y - 1, lambda idx=i: self._max_row(idx), group=None),
                "weight": self._addLabel("", x + 360, row_y, Gump.hues["text"], group=None),
            }
            self.rowControls.append(row_control)
        total_y = y + 126
        self._addLabel("Total Weight", x + 226, total_y + 3, Gump.hues["muted"])
        self.controls["totalWeightLabel"] = self._addLabel("", x + 334, total_y + 3, Gump.hues["text"])

        preset_y = total_y + 24
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
            x + 155,
            preset_y,
            selected_preset == "Basic LRC",
            lambda: self._apply_preset("Basic LRC"),
            group="main",
        )
    def _draw_material_costs(self, g):
        panel = self._addSectionPanel(4, "Materials Cost", 8, 496, self.PANEL_WIDTH, 116)
        x = panel["x"] + 10
        y = panel["y"] + 18
        scroll_y = y + 18
        scroll_width = panel["width"] - 20
        scroll_height = 34
        self.materialTableWidth = scroll_width - 18
        self.materialQtyX = self.materialTableWidth - 86
        self._addLabel("Material", x + 20, y, Gump.hues["muted"])
        self._addLabel("Qty", x + self.materialQtyX, y, Gump.hues["muted"])
        self.controls["noMaterialsLabel"] = self._addLabel("", x, y + 22, Gump.hues["muted"], group=None)
        self.materialScrollArea = self._ui_gump().addScrollArea(x - 4, scroll_y, scroll_width, scroll_height)
        self._remember(self.materialScrollArea, "main")
        count_y = y
        self.controls["moreMaterialsIcon"] = self._addNativeCircleButton("radioBlue", x + 142, count_y - 2, None, group="main")
        self.controls["moreMaterialsLabel"] = self._addLabel("", x + 170, count_y, Gump.hues["muted"], group="main")
        self.controls["startImbuingButton"] = self._addButton(
            "Start Imbuing",
            x - 4,
            panel["y"] + panel["height"] - 28,
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
            ui = self._ui_gump()
            for index, (name, amount) in enumerate(items):
                row_y = index * 16
                ui.addColorBox(0, row_y, 15, self.materialTableWidth, Gump.theme["row"], 0.42, container=self.materialScrollArea)
                ui.addColorBox(0, row_y + 15, 1, self.materialTableWidth, "#000000", 0.32, container=self.materialScrollArea)
                graphic_data = INGREDIENT_GRAPHICS.get(name)
                if graphic_data:
                    try:
                        ui.addItemPic(graphic_data[0], 2, row_y - 1, 16, 16, container=self.materialScrollArea)
                    except Exception:
                        pass
                ui.addLabel(name, 26, row_y, Gump.hues["text"], container=self.materialScrollArea)
                ui.addLabel(str(amount), self.materialQtyX, row_y, Gump.hues["text"], container=self.materialScrollArea)
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
