import API

savedGears = {}
layers = [
    "OneHanded",
    "TwoHanded",
    "Shoes",
    "Pants",
    "Shirt",
    "Helmet",
    "Gloves",
    "Ring",
    "Talisman",
    "Necklace",
    "Hair",
    "Waist",
    "Torso",
    "Bracelet",
    "Face",
    "Beard",
    "Tunic",
    "Earrings",
    "Arms",
    "Cloak",
    "Robe",
    "Skirt",
    "Legs"
]

def save_equipped_items():
    savedGears.clear()
    for layer in layers:
        item = API.FindLayer(layer)
        if item:
            savedGears[layer] = item.Serial
    API.SysMsg("Equipped items saved.", 48)


def equip_all_from_backpack():
    items = Util.Util.itemsInContainer(API.Backpack)
    for savedGear in savedGears:
        for item in items:
            if item.Serial == savedGears[savedGear]:
                API.EquipItem(item)
                API.Pause(1)


save_equipped_items()

while API.Player.Hits > 0:
    if API.InJournal("Dress Agent Activated"):
        API.ClearJournal()
        equip_all_from_backpack()
    API.Pause(0.1)
