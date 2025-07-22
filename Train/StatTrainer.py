import API
import importlib
import sys
import traceback

sys.path.append(r".\\TazUO\\LegionScripts\\_Classes")
sys.path.append(r".\\TazUO\\LegionScripts\\_Utils")
sys.path.append(r".\\TazUO\\LegionScripts\\_Skills")

import Gump
import Util
import Math
import ArmsLore
import ItemIdentification

importlib.reload(Gump)
importlib.reload(Util)
importlib.reload(Math)
importlib.reload(ArmsLore)
importlib.reload(ItemIdentification)

from Gump import Gump
from Util import Util
from Math import Math
from ArmsLore import ArmsLore
from ItemIdentification import ItemIdentification


class StatTrainer:
    def __init__(self):
        self._running = True
        self.gump = None
        self.statInputs = []
        self.stats = [
            {
                "statName": "Strength",
                "name": "str",
                "lock": "StrLock",
                "trainer": ArmsLore,
                "value": Util.getStatValue("Strength"),
            },
            {
                "statName": "Dexterity",
                "name": "dex",
                "lock": "DexLock",
                "trainer": ItemIdentification,
                "value": Util.getStatValue("Dexterity"),
            },
            {
                "statName": "Intelligence",
                "name": "int",
                "lock": "IntLock",
                "trainer": ItemIdentification,
                "value": Util.getStatValue("Intelligence"),
            },
        ]
        self._started = False
        self._activeStat = None
        self._activeTrainer = None

    def main(self):
        try:
            Util.openContainer(API.Backpack)
            self._showGump()
            self.gump.create()
        except Exception as e:
            API.SysMsg(f"StatTrainer e: {e}", 33)
            API.SysMsg(traceback.format_exc())
            self._onClose()

    def tick(self):
        if not self._running:
            return False
        if self.gump:
            self.gump.tick()
            self.gump.tickSubGumps()
            if self.gump.gump.IsDisposed:
                self._onClose()
                return False
        if self._started and self._activeStat and self._activeTrainer:
            self._setStatLocks()
            statName = self._activeStat["statName"]
            current = Util.getStatValue(statName)
            if current < self._activeStat["value"]:
                self._activeTrainer.trainOnce()
            else:
                self._advanceToNextStat()
        return True

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

    def _validate(self):
        if Util.getTotalSkillPoints() < 720:
            API.SysMsg("You must be at skill cap (720)", 33)
            API.Stop()

    def _setSkillLocks(self):
        for skillName in Util.skillNames:
            API.SetSkillLock(skillName, "locked")

    def _setStatLocks(self):
        for stat in self.stats:
            target = int(stat["value"])
            current = Util.getStatValue(stat["statName"])
            if current == target:
                mode = "locked"
            elif current < target:
                mode = "up"
            else:
                mode = "down"
            if getattr(API.Player, stat["lock"]).lower() != mode:
                API.SetStatLock(stat["name"], mode)

    def _onStart(self):
        self._validate()
        self._setSkillLocks()
        self._started = True
        self._advanceToNextStat()

    def _advanceToNextStat(self):
        for stat in self.stats:
            if Util.getStatValue(stat["statName"]) < stat["value"]:
                self.gump.setStatus(f"Training: {stat['statName']}")
                self._activeStat = stat
                self._activeTrainer = stat["trainer"]()
                return
        API.SysMsg("Done!", 88)
        self._onClose()

    def _addValue(self, value, label, totalLbl, stat):
        current = int(label.Text)
        new = current + value
        if not (10 <= new <= 125):
            return
        totalNow = int(totalLbl.Text)
        newTotal = totalNow + value
        if newTotal > API.Player.StatsCap:
            return
        stat["value"] = new
        label.Text = str(new)
        totalLbl.Text = str(newTotal)

    def _showGump(self):
        height = 100 + 30 * len(self.stats)
        width = 300

        g = Gump(width, height, self._onClose)
        self.gump = g
        g.addLabel("Stat Adjustements", 90, 5)

        self.statInputs = []
        y = 40
        total = 0
        x = 150
        totalLbl = g.addLabel("0", x, 0)
        g.addLabel("|", x + 30, 0)
        g.addLabel(str(API.Player.StatsCap), x + 45, 0)

        for stat in self.stats:
            statName = stat["statName"]
            lbl = g.addLabel(statName, 10, y)
            value = stat["value"]
            total += value
            statLbl = g.addLabel(str(value), x, y)

            for dx, hue, val in [
                (-50, "arrowLeftGray", -5),
                (-30, "arrowLeftBlue", -1),
                (75, "arrowRightGray", 1),
                (95, "arrowRightBlue", 5),
            ]:
                g.addButton(
                    "",
                    x + dx,
                    y,
                    hue,
                    g.onClick(
                        lambda v=val, l=statLbl, t=totalLbl, s=stat: self._addValue(
                            v, l, t, s
                        )
                    ),
                )

            g.addLabel("|", x + 30, y)
            g.addLabel("125", x + 45, y)
            self.statInputs.append((stat, statLbl, lbl))
            y += 30

        totalLbl.Text = str(total)
        totalLbl.SetY(y)
        g.addButton(
            "", 10, y, "okay", g.onClick(self._onStart, "Validating...", "Training")
        )


trainer = StatTrainer()
trainer.main()
while trainer._isRunning():
    trainer.gump.tick()
    trainer.gump.tickSubGumps()
    trainer.tick()
    API.Pause(0.1)