from decimal import Decimal
import json
import time
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util
import Math
import Color

importlib.reload(Util)
importlib.reload(Math)
importlib.reload(Color)

from Util import Util
from Math import Math
from Color import Color

with open(LegionPath.createPath("_Jsons\\button-types.json")) as f:
    buttonTypesStr = json.load(f)


class Gump:
    buttonTypes = Math.convertToHex(buttonTypesStr)

    def __init__(self, width, height, onCloseCb=None, withStatus=True):
        self.width = width
        self.height = height
        self.onCloseCb = onCloseCb
        self.withStatus = withStatus

        self.gump = API.CreateGump(True, True)
        self.subGumps = []
        self.bg = None
        self._running = True
        self.buttons = []
        self.skillTextBoxes = []
        self.pendingCallbacks = []
        self.tabGumps = {}

        self.gump.SetWidth(self.width)
        self.gump.SetHeight(self.height)
        self.gump.CenterXInViewPort()
        self.gump.CenterYInViewPort()
        self.borders = self._setBorders(0, 0, self.width, self.height)
        self._setBackground()

        if withStatus:
            self.statusLabel = API.CreateGumpLabel("Ready.")
            self.statusLabel.SetX(10)
            self.statusLabel.SetY(self.height - 30)
            self.gump.Add(self.statusLabel)

        self._lastCheckTime = time.time()
        self._checkInterval = 0.1

    def create(self):
        API.AddGump(self.gump)

    def tick(self):
        if not self._running or self.gump.IsDisposed:
            self._running = False
            if self.onCloseCb:
                self.onCloseCb()
            else:
                self.destroy()
                API.Stop()
            return

        now = time.time()
        if (now - self._lastCheckTime) >= self._checkInterval:
            self.checkValidateForm()
            self._checkEvents()
            self._lastCheckTime = now

    def tickSubGumps(self):
        for subGump, position, _ in self.subGumps:
            if subGump._running and not subGump.gump.IsDisposed:
                self._setSubGumpPosition(subGump.gump, subGump.width, subGump.height, position)

    def destroy(self):
        if not self._running:
            return
        self._running = False
        for tab in self.tabGumps.values():
            try:
                if not tab.IsDisposed:
                    tab.Dispose()
            except:
                pass
        for subGump in self.subGumps:
            subGump.destroy()
        try:
            if not self.gump.IsDisposed:
                self.gump.Dispose()
        except Exception as e:
            API.SysMsg(f"Gump.Dispose failed: {e}", 33)
        API.SysMsg("Gump destroyed.", 66)

    def createSubGump(self, width, height, position="bottom", withStatus=False, alwaysVisible=True):
        gump = Gump(width, height, withStatus=withStatus)
        self._setSubGumpPosition(gump.gump, width, height, position)
        API.AddGump(gump.gump)
        self.subGumps.append((gump, position, alwaysVisible))
        return gump

    def setStatus(self, text, hue=996):
        if self.withStatus:
            self.statusLabel.Text = text
            if hue:
                self.statusLabel.Hue = hue

    def onClick(self, cb, startText=None, endText=None):
        def wrapped():
            if startText:
                self.setStatus(startText)
            cb()
            if endText:
                self.setStatus(endText)

        return wrapped

    def setActiveTab(self, name):
        if name not in self.tabGumps:
            return
        for subGumps, _, alwaysVisible in self.subGumps:
            if not alwaysVisible:
                subGumps.gump.IsVisible = False
        tabGump = self.tabGumps[name]
        tabGump.gump.IsVisible = True

    def addTabButton(self, name, iconType, gumpWidth, callback=None, yOffset=45, withStatus=False, label="", isDarkMode=False):
        y = 10 + len(self.tabGumps) * yOffset
        x = 0

        def onClick():
            self.setActiveTab(name)
            if callback:
                callback()

        btn = self.addButton(label, x + 5, y, iconType, self.onClick(onClick), isDarkMode)
        self.buttons.append(btn)
        tabGump = self.createSubGump(gumpWidth, self.height, "right", withStatus, False)
        tabGump.gump.IsVisible = False
        self.tabGumps[name] = tabGump
        return tabGump

    def addColorBox(self, x, y, height, width, colorHex=Color.defaultBlack, opacity=1):
        colorBox = API.CreateGumpColorBox(opacity, colorHex)
        colorBox.SetX(x)
        colorBox.SetY(y)
        colorBox.SetWidth(width)
        colorBox.SetHeight(height)
        self.gump.Add(colorBox)
        return colorBox        

    def addCheckbox(self, label, x, y, isChecked, callback, hue=996):
        checkbox = API.CreateGumpCheckbox(
            label, hue, isChecked
        )
        checkbox.SetX(x)
        checkbox.SetY(y)
        if callback:
            API.AddControlOnClick(checkbox, callback)
        self.gump.Add(checkbox)
        return checkbox

    def addButton(self, label, x, y, type, callback, isDarkMode = False):
        btnDef = Gump.buttonTypes.get(type, Gump.buttonTypes["default"])
        btn = API.CreateGumpButton(
            "", 996, btnDef["normal"], btnDef["pressed"], btnDef["hover"]
        )
        btn.SetX(x)
        btn.SetY(y)
        API.AddControlOnClick(btn, callback)
        self.gump.Add(btn)
        if type == "default":
            color = Color.defaultBlack
            if isDarkMode:
                color = Color.defaultWhite
            labelObj = self.addTtfLabel(label, x, y, 63, 23, 12, color, "center", callback)
        else:
            labelObj = API.CreateGumpLabel(label)
            labelObj.SetY(y)
            labelObj.SetX(50)
        API.AddControlOnClick(labelObj, callback)
        self.gump.Add(labelObj)
        return btn

    def addTtfLabel(
        self, label, x, y, width, height, fontSize, fontColorHex, position, callback
    ):
        ttfLabel = API.CreateGumpTTFLabel(
            label, fontSize, fontColorHex, maxWidth=width, aligned=position
        )
        centerY = y + int(height / 2) - 6
        ttfLabel.SetX(x)
        ttfLabel.SetY(centerY)
        API.AddControlOnClick(ttfLabel, self.onClick(callback))
        self.gump.Add(ttfLabel)
        return ttfLabel

    def addLabel(self, text, x, y, hue=None):
        label = API.CreateGumpLabel(text)
        label.SetX(x)
        label.SetY(y)
        if hue:
            label.Hue = hue
        self.gump.Add(label)
        return label

    def addSkillTextBox(
        self, defaultValue, x, y, minValue=0, maxValue=120, width=60, height=24
    ):
        clampedValue = max(minValue, min(maxValue, Decimal(defaultValue)))
        borderColor = "".join(Color.defaultWhite)
        borders = []
        for bx, by, bw, bh in [
            (x - 2, y - 2, width + 4, 2),
            (x - 2, y + height, width + 4, 2),
            (x - 2, y, 2, height),
            (x + width, y, 2, height),
        ]:
            border = API.CreateGumpColorBox(1, borderColor)
            border.SetX(bx)
            border.SetY(by)
            border.SetWidth(bw)
            border.SetHeight(bh)
            self.gump.Add(border)
            borders.append(border)
        textbox = API.CreateGumpTextBox(str(clampedValue), width, height, False)
        textbox.SetX(x)
        textbox.SetY(y)
        self.gump.Add(textbox)
        self.skillTextBoxes.append((textbox, minValue, maxValue, borders))
        return textbox

    def checkValidateForm(self):
        for skillTextBox, minValue, maxValue, borders in self.skillTextBoxes:
            isValidated = self._getValidatedNumber(skillTextBox, minValue, maxValue)
            color = Color.defaultWhite if isValidated else Color.defaultRed
            hue = Color.convertFromHexToHue(color)
            for border in borders:
                border.Hue = hue
            if not isValidated:
                return False
        return True

    def _getValidatedNumber(self, textbox, minValue, maxValue):
        try:
            if not textbox.Text:
                return False
            val = Decimal(textbox.Text)
            return minValue <= val <= maxValue
        except ValueError:
            return False

    def _checkEvents(self):
        API.ProcessCallbacks()
        while self.pendingCallbacks:
            cb = self.pendingCallbacks.pop(0)
            cb()

    def _setBackground(self):
        if not self.bg:
            self.bg = API.CreateGumpColorBox(0.75, Color.defaultBlack)
            self.gump.Add(self.bg)
        self.bg.SetWidth(self.width - 10)
        self.bg.SetHeight(self.height - 10)
        self.bg.SetX(0)
        self.bg.SetY(0)

    def _setBorders(
        self,
        x,
        y,
        width,
        height,
        frameColor=Color.defaultBorder,
        thickness=5,
        inside=False,
    ):
        positions = (
            [
                (x, y, width, thickness),
                (x, y + height - thickness, width, thickness),
                (x, y, thickness, height),
                (x + width - thickness, y, thickness, height),
            ]
            if inside
            else [
                (-thickness, -thickness, width, thickness),
                (-thickness, height - thickness * 2, width, thickness),
                (-thickness, -thickness, thickness, height),
                (width - thickness * 2, -thickness, thickness, height),
            ]
        )
        borders = []
        for bx, by, bw, bh in positions:
            border = API.CreateGumpColorBox(1, frameColor)
            border.SetX(bx)
            border.SetY(by)
            border.SetWidth(bw)
            border.SetHeight(bh)
            self.gump.Add(border)
            borders.append(border)
        return borders

    def _setSubGumpPosition(self, gump, width, height, position):
        gx, gy = self.gump.GetX(), self.gump.GetY()
        if position == "bottom":
            gump.SetX(gx)
            gump.SetY(gy + self.height)
        elif position == "top":
            gump.SetX(gx)
            gump.SetY(gy - height)
        elif position == "center":
            gump.SetX(gx + self.width // 2 - width // 2)
            gump.SetY(gy + self.height // 2 - height // 2)
        elif position == "left":
            gump.SetX(gx - width)
            gump.SetY(gy)
        elif position == "right":
            gump.SetX(gx + self.width)
            gump.SetY(gy)
