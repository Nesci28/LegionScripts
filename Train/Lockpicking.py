try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass
# API is injected by TazUO at runtime; the import above is IDE-only.

lockpicks = API.FindType(0x14FB)
chests1 = API.FindTypeAll(0x09A8, 4294967295, 2)
chests2 = API.FindTypeAll(0x0E80, 4294967295, 2)
chests = chests1 + chests2
for chest in chests:
    API.ClearJournal()
    isUnlocked = API.InJournal("The lock quickly yields to your skill.") or API.InJournal("This does not appear to be locked.")
    while not isUnlocked:
        API.UseObject(lockpicks.Serial)
        API.WaitForTarget()
        API.Target(chest.Serial)
        API.Pause(1)
        isUnlocked = API.InJournal("The lock quickly yields to your skill.") or API.InJournal("This does not appear to be locked.")