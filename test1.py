import API
from LegionPath import LegionPath
import importlib

LegionPath.addSubdirs()


def f1_combo():
    API.SysMsg("CTRL+SHIFT+F1 pressed!")

def alt_a():
    print("ALT+A Python callback firing!")   # debug to stdout
    API.SysMsg("ALT+A pressed! 1")
API.Pause(1)
API.SysMsg("Register")
API.OnHotKey("CTRL+SHIFT+F1", f1_combo)  # auto-normalized
API.OnHotKey("SHIFT+A", alt_a)

while True:
    API.ProcessCallbacks()
    API.Pause(0.1)