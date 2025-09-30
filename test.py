import API
from LegionPath import LegionPath
import importlib

LegionPath.addSubdirs()


runebookItem = API.FindItem(0x43E95D7B)
while not API.HasGump(498):
    API.UseObject(0x43E95D7B)
    API.WaitForGump(498)

gump = API.GetGump(498)
values = gump.PacketGumpText.split("\n")
for value in values:
    API.SysMsg(value)