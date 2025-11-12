import API
import importlib
import traceback
import re
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Gump
import Util
import Math
import Timer
import Magic
import Python

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Timer)
importlib.reload(Magic)
importlib.reload(Python)

from Gump import Gump
from Util import Util
from Math import Math
from Timer import Timer
from Magic import Magic
from Python import Python


class ProgressBar:
    gumpId = 999060
    fameRe = re.compile(r"Fame:\s*(\d+)", re.IGNORECASE)
    karmaRe = re.compile(r"Karma:\s*(\d+)", re.IGNORECASE)

    def __init__(self):
        self._running = True
        self.gump = None

        self._karmaProgressBar = None
        self._fameProgressBar = None
        self._skills = [{ "name": "Animal Taming", "progressBar": None }]

    def main(self):
        try:
            self._showGump()
        except Exception as e:
            API.SysMsg(f"ProgressBar e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            progressBar.gump.tick()
            progressBar.gump.tickSubGumps()
        return True

    def run(self):
        values = self._checkJournal()
        if values:
            if self._karmaProgressBar:
                for e in self._karmaProgressBar:
                    e.Dispose()
            if self._fameProgressBar:
                for e in self._fameProgressBar:
                    e.Dispose()
            y = 1
            self._karmaProgressBar = self.gump.createProgressBar(1, y, 19, 500 - 12, values["karma"], 10000)
            y += 20
            self._fameProgressBar = self.gump.createProgressBar(1, y, 19, 500 - 12, values["fame"], 32000)
            for skill in self._skills:
                y += 20
                skill["progressBar"] = self.gump.createProgressBar(1, y, 19, 500 - 12, Util.getSkillInfo(skill["name"])["value"], 100)

    def _checkJournal(self):
        journalMessages = ["$You have (.*) fame.", "$You have (.*) karma."]
        for skill in self._skills:
            name = skill["name"]
            journalMessages.append(f"$Your skill in {name} has increased(.*).")
        if not API.InJournalAny(journalMessages):
            return
        API.ClearJournal()
        return self._getValues()

    def _getValues(self):
        API.ContextMenu(API.Player.Serial, 915)

        # Wait until gump appears
        attempts = 0
        while not API.HasGump(self.gumpId) and attempts < 50:
            API.Pause(0.1)
            attempts += 1

        if not API.HasGump(self.gumpId):
            API.SysMsg("[ProgressBar] Gump did not open.", 33)
            return {"fame": 0, "karma": 0}

        # Now wait until fame/karma data is populated
        fame_match = None
        karma_match = None

        for _ in range(30):  # retry up to 3 seconds
            lines = API.GetGumpContents(self.gumpId)
            fame_match = self.fameRe.search(lines)
            karma_match = self.karmaRe.search(lines)
            if fame_match and karma_match:
                break
            API.Pause(0.1)  # let the server populate

        API.CloseGump(self.gumpId)

        fame = int(fame_match.group(1)) if fame_match else 0
        karma = int(karma_match.group(1)) if karma_match else 0
        return {"fame": fame, "karma": karma}

    def _showGump(self):
        width = 500
        height = 51 + (20 * len(self._skills))
        g = Gump(width, height, self._onClose, False)
        self.gump = g
        y = 1

        values = self._getValues()

        self._karmaProgressBar = self.gump.createProgressBar(1, y, 19, width - 12, values["karma"], 10000)
        y += 20
        self._karmaProgressBar = self.gump.createProgressBar(1, y, 19, width - 12, values["fame"], 32000)
        for skill in self._skills:
            y += 20
            skill["progressBar"] = self.gump.createProgressBar(1, y, 19, 500 - 12, Util.getSkillInfo(skill["name"])["value"], 100)


        self.gump.create()

    def _isRunning(self):
        return self._running

    def _onClose(self):
        if not self._running:
            return
        self._running = False
        if self.gump:
            for subGump in self.gump.subGumps:
                subGump.destroy()
            self.gump.destroy()
            self.gump = None
        API.Stop()


progressBar = ProgressBar()
progressBar.main()
while progressBar._isRunning():
    progressBar.tick()
    progressBar.run()
    API.Pause(0.1)
