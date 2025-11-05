#=========== Consolidated Imports ============#
import API
import importlib
import os
import re
import sys


#=========== Start of LegionPath.py ============#

class LegionPath:
    @staticmethod
    def createPath(path):
        path = f"{LegionPath.getLegionPath()}/{path}"
        return path

    @staticmethod
    def getLegionPath():
        base = sys.prefix
        if base.lower().endswith("ironpython.dll"):
            base = os.path.dirname(base)

        legion_path = os.path.join(base, "LegionScripts")
        return legion_path

    @staticmethod
    def addSubdirs():
        legion_path = LegionPath.getLegionPath()

        if not os.path.isdir(legion_path):
            return

        for name in os.listdir(legion_path):
            subdir = os.path.join(legion_path, name)
            if os.path.isdir(subdir) and name.startswith("_"):
                if subdir not in sys.path:
                    sys.path.append(subdir)
#=========== End of LegionPath.py ============#

#=========== Start of _Utils\Math.py ============#

class Math:
    centerX = 1323
    mapWidth = 5120
    centerY = 1624
    mapHeight = 4096
    
    @staticmethod
    def truncateDecimal(n1, d=1):
        n = str(n1)
        return n if "." not in n else n[: n.find(".") + d + 1]
    
    @staticmethod
    def distanceBetween(m1, m2):
        if not m1 or not m2:
            return 999
        return max(abs(m1.X - m2.X), abs(m1.Y - m2.Y))

    @staticmethod
    def convertToHex(obj):
        if isinstance(obj, dict):
            return {k: Math.convertToHex(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Math.convertToHex(elem) for elem in obj]
        elif isinstance(obj, str) and re.fullmatch(r"0x[0-9a-fA-F]+", obj):
            return int(obj, 16)
        return obj
    
    @staticmethod
    def tilesToLatLon(x, y):
        degLon = (x - Math.centerX) * 360.0 / Math.mapWidth
        degLat = (y - Math.centerY) * 360.0 / Math.mapHeight

        if degLon > 180:
            degLon = 360 - degLon
            lonDir = "W"
        else:
            lonDir = "E"

        if degLat > 180:
            degLat = 360 - degLat
            latDir = "N"
        else:
            latDir = "S"

        lat = (int(degLat), (degLat - int(degLat)) * 60, latDir)
        lon = (int(degLon), (degLon - int(degLon)) * 60, lonDir)
        return lat, lon

    @staticmethod
    def latLonToTiles(degLat, minLat, latDir, degLon, minLon, lonDir):
        totalLat = degLat + minLat / 60
        if latDir == "N":
            totalLat = 360 - totalLat

        totalLon = degLon + minLon / 60
        if lonDir == "W":
            totalLon = 360 - totalLon

        y = totalLat * Math.mapHeight / 360 + Math.centerY
        x = totalLon * Math.mapWidth / 360 + Math.centerX
        return int(x % Math.mapWidth), int(y % Math.mapHeight)
#=========== End of _Utils\Math.py ============#

#=========== Start of .\Pet\tame.py ============#




class TamingScript:
    tamingDelay = 10
    checkInterval = 0.5
    maxTamingAttempts = 10

    def __init__(self):
        self.petSerial = None

    def isAngry(self):
        return API.InJournalAny(["You seem to anger the beast!"])

    def isTooFar(self):
        return API.InJournalAny(["It's too far away."])

    def waitForPetInRange(self, maxRange=3):
        while not API.HasTarget():
            pet = API.FindMobile(self.petSerial)
            distance = Math.Math.distanceBetween(API.Player, pet)
            API.SysMsg(str(distance))
            if distance <= maxRange:
                break
            API.Pause(self.checkInterval)

    def attemptTame(self):
        API.ClearJournal()
        API.UseSkill("Animal Taming")
        API.WaitForTarget()
        API.Target(self.petSerial)

    def run(self):
        API.SysMsg("Select the wild pet to tame", 34)
        self.petSerial = API.RequestTarget()
        attempts = 0
        while attempts < self.maxTamingAttempts:
            self.waitForPetInRange()
            API.ClearJournal()
            self.attemptTame()
            API.Pause(0.5)

            if not self.isAngry() and not self.isTooFar():
                API.Pause(self.tamingDelay)
                attempts += 1

        else:
            API.SysMsg("Too many attempts. Stopping.", 38)


TamingScript().run()
#=========== End of .\Pet\tame.py ============#

