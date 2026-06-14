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

from button_types import buttonTypesStr


class GumpRadio:
    def __init__(self, nativeRadio, fills):
        self.nativeRadio = nativeRadio
        self.fills = fills

    @property
    def IsChecked(self):
        return self.nativeRadio.IsChecked

    @IsChecked.setter
    def IsChecked(self, value):
        self.nativeRadio.IsChecked = value
        for fill in self.fills:
            fill.IsVisible = value


class Gump:
    buttonTypes = Math.convertToHex(buttonTypesStr)
    theme = {
        "bgOuter": "#030201",
        "bgInner": "#061014",
        "bgInset": "#0a1519",
        "grainLine": "#d7a94a",
        "frameOuter": "#070401",
        "frameInner": "#b67d28",
        "frameHighlight": "#f2c45e",
        "panelOuter": "#6a4316",
        "panelInner": "#0a171b",
        "panelTop": "#102a32",
        "panelBottom": "#050a0d",
        "panelHeader": "#0b1519",
        "panelHeaderLine": "#b67d28",
        "buttonShadow": "#000000",
        "buttonFrame": "#bd842e",
        "buttonInset": "#05090b",
        "buttonFill": "#0e3340",
        "buttonHighlight": "#1f6275",
        "buttonText": "#ffd66b",
        "buttonTextDark": "#fff8dc",
        "row": "#0d1b20",
        "rowAlt": "#091317",
        "selectedRow": "#173522",
        "statusBg": "#050a0d",
        "inputFill": "#080d10",
        "sectionBadge": "#0b1114",
    }
    hues = {"text": 2414, "muted": 2406, "accent": 67, "status": 996}

    def __init__(self, width, height, onCloseCb=None, withStatus=True, gumpId=None):
        self.width = width
        self.height = height
        self.onCloseCb = onCloseCb
        self.withStatus = withStatus
        self.gumpId = gumpId

        try:
            self.gump = API.CreateGump(True, True, False, self.gumpId or 0)
        except:
            self.gump = API.CreateGump(True, True)
        if self.gumpId is not None:
            for attr in ["ID", "LocalSerial", "ServerSerial"]:
                try:
                    setattr(self.gump, attr, self.gumpId)
                except:
                    pass
        self.subGumps = []
        self.bg = None
        self._running = True
        self.buttons = []
        self.hoverControls = []
        self.skillTextBoxes = []
        self.pendingCallbacks = []
        self.tabGumps = {}
        self._statusPanel = []

        self.gump.SetWidth(self.width)
        self.gump.SetHeight(self.height)
        self.gump.CenterXInViewPort()
        self.gump.CenterYInViewPort()
        self._setBackground()
        self.borders = self._setBorders(
            0, 0, self.width, self.height, Gump.theme["frameOuter"], 3, True
        )
        self._setBorders(
            2, 2, self.width - 4, self.height - 4, Gump.theme["frameInner"], 1, True
        )
        self._setCornerAccents()

        if withStatus:
            self._drawStatusArea()

        self._lastCheckTime = time.time()
        self._checkInterval = 0.1

    def create(self):
        self._applyGumpId()
        API.AddGump(self.gump)

    def _applyGumpId(self):
        if self.gumpId is None:
            return
        for attr in ["ID", "LocalSerial", "ServerSerial"]:
            try:
                setattr(self.gump, attr, self.gumpId)
            except:
                pass

    def tick(self):
        if not self._running:
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
            self._updateHoverControls()
            self._lastCheckTime = now

    def tickSubGumps(self):
        for subGump, position, _ in self.subGumps:
            if subGump._running and not subGump.gump.IsDisposed:
                self._setSubGumpPosition(
                    subGump.gump, subGump.width, subGump.height, position
                )

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
        for subGump, _, _ in self.subGumps:
            subGump.destroy()
        try:
            if not self.gump.IsDisposed:
                self.gump.Dispose()
        except Exception as e:
            API.SysMsg(f"Gump.Dispose failed: {e}", 33)
        API.SysMsg("Gump destroyed.", 66)

    def createProgressBar(self, x, y, height, width, current, total, title=""):
        elements = []
        if total <= 0:
            total = 1

        if title:
            label = self.addLabel(title, x, y, Gump.hues["text"])
            elements.append(label)
            y += 18

        panel = self.addPanel(x, y, width, height, withTexture=False)
        elements.extend(panel["elements"])

        ratio = max(0.0, min(1.0, current / total))
        fillWidth = int((width - 6) * ratio)
        if fillWidth > 0:
            fill = self.addColorBox(
                x + 3, y + 3, height - 6, fillWidth, Gump.theme["buttonHighlight"], 0.95
            )
            elements.append(fill)

        progressLabel = self.addLabel(
            f"{int(current)} / {int(total)}",
            x + width // 2 - 20,
            y + (height // 2) - 7,
            Gump.hues["text"],
        )
        elements.append(progressLabel)
        return elements

    def createStackedBarChart(self, x, y, height, width, count, title=""):
        elements = []
        if title:
            label = self.addLabel(title, x, y, Gump.hues["text"])
            elements.append(label)
            y += 18

        panel = self.addPanel(x, y, width, height, withTexture=False)
        elements.extend(panel["elements"])

        eliteWidth = int((width - 6) * (count / 100))
        eliteBar = self.addColorBox(
            x + 3, y + 3, height - 6, max(0, eliteWidth), "#2a8f39", 0.95
        )
        elements.append(eliteBar)

        nonEliteWidth = (width - 6) - eliteWidth
        if nonEliteWidth > 0:
            nonEliteBar = self.addColorBox(
                x + 3 + eliteWidth,
                y + 3,
                height - 6,
                nonEliteWidth,
                "#8f171a",
                0.95,
            )
            elements.append(nonEliteBar)
        return elements

    def createSubGump(
        self, width, height, position="bottom", withStatus=False, alwaysVisible=True
    ):
        gump = Gump(width, height, withStatus=withStatus)
        self._setSubGumpPosition(gump.gump, width, height, position)
        API.AddGump(gump.gump)
        self.subGumps.append((gump, position, alwaysVisible))
        return gump

    def setStatus(self, text, hue=None):
        if hue is None:
            hue = Gump.hues["status"]
        if self.withStatus:
            self.statusLabel.Text = text
            if hue is not None:
                self.statusLabel.Hue = hue

    def onClick(self, cb, startText=None, endText=None):
        if not cb:
            return lambda: None

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

    def addTabButton(
        self,
        name,
        iconType,
        gumpWidth,
        callback=None,
        yOffset=45,
        withStatus=False,
        label="",
        isDarkMode=False,
    ):
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

    def addTitle(self, text, y=7, hue=None, compact=False):
        if hue is None:
            hue = Gump.hues["accent"]
        self.addColorBox(
            14,
            y - 2,
            20,
            self.width - 28,
            Gump.theme["panelHeader"],
            0.72,
            withTexture=False,
        )
        dividerX = 18 if not compact else 26
        dividerWidth = self.width - 36 if not compact else self.width - 52
        accentWidth = 42 if not compact else 34
        self.addDivider(dividerX, y + 18, dividerWidth)
        self.addColorBox(dividerX + 8, y + 4, 1, accentWidth, Gump.theme["frameHighlight"], 0.55)
        self.addColorBox(self.width - dividerX - accentWidth - 8, y + 4, 1, accentWidth, Gump.theme["frameHighlight"], 0.55)
        x = round(self.width / 2 - (len(text) * 3.5))
        return self.addLabel(text, x, y, hue)

    def addDivider(self, x, y, width, opacity=0.95):
        lines = []
        top = self.addColorBox(
            x, y, 1, width, Gump.theme["panelHeaderLine"], opacity, withTexture=False
        )
        bottom = self.addColorBox(
            x, y + 1, 1, width, Gump.theme["bgInset"], 0.85, withTexture=False
        )
        lines.extend([top, bottom])
        return lines

    def addPanel(self, x, y, width, height, title=None, titleHue=None, withTexture=True):
        if titleHue is None:
            titleHue = Gump.hues["text"]
        elements = []
        outer = self.addColorBox(
            x, y, height, width, Gump.theme["panelOuter"], 0.96, withTexture=False
        )
        inner = self.addColorBox(
            x + 1,
            y + 1,
            height - 2,
            width - 2,
            Gump.theme["panelInner"],
            0.95,
            withTexture=False,
        )
        topTint = self.addColorBox(
            x + 2,
            y + 2,
            max(6, int(height * 0.25)),
            max(1, width - 4),
            Gump.theme["panelTop"],
            0.35,
            withTexture=False,
        )
        bottomTint = self.addColorBox(
            x + 2,
            y + max(2, int(height * 0.55)),
            max(1, height - int(height * 0.55) - 2),
            max(1, width - 4),
            Gump.theme["panelBottom"],
            0.45,
            withTexture=False,
        )
        elements.extend([outer, inner, topTint, bottomTint])
        inset = self._setBorders(
            x + 3,
            y + 3,
            width - 6,
            height - 6,
            Gump.theme["frameOuter"],
            1,
            True,
        )
        elements.extend(inset)

        if withTexture and width > 40 and height > 26:
            step = 14
            for offset in range(8, height - 4, step):
                line = self.addColorBox(
                    x + 3,
                    y + offset,
                    1,
                    width - 6,
                    Gump.theme["grainLine"],
                    0.025,
                    withTexture=False,
                )
                elements.append(line)
            for offset in range(16, width - 8, 32):
                grain = self.addColorBox(
                    x + offset,
                    y + 5,
                    height - 10,
                    1,
                    Gump.theme["grainLine"],
                    0.01,
                    withTexture=False,
                )
                elements.append(grain)

        contentX = x + 8
        contentY = y + 8
        contentHeight = height - 16
        if title:
            header = self.addColorBox(
                x + 1,
                y + 1,
                18,
                width - 2,
                Gump.theme["panelHeader"],
                0.9,
                withTexture=False,
            )
            headerLine = self.addColorBox(
                x + 2,
                y + 19,
                1,
                width - 4,
                Gump.theme["panelHeaderLine"],
                0.9,
                withTexture=False,
            )
            label = self.addLabel(title, x + 8, y + 3, titleHue)
            elements.extend([header, headerLine, label])
            contentY = y + 24
            contentHeight = height - 32

        return {
            "x": contentX,
            "y": contentY,
            "width": max(1, width - 16),
            "height": max(1, contentHeight),
            "elements": elements,
        }

    def addRow(self, x, y, width, height=20, selected=False):
        color = Gump.theme["selectedRow"] if selected else Gump.theme["row"]
        row = self.addColorBox(x, y, height, width, color, 0.72, withTexture=True)
        self.addColorBox(x, y + height - 1, 1, width, "#000000", 0.45)
        self.addColorBox(x, y, 1, width, "#ffffff", 0.04)
        return row

    def addTableFrame(self, x, y, width, height, columns=None):
        panel = self.addPanel(x, y, width, height, withTexture=True)
        if columns:
            for colX in columns:
                self.addColorBox(x + colX, y + 4, height - 8, 1, Gump.theme["panelHeaderLine"], 0.35)
        return panel

    def addChartGrid(self, x, y, width, height, yLabels=None, xLabels=None):
        elements = []
        frame = self.addPanel(x, y, width, height, withTexture=False)
        elements.extend(frame["elements"])
        gridX = x + 30
        gridY = y + 14
        gridWidth = width - 42
        gridHeight = height - 36
        for i in range(0, 6):
            lineY = gridY + int(gridHeight * i / 5)
            elements.append(self.addColorBox(gridX, lineY, 1, gridWidth, "#6b6b58", 0.18))
            if yLabels and i < len(yLabels):
                elements.append(self.addLabel(yLabels[i], x + 6, lineY - 6, hue=2406))
        for i in range(0, 10):
            lineX = gridX + int(gridWidth * i / 9)
            elements.append(self.addColorBox(lineX, gridY, gridHeight, 1, "#6b6b58", 0.08))
            if xLabels and i < len(xLabels):
                elements.append(self.addLabel(xLabels[i], lineX - 3, gridY + gridHeight + 5, hue=2406))
        self.addColorBox(gridX, gridY + gridHeight, 1, gridWidth, Gump.theme["frameHighlight"], 0.75)
        return {
            "x": gridX,
            "y": gridY,
            "width": gridWidth,
            "height": gridHeight,
            "elements": elements,
        }

    def addColorBox(
        self,
        x,
        y,
        height,
        width,
        colorHex=Color.defaultBlack,
        opacity=1,
        withTexture=False,
    ):
        colorBox = self._createColorBox(x, y, width, height, colorHex, opacity)
        if withTexture and width > 20 and height > 8:
            self._createColorBox(x + 1, y + 1, width - 2, 1, "#ffffff", 0.06)
            self._createColorBox(x + 1, y + height - 2, width - 2, 1, "#000000", 0.25)
        return colorBox

    def addCheckbox(self, label, x, y, isChecked, callback, hue=None):
        if hue is None:
            hue = Gump.hues["text"]
        checkbox = API.CreateGumpCheckbox(label, hue, isChecked)
        checkbox.SetX(x)
        checkbox.SetY(y)
        if callback:
            API.AddControlOnClick(checkbox, callback)
        self.gump.Add(checkbox)
        return checkbox

    def addRadio(self, label, x, y, group, isChecked, callback, hue=None, labelYOffset=0, boxYOffset=2):
        if hue is None:
            hue = Gump.hues["text"]
        radio = API.CreateGumpRadioButton("", group, 9020, 9021, hue, isChecked)
        radio.SetX(x)
        radio.SetY(y)
        radio.IsVisible = False
        if callback:
            API.AddControlOnClick(radio, callback)
        boxY = y + boxYOffset
        self.addColorBox(x, boxY, 14, 14, "#030506", 0.95)
        self.addColorBox(x + 1, boxY + 1, 12, 12, Gump.theme["frameInner"], 0.95)
        self.addColorBox(x + 2, boxY + 2, 10, 10, "#111b20", 1)
        self.addColorBox(x + 3, boxY + 3, 8, 8, "#050809", 1)
        fills = [
            self.addColorBox(x + 4, boxY + 4, 6, 6, "#76c84a", 1),
            self.addColorBox(x + 5, boxY + 5, 4, 4, "#b9ef80", 0.9),
        ]
        for fill in fills:
            fill.IsVisible = isChecked
        self.gump.Add(radio)
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(18)
        hitTarget.SetHeight(18)
        if callback:
            API.AddControlOnClick(hitTarget, callback)
        self.gump.Add(hitTarget)
        labelObj = self.addLabel(label, x + 22, y + labelYOffset, hue)
        if callback:
            API.AddControlOnClick(labelObj, callback)
        return GumpRadio(radio, fills)

    def addRadioRow(self, label, x, y, width, group, isChecked, callback, hue=None, selected=None):
        if selected is None:
            selected = isChecked
        self.addRow(x, y, width, 20, selected)
        return self.addRadio(label, x + 10, y + 1, group, isChecked, callback, hue, 1, 2)

    def addButton(self, label, x, y, type, callback=None, isDarkMode=False, width=63, height=24, fontSize=13):
        if type == "default":
            self.addColorBox(
                x + 2, y + 4, height - 2, width, Gump.theme["buttonShadow"], 0.55, withTexture=False
            )
            self.addColorBox(
                x, y, height, width, Gump.theme["buttonFrame"], 1, withTexture=False
            )
            self.addColorBox(
                x + 1, y + 1, height - 2, width - 2, Gump.theme["buttonInset"], 1, withTexture=False
            )
            self.addColorBox(
                x + 2, y + 2, max(1, int((height - 4) / 2)), width - 4, Gump.theme["buttonHighlight"], 0.9, withTexture=True
            )
            self.addColorBox(
                x + 2, y + 2 + max(1, int((height - 4) / 2)), max(1, height - 4 - max(1, int((height - 4) / 2))), width - 4, Gump.theme["buttonFill"], 0.95, withTexture=False
            )
            self.addColorBox(
                x + 2, y + 2, 1, width - 4, "#ffffff", 0.14, withTexture=False
            )
            self.addColorBox(
                x + 2, y + height - 2, 1, width - 4, "#000000", 0.6, withTexture=False
            )
            hover = self.addColorBox(
                x + 2, y + 2, height - 4, width - 4, Gump.theme["frameHighlight"], 0.18, withTexture=False
            )
            hover.IsVisible = False
            btn = API.CreateGumpColorBox(0.01, "#000000")
            btn.SetX(x)
            btn.SetY(y)
            btn.SetWidth(width)
            btn.SetHeight(height)
            if callback:
                API.AddControlOnClick(btn, callback)
        else:
            btnDef = Gump.buttonTypes.get(type, Gump.buttonTypes["default"])
            btn = API.CreateGumpButton("", 996, btnDef["normal"], btnDef["pressed"], btnDef["hover"])
            btn.SetX(x)
            btn.SetY(y)
            if callback:
                API.AddControlOnClick(btn, callback)
            self.gump.Add(btn)

        if label:
            if type == "default":
                color = Gump.theme["buttonText"]
                if isDarkMode:
                    color = Gump.theme["buttonTextDark"]
                labelObj = self.addTtfLabel(label, x, y, width, height, fontSize, color, "center", None)
                self.hoverControls.append({"targets": [btn, labelObj], "hover": hover})
                self.gump.Add(btn)
            else:
                labelObj = API.CreateGumpLabel(label, Gump.hues["text"])
                labelObj.SetY(y)
                labelObj.SetX(x + 24)
                if callback:
                    API.AddControlOnClick(labelObj, callback)
                self.gump.Add(labelObj)
        elif type == "default":
            self.hoverControls.append({"targets": [btn], "hover": hover})
            self.gump.Add(btn)
        return btn

    def addHelpButton(self, x, y, callback=None, width=20, height=20):
        self.addColorBox(x + 6, y, 2, width - 12, "#7bd8ff", 0.9)
        self.addColorBox(x + 3, y + 2, 2, width - 6, "#1f8bc3", 1)
        self.addColorBox(x + 1, y + 4, height - 8, width - 2, "#0e5f8a", 1)
        self.addColorBox(x + 3, y + height - 4, 2, width - 6, "#053650", 1)
        self.addColorBox(x + 6, y + height - 2, 2, width - 12, "#032233", 1)
        self.addColorBox(x + 5, y + 4, 4, width - 10, "#2fb3ef", 0.72)
        self.addColorBox(x + 3, y + 6, height - 12, width - 6, "#0b4060", 0.38)
        hover = self.addColorBox(x + 2, y + 2, height - 4, width - 4, "#62c6ff", 0.24)
        hover.IsVisible = False
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(width)
        hitTarget.SetHeight(height)
        if callback:
            API.AddControlOnClick(hitTarget, callback)
        self.addColorBox(x + 9, y + 5, 2, 2, "#f5fbff", 1, withTexture=False)
        self.addColorBox(x + 9, y + 9, 7, 2, "#f5fbff", 1, withTexture=False)
        self.addColorBox(x + 8, y + 16, 1, 4, "#f5fbff", 1, withTexture=False)
        self.hoverControls.append({"targets": [hitTarget], "hover": hover})
        self.gump.Add(hitTarget)
        return hitTarget

    def _updateHoverControls(self):
        for item in self.hoverControls:
            isHovered = False
            for target in item["targets"]:
                try:
                    if target.MouseIsOver:
                        isHovered = True
                        break
                except:
                    pass
            try:
                item["hover"].IsVisible = isHovered
            except:
                pass

    def addTtfLabel(
        self, label, x, y, width, height, fontSize, fontColorHex, position, callback
    ):
        ttfLabel = API.CreateGumpTTFLabel(
            label, fontSize, fontColorHex, maxWidth=width, aligned=position, applyStroke=True
        )
        centerY = y + max(0, int((height - fontSize) / 2))
        ttfLabel.SetX(x)
        ttfLabel.SetY(centerY)
        if callback:
            API.AddControlOnClick(ttfLabel, callback)
        self.gump.Add(ttfLabel)
        return ttfLabel

    def addLabel(self, text, x, y, hue=None):
        if hue is None:
            hue = Gump.hues["text"]
        label = API.CreateGumpLabel(text, hue)
        label.SetX(x)
        label.SetY(y)
        self.gump.Add(label)
        return label

    def addSkillTextBox(
        self, defaultValue, x, y, minValue=0, maxValue=120, width=60, height=24
    ):
        clampedValue = max(minValue, min(maxValue, Decimal(defaultValue)))
        borderColor = "".join(Color.defaultWhite)
        borders = []

        self.addColorBox(x - 4, y - 4, height + 8, width + 8, Gump.theme["panelOuter"], 0.95)
        self.addColorBox(x - 3, y - 3, height + 6, width + 6, Gump.theme["panelInner"], 0.95)
        self.addColorBox(x - 2, y - 2, height + 4, width + 4, "#1a1a1a", 0.85)

        for bx, by, bw, bh in [
            (x - 1, y - 1, width + 2, 1),
            (x - 1, y + height, width + 2, 1),
            (x - 1, y, 1, height),
            (x + width, y, 1, height),
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

    def _createColorBox(self, x, y, width, height, colorHex, opacity=1, container=None):
        if width <= 0 or height <= 0:
            return None
        colorBox = API.CreateGumpColorBox(opacity, colorHex)
        colorBox.SetX(x)
        colorBox.SetY(y)
        colorBox.SetWidth(width)
        colorBox.SetHeight(height)
        if container:
            container.Add(colorBox)
        else:
            self.gump.Add(colorBox)
        return colorBox

    def _setBackground(self):
        if not self.bg:
            self.bg = API.CreateGumpColorBox(1, Gump.theme["bgOuter"])
            self.gump.Add(self.bg)

        self.bg.SetWidth(self.width)
        self.bg.SetHeight(self.height)
        self.bg.SetX(0)
        self.bg.SetY(0)

        self._createColorBox(3, 3, self.width - 6, self.height - 6, Gump.theme["bgInner"], 0.98)
        self._createColorBox(5, 5, self.width - 10, self.height - 10, Gump.theme["bgInset"], 0.92)
        self._createColorBox(5, 5, self.width - 10, 26, "#1d3344", 0.28)
        self._createColorBox(5, self.height - 34, self.width - 10, 22, "#05090d", 0.6)

        for y in range(10, self.height - 10, 20):
            self._createColorBox(8, y, self.width - 16, 1, Gump.theme["grainLine"], 0.03)
        for x in range(16, self.width - 16, 36):
            self._createColorBox(x, 8, 1, self.height - 16, Gump.theme["grainLine"], 0.015)

    def _drawStatusArea(self):
        self._statusPanel.extend(self.addDivider(8, self.height - 33, self.width - 16))
        bg = self.addColorBox(
            8, self.height - 31, 22, self.width - 16, Gump.theme["statusBg"], 0.92, withTexture=True
        )
        self._statusPanel.append(bg)

        self.statusLabel = API.CreateGumpLabel("Ready.", Gump.hues["status"])
        self.statusLabel.SetX(14)
        self.statusLabel.SetY(self.height - 27)
        self.gump.Add(self.statusLabel)

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

    def _setCornerAccents(self):
        accentWidth = 14
        accentHeight = 2
        accentColor = Gump.theme["frameHighlight"]
        for x, y in [
            (4, 4),
            (self.width - 18, 4),
            (4, self.height - 6),
            (self.width - 18, self.height - 6),
        ]:
            self.addColorBox(x, y, accentHeight, accentWidth, accentColor, 0.9, withTexture=False)

    def addTabButton(
        self,
        name,
        iconType,
        gumpWidth,
        callback=None,
        yOffset=68,
        withStatus=False,
        label="",
        isDarkMode=False,
    ):
        y = 12 + len(self.tabGumps) * yOffset
        x = 11

        def onClick():
            self.setActiveTab(name)
            if callback:
                callback()

        slot = [
            self.addColorBox(x - 4, y - 4, 60, 58, Gump.theme["frameOuter"], 1, withTexture=False),
            self.addColorBox(x - 2, y - 2, 56, 54, Gump.theme["frameInner"], 0.95, withTexture=False),
            self.addColorBox(x, y, 52, 50, Gump.theme["bgInset"], 0.96, withTexture=True),
        ]
        btn = self.addButton(label, x + 6, y + 6, iconType, self.onClick(onClick), isDarkMode)
        self.buttons.append({"slot": slot, "button": btn})
        tabGump = self.createSubGump(gumpWidth, self.height, "right", withStatus, False)
        tabGump.gump.IsVisible = False
        self.tabGumps[name] = tabGump
        return tabGump

    def addTitle(self, text, y=7, hue=None, compact=False):
        if hue is None:
            hue = Gump.hues["text"]
        dividerX = 76 if not compact else 48
        dividerWidth = max(40, self.width - dividerX * 2)
        self.addDivider(dividerX, y + 29, dividerWidth, 0.72)
        mid = self.width // 2
        self.addColorBox(mid - 9, y + 26, 7, 18, Gump.theme["bgInset"], 0.98, withTexture=False)
        self.addColorBox(mid - 6, y + 27, 5, 12, Gump.theme["frameHighlight"], 0.9, withTexture=False)
        self.addColorBox(mid - 3, y + 28, 3, 6, Gump.theme["bgOuter"], 0.95, withTexture=False)
        return self.addTtfLabel(text, 0, y + 2, self.width, 28, 18, Gump.theme["buttonText"], "center", None)

    def addPanel(self, x, y, width, height, title=None, titleHue=None, withTexture=True):
        if titleHue is None:
            titleHue = Gump.hues["text"]
        elements = []
        elements.append(self.addColorBox(x, y, height, width, Gump.theme["panelOuter"], 1, withTexture=False))
        elements.append(self.addColorBox(x + 1, y + 1, height - 2, width - 2, Gump.theme["bgOuter"], 0.96, withTexture=False))
        elements.append(self.addColorBox(x + 3, y + 3, height - 6, width - 6, Gump.theme["panelInner"], 0.96, withTexture=False))
        elements.append(self.addColorBox(x + 4, y + 4, max(8, int(height * 0.28)), width - 8, Gump.theme["panelTop"], 0.24, withTexture=True))
        elements.append(self.addColorBox(x + 4, y + max(4, height - 36), max(1, min(32, height - 8)), width - 8, Gump.theme["panelBottom"], 0.44, withTexture=False))
        elements.extend(self._setBorders(x + 3, y + 3, width - 6, height - 6, Gump.theme["frameOuter"], 1, True))

        if withTexture and width > 40 and height > 24:
            for offset in range(16, height - 6, 24):
                elements.append(self.addColorBox(x + 4, y + offset, 1, width - 8, Gump.theme["grainLine"], 0.035, withTexture=False))

        contentX = x + 8
        contentY = y + 8
        contentHeight = height - 16
        if title:
            elements.append(self.addColorBox(x + 7, y + 30, 1, width - 14, Gump.theme["panelHeaderLine"], 0.55, withTexture=False))
            label = self.addLabel(title, x + 32, y + 8, titleHue)
            elements.append(label)
            contentY = y + 34
            contentHeight = height - 42

        return {
            "x": contentX,
            "y": contentY,
            "width": max(1, width - 16),
            "height": max(1, contentHeight),
            "elements": elements,
        }

    def addRow(self, x, y, width, height=20, selected=False):
        color = Gump.theme["selectedRow"] if selected else Gump.theme["row"]
        row = self.addColorBox(x, y, height, width, color, 0.55, withTexture=False)
        self.addColorBox(x, y, 1, width, "#2f4850", 0.24, withTexture=False)
        self.addColorBox(x, y + height - 1, 1, width, "#000000", 0.55, withTexture=False)
        return row

    def addSkillTextBox(
        self, defaultValue, x, y, minValue=0, maxValue=120, width=60, height=24
    ):
        clampedValue = max(minValue, min(maxValue, Decimal(defaultValue)))
        borders = []
        self.addColorBox(x - 3, y - 3, height + 6, width + 6, Gump.theme["buttonShadow"], 0.72, withTexture=False)
        self.addColorBox(x - 2, y - 2, height + 4, width + 4, Gump.theme["buttonFrame"], 1, withTexture=False)
        self.addColorBox(x - 1, y - 1, height + 2, width + 2, Gump.theme["inputFill"], 0.96, withTexture=False)
        for bx, by, bw, bh in [
            (x - 1, y - 1, width + 2, 1),
            (x - 1, y + height, width + 2, 1),
            (x - 1, y, 1, height),
            (x + width, y, 1, height),
        ]:
            border = API.CreateGumpColorBox(1, Gump.theme["frameHighlight"])
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

    def _setBackground(self):
        if not self.bg:
            self.bg = API.CreateGumpColorBox(1, Gump.theme["bgOuter"])
            self.gump.Add(self.bg)
        self.bg.SetWidth(self.width)
        self.bg.SetHeight(self.height)
        self.bg.SetX(0)
        self.bg.SetY(0)
        self._createColorBox(4, 4, self.width - 8, self.height - 8, Gump.theme["frameInner"], 0.92)
        self._createColorBox(6, 6, self.width - 12, self.height - 12, Gump.theme["bgInner"], 0.99)
        self._createColorBox(10, 10, self.width - 20, self.height - 20, Gump.theme["bgInset"], 0.92)
        for x in range(22, self.width - 16, 42):
            self._createColorBox(x, 12, 1, self.height - 24, Gump.theme["grainLine"], 0.018)
        for y in range(36, self.height - 16, 34):
            self._createColorBox(12, y, self.width - 24, 1, Gump.theme["grainLine"], 0.018)

    def _drawStatusArea(self):
        self._statusPanel.extend(self.addDivider(10, self.height - 33, self.width - 20, 0.68))
        bg = self.addColorBox(10, self.height - 30, 20, self.width - 20, Gump.theme["statusBg"], 0.9, withTexture=False)
        self._statusPanel.append(bg)
        self.statusLabel = API.CreateGumpLabel("Ready.", Gump.hues["status"])
        self.statusLabel.SetX(18)
        self.statusLabel.SetY(self.height - 27)
        self.gump.Add(self.statusLabel)

    def _setCornerAccents(self):
        accentColor = Gump.theme["frameHighlight"]
        for x, y, w, h in [
            (8, 8, 26, 2),
            (8, 8, 2, 26),
            (self.width - 34, 8, 26, 2),
            (self.width - 10, 8, 2, 26),
            (8, self.height - 10, 26, 2),
            (8, self.height - 34, 2, 26),
            (self.width - 34, self.height - 10, 26, 2),
            (self.width - 10, self.height - 34, 2, 26),
        ]:
            self._createColorBox(x, y, w, h, accentColor, 0.86)

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
