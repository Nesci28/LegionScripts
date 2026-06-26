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
    def __init__(self, nativeRadio, fills, elements=None):
        self.nativeRadio = nativeRadio
        self.fills = fills
        self.elements = elements or [nativeRadio] + list(fills)

    @property
    def IsChecked(self):
        return self.nativeRadio.IsChecked

    @IsChecked.setter
    def IsChecked(self, value):
        self.nativeRadio.IsChecked = value
        for fill in self.fills:
            fill.IsVisible = value

    @property
    def IsVisible(self):
        return any(getattr(element, "IsVisible", False) for element in self.elements)

    @IsVisible.setter
    def IsVisible(self, value):
        for element in self.elements:
            try:
                element.IsVisible = value
            except Exception:
                pass


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

    def __init__(
        self, width, height, onCloseCb=None, withStatus=True, gumpId=None, keepOpen=False
    ):
        self.width = width
        self.height = height
        self.onCloseCb = onCloseCb
        self.withStatus = withStatus
        self.gumpId = gumpId
        self.keepOpen = keepOpen

        self.gump = self._createNativeGump()
        self._applyGumpId()
        self.subGumps = []
        self._subGumpStates = {}
        self._lastGroupMainPosition = None
        self._controls = []
        self._destroying = False
        self.bg = None
        self._running = True
        self.buttons = []
        self.hoverControls = []
        self.skillTextBoxes = []
        self.pendingCallbacks = []
        self.tabGumps = {}
        self.tabButtons = {}
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
        self._rememberGroupPositions()

    def _applyGumpId(self):
        if self.gumpId is None:
            return
        for attr in ["ID", "LocalSerial", "ServerSerial"]:
            try:
                setattr(self.gump, attr, self.gumpId)
            except:
                pass

    def _createNativeGump(self):
        try:
            return API.CreateGump(True, True, self.keepOpen, self.gumpId or 0)
        except:
            try:
                return API.CreateGump(True, True, self.keepOpen)
            except:
                return API.CreateGump(True, True)

    def _addToGump(self, control):
        if control is None:
            return control
        if not any(existing is control for existing in self._controls):
            self._controls.append(control)
        self.gump.Add(control)
        return control

    def _bindSubGumpCloseHandler(self, subGump):
        def onDisposed():
            state = self._subGumpStates.get(subGump)
            if state is None or self._destroying or not self._running:
                return
            state["needsRestore"] = True
            subGump._running = True

        try:
            API.AddControlOnDisposed(subGump.gump, onDisposed)
            return
        except:
            pass
        try:
            API.Gumps.AddControlOnDisposed(subGump.gump, onDisposed)
        except:
            pass

    def _isDisposed(self, nativeGump):
        try:
            return nativeGump.IsDisposed
        except:
            return True

    def _isVisible(self, nativeGump):
        try:
            return nativeGump.IsVisible
        except:
            return True

    def _getGumpPosition(self, nativeGump):
        try:
            return nativeGump.GetX(), nativeGump.GetY()
        except:
            return 0, 0

    def _setGumpPosition(self, nativeGump, x, y):
        try:
            nativeGump.SetPos(x, y)
            return
        except:
            pass
        nativeGump.SetX(x)
        nativeGump.SetY(y)

    def _subGumpOffset(self, width, height, position):
        if position == "bottom":
            return 0, self.height
        if position == "top":
            return 0, -height
        if position == "center":
            return self.width // 2 - width // 2, self.height // 2 - height // 2
        if position == "left":
            return -width, 0
        if position == "right":
            return self.width, 0
        return 0, 0

    def _subGumpPositionFromMain(self, mainX, mainY, width, height, position):
        offsetX, offsetY = self._subGumpOffset(width, height, position)
        return mainX + offsetX, mainY + offsetY

    def _mainPositionFromSubGump(self, subX, subY, width, height, position):
        offsetX, offsetY = self._subGumpOffset(width, height, position)
        return subX - offsetX, subY - offsetY

    def _rememberGroupPositions(self):
        if self._isDisposed(self.gump):
            return
        self._lastGroupMainPosition = self._getGumpPosition(self.gump)
        for subGump, _, alwaysVisible in self.subGumps:
            state = self._subGumpStates.get(subGump)
            if not state:
                continue
            if subGump._running and not self._isDisposed(subGump.gump):
                state["lastPosition"] = self._getGumpPosition(subGump.gump)
                state["visible"] = True if alwaysVisible else self._isVisible(subGump.gump)

    def _groupMainPositionFromMovedGump(self):
        if self._isDisposed(self.gump):
            return None

        mainPosition = self._getGumpPosition(self.gump)
        if self._lastGroupMainPosition is None or mainPosition != self._lastGroupMainPosition:
            return mainPosition

        for subGump, position, _ in self.subGumps:
            state = self._subGumpStates.get(subGump)
            if not state or not subGump._running or self._isDisposed(subGump.gump):
                continue
            if not self._isVisible(subGump.gump):
                continue

            subPosition = self._getGumpPosition(subGump.gump)
            if state.get("lastPosition") and subPosition != state["lastPosition"]:
                return self._mainPositionFromSubGump(
                    subPosition[0],
                    subPosition[1],
                    subGump.width,
                    subGump.height,
                    position,
                )

        return mainPosition

    def _restoreSubGump(self, subGump, position, alwaysVisible, x, y):
        state = self._subGumpStates.get(subGump, {})
        visible = True if alwaysVisible else state.get("visible", True)
        state["needsRestore"] = False
        subGump._running = True

        try:
            subGump.gump = subGump._createNativeGump()
            subGump._applyGumpId()
            subGump.gump.SetWidth(subGump.width)
            subGump.gump.SetHeight(subGump.height)
            self._setGumpPosition(subGump.gump, x, y)
            for control in getattr(subGump, "_controls", []):
                try:
                    subGump.gump.Add(control)
                except:
                    pass
            subGump.gump.IsVisible = visible
            self._bindSubGumpCloseHandler(subGump)
            API.AddGump(subGump.gump)
            subGump.gump.IsVisible = visible
        except Exception as e:
            API.SysMsg(f"Sub-gump restore failed: {e}", 33)
            return False

        return not self._isDisposed(subGump.gump)

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
            if self.skillTextBoxes:
                self.checkValidateForm()
            self._checkEvents()
            if self.hoverControls:
                self._updateHoverControls()
            self._lastCheckTime = now

    def tickSubGumps(self):
        if not self._running or self._isDisposed(self.gump):
            return

        mainX, mainY = self._groupMainPositionFromMovedGump()
        self._setGumpPosition(self.gump, mainX, mainY)

        for subGump, position, alwaysVisible in self.subGumps:
            state = self._subGumpStates.get(subGump)
            needsRestore = bool(state and state.get("needsRestore"))
            isDisposed = self._isDisposed(subGump.gump)
            shouldBeVisible = True if alwaysVisible else bool(state and state.get("visible"))
            isHiddenClosed = shouldBeVisible and not isDisposed and not self._isVisible(subGump.gump)

            if not subGump._running and not (needsRestore or isDisposed or isHiddenClosed):
                continue

            x, y = self._subGumpPositionFromMain(
                mainX, mainY, subGump.width, subGump.height, position
            )

            if needsRestore or isDisposed:
                if not self._restoreSubGump(subGump, position, alwaysVisible, x, y):
                    continue
            else:
                self._setGumpPosition(subGump.gump, x, y)
                if isHiddenClosed:
                    subGump.gump.IsVisible = True

            if state is not None:
                state["lastPosition"] = (x, y)
                state["visible"] = True if alwaysVisible else self._isVisible(subGump.gump)
                state["needsRestore"] = False

        self._lastGroupMainPosition = (mainX, mainY)

    def destroy(self):
        if not self._running:
            return
        self._destroying = True
        self._running = False
        for subGump, _, _ in self.subGumps:
            subGump.destroy()
        self._subGumpStates = {}
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
        gump = Gump(width, height, withStatus=withStatus, keepOpen=True)
        self._setSubGumpPosition(gump.gump, width, height, position)
        API.AddGump(gump.gump)
        self.subGumps.append((gump, position, alwaysVisible))
        self._subGumpStates[gump] = {
            "lastPosition": self._getGumpPosition(gump.gump),
            "visible": True,
            "needsRestore": False,
        }
        self._bindSubGumpCloseHandler(gump)
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
        for tabName, tabButton in self.tabButtons.items():
            isActive = tabName == name
            for element in tabButton.get("active", []):
                try:
                    element.IsVisible = isActive
                except Exception:
                    pass
        for subGumps, _, alwaysVisible in self.subGumps:
            if not alwaysVisible:
                subGumps.gump.IsVisible = False
                state = self._subGumpStates.get(subGumps)
                if state is not None:
                    state["visible"] = False
        tabGump = self.tabGumps[name]
        tabGump.gump.IsVisible = True
        state = self._subGumpStates.get(tabGump)
        if state is not None:
            state["visible"] = True



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
        container=None,
    ):
        colorBox = self._createColorBox(x, y, width, height, colorHex, opacity, container)
        if withTexture and width > 20 and height > 8:
            self._createColorBox(x + 1, y + 1, width - 2, 1, "#ffffff", 0.06, container)
            self._createColorBox(x + 1, y + height - 2, width - 2, 1, "#000000", 0.25, container)
        return colorBox

    def addCheckbox(self, label, x, y, isChecked, callback, hue=None):
        if hue is None:
            hue = Gump.hues["text"]
        checkbox = API.CreateGumpCheckbox(label, hue, isChecked)
        checkbox.SetX(x)
        checkbox.SetY(y)
        if callback:
            API.AddControlOnClick(checkbox, callback)
        self._addToGump(checkbox)
        return checkbox

    def addRadio(
        self,
        label,
        x,
        y,
        group,
        isChecked,
        callback,
        hue=None,
        labelYOffset=0,
        boxYOffset=2,
        boxSize=14,
        labelGap=22,
        hitWidth=18,
        hitHeight=18,
        fillColor="#76c84a",
    ):
        if hue is None:
            hue = Gump.hues["text"]
        radio = API.CreateGumpRadioButton("", group, 9020, 9021, hue, isChecked)
        radio.SetX(x)
        radio.SetY(y)
        radio.IsVisible = False
        if callback:
            API.AddControlOnClick(radio, callback)

        elements = [radio]
        boxY = y + boxYOffset
        box = self.addColorBox(x, boxY, boxSize, boxSize, Gump.theme["buttonFrame"], 1)
        innerMargin = 2 if boxSize <= 14 else 3
        innerSize = max(2, boxSize - innerMargin * 2)
        inner = self.addColorBox(
            x + innerMargin,
            boxY + innerMargin,
            innerSize,
            innerSize,
            Gump.theme.get("inputFill", "#111b20"),
            0.98,
        )
        fillMargin = 4 if boxSize <= 14 else 5
        fillSize = max(2, boxSize - fillMargin * 2)
        fill = self.addColorBox(x + fillMargin, boxY + fillMargin, fillSize, fillSize, fillColor, 0.98)
        fill.IsVisible = isChecked
        elements.extend([box, inner, fill])

        self._addToGump(radio)
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(hitWidth)
        hitTarget.SetHeight(hitHeight)
        if callback:
            API.AddControlOnClick(hitTarget, callback)
        self._addToGump(hitTarget)
        elements.append(hitTarget)

        labelObj = self.addLabel(label, x + labelGap, y + labelYOffset, hue)
        if callback:
            API.AddControlOnClick(labelObj, callback)
        elements.append(labelObj)
        return GumpRadio(radio, [fill], elements)

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
        self._addToGump(btn)

        if label:
            if type == "default":
                color = Gump.theme["buttonText"]
                if isDarkMode:
                    color = Gump.theme["buttonTextDark"]
                labelObj = self.addTtfLabel(label, x, y, width, height, fontSize, color, "center", None)
                self.hoverControls.append({"targets": [btn, labelObj], "hover": hover})
                self._addToGump(btn)
            else:
                labelObj = API.CreateGumpLabel(label, Gump.hues["text"])
                labelObj.SetY(y)
                labelObj.SetX(x + 24)
                if callback:
                    API.AddControlOnClick(labelObj, callback)
                self._addToGump(labelObj)
        elif type == "default":
            self.hoverControls.append({"targets": [btn], "hover": hover})
            self._addToGump(btn)
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
        self._addToGump(hitTarget)
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
        self, label, x, y, width, height, fontSize, fontColorHex, position, callback, container=None
    ):
        ttfLabel = API.CreateGumpTTFLabel(
            label, fontSize, fontColorHex, maxWidth=width, aligned=position, applyStroke=True
        )
        centerY = y + max(0, int((height - fontSize) / 2))
        ttfLabel.SetX(x)
        ttfLabel.SetY(centerY)
        if callback:
            API.AddControlOnClick(ttfLabel, callback)
        if container is not None:
            container.Add(ttfLabel)
        else:
            self._addToGump(ttfLabel)
        return ttfLabel

    def createLabel(self, text, hue=None):
        if hue is None:
            hue = Gump.hues["text"]
        return API.CreateGumpLabel(text, hue)

    def addLabel(self, text, x, y, hue=None, container=None):
        label = self.createLabel(text, hue)
        label.SetX(x)
        label.SetY(y)
        if container is not None:
            container.Add(label)
        else:
            self._addToGump(label)
        return label

    def createNativeButton(self, label, normal, pressed=None, hover=None, hue=996):
        if pressed is None:
            pressed = normal
        if hover is None:
            hover = pressed
        return API.CreateGumpButton(label, hue, normal, pressed, hover)

    def addNativeButton(
        self,
        label,
        x,
        y,
        normal,
        pressed=None,
        hover=None,
        hue=996,
        callback=None,
        container=None,
        width=None,
        height=None,
    ):
        button = self.createNativeButton(label, normal, pressed, hover, hue)
        button.SetX(x)
        button.SetY(y)
        if width is not None:
            button.SetWidth(width)
        if height is not None:
            button.SetHeight(height)
        if callback:
            API.AddControlOnClick(button, callback)
        if container is not None:
            container.Add(button)
        else:
            self._addToGump(button)
        return button

    def addScrollArea(self, x, y, width, height):
        scrollArea = API.CreateGumpScrollArea(x, y, width, height)
        self._addToGump(scrollArea)
        return scrollArea

    def addItemPic(self, itemId, x, y, width, height, container=None):
        itemPic = API.CreateGumpItemPic(itemId, width, height)
        itemPic.SetX(x)
        itemPic.SetY(y)
        if container is not None:
            container.Add(itemPic)
        else:
            self._addToGump(itemPic)
        return itemPic

    def addFlatRow(self, x, y, width, height=20, selected=False, container=None):
        color = Gump.theme["selectedRow"] if selected else Gump.theme["row"]
        row = self.addColorBox(x, y, height, width, color, 0.42, withTexture=False, container=container)
        line = self.addColorBox(x, y + height - 1, 1, width, "#000000", 0.32, withTexture=False, container=container)
        return {"row": row, "line": line, "elements": [row, line]}

    def addTextButton(self, text, x, y, width, height=24, callback=None, fontSize=11, isDarkMode=False):
        topHeight = max(1, int((height - 6) / 2))
        textColor = Gump.theme["buttonTextDark"] if isDarkMode else Gump.theme["buttonText"]
        parts = [
            self.addColorBox(x + 2, y + 4, height - 2, width, Gump.theme["buttonShadow"], 0.55, withTexture=False),
            self.addColorBox(x, y, height, width, Gump.theme["buttonFrame"], 1, withTexture=False),
            self.addColorBox(x + 1, y + 1, height - 2, width - 2, Gump.theme["buttonInset"], 1, withTexture=False),
            self.addColorBox(x + 3, y + 3, topHeight, width - 6, Gump.theme["buttonHighlight"], 0.76, withTexture=True),
            self.addColorBox(x + 3, y + 3 + topHeight, max(1, height - 6 - topHeight), width - 6, Gump.theme["buttonFill"], 0.94, withTexture=True),
            self.addColorBox(x + 2, y + 2, 1, width - 4, "#ffffff", 0.12, withTexture=False),
            self.addColorBox(x + 2, y + height - 2, 1, width - 4, "#000000", 0.58, withTexture=False),
        ]
        hover = self.addColorBox(x + 2, y + 2, height - 4, width - 4, Gump.theme["frameHighlight"], 0.16, withTexture=False)
        hover.IsVisible = False
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(width)
        hitTarget.SetHeight(height)
        if callback:
            API.AddControlOnClick(hitTarget, callback)
        self._addToGump(hitTarget)
        label = self.addTtfLabel(text, x, y, width, height, fontSize, textColor, "center", callback)
        self.hoverControls.append({"targets": [hitTarget, label], "hover": hover})
        return {
            "parts": parts,
            "hover": hover,
            "hitTarget": hitTarget,
            "label": label,
            "button": hitTarget,
            "elements": parts + [hover, hitTarget, label],
        }

    def addGemDot(self, x, y, color, callback=None):
        parts = [
            self.addColorBox(x + 5, y, 4, 8, "#d7f2ff", 0.62, withTexture=False),
            self.addColorBox(x + 2, y + 3, 10, 14, color, 0.98, withTexture=False),
            self.addColorBox(x + 5, y + 6, 8, 8, "#f5fbff", 0.28, withTexture=False),
            self.addColorBox(x + 7, y + 2, 3, 4, "#ffffff", 0.68, withTexture=False),
        ]
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(20)
        hitTarget.SetHeight(20)
        if callback:
            API.AddControlOnClick(hitTarget, callback)
        self._addToGump(hitTarget)
        return {"parts": parts, "hitTarget": hitTarget, "elements": parts + [hitTarget]}

    def addSectionTitle(self, number, title, x, y, width, hue=None):
        if hue is None:
            hue = Gump.hues["text"]
        elements = [
            self.addColorBox(x, y, 26, 26, Gump.theme["panelOuter"], 1, withTexture=False),
            self.addColorBox(x + 2, y + 2, 22, 22, Gump.theme["sectionBadge"], 0.98, withTexture=False),
            self.addColorBox(x + 5, y + 5, 16, 16, Gump.theme["frameInner"], 0.86, withTexture=False),
            self.addColorBox(x + 8, y + 8, 10, 10, Gump.theme["bgOuter"], 0.98, withTexture=False),
            self.addColorBox(x + 34, y + 20, 1, max(1, width - 34), Gump.theme["panelHeaderLine"], 0.55, withTexture=False),
        ]
        numberLabel = None
        if number:
            numberLabel = self.addLabel(number, x + 9, y + 5, hue)
            elements.append(numberLabel)
        titleLabel = self.addLabel(title, x + 34, y + 3, hue)
        elements.append(titleLabel)
        return {"number": numberLabel, "title": titleLabel, "elements": elements}

    def addSectionPanel(self, number, title, x, y, width, height, titleHue=None, withTexture=True):
        panel = self.addPanel(x, y, width, height, None, titleHue, withTexture)
        titleControl = self.addSectionTitle(str(number) if number is not None else "", title, x + 8, y + 10, width - 16, titleHue)
        panel["sectionTitle"] = titleControl
        panel["elements"].extend(titleControl["elements"])
        return panel

    def addSettingAction(self, text, x, y, callback=None, width=286):
        button = self.addButton("", x, y, "radioBlue", callback)
        label = self.addLabel(text, x + 28, y + 2, Gump.hues["text"])
        hitTarget = API.CreateGumpColorBox(0.01, "#000000")
        hitTarget.SetX(x)
        hitTarget.SetY(y)
        hitTarget.SetWidth(width)
        hitTarget.SetHeight(22)
        if callback:
            API.AddControlOnClick(hitTarget, callback)
        self._addToGump(hitTarget)
        return {"button": button, "label": label, "hitTarget": hitTarget, "elements": [button, label, hitTarget]}


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
        if container is not None:
            container.Add(colorBox)
        else:
            self._addToGump(colorBox)
        return colorBox



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
            self._addToGump(border)
            borders.append(border)
        return borders


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
        tabStyle="icon",
    ):
        y = 12 + len(self.tabGumps) * yOffset
        x = 11

        def onClick():
            self.setActiveTab(name)
            if callback:
                callback()

        if tabStyle == "list":
            row_width = max(62, self.width - 22)
            slot = [
                self.addColorBox(x, y + 44, 1, row_width, Gump.theme["grainLine"], 0.16, withTexture=False),
                self.addColorBox(x, y + 5, 22, row_width, Gump.theme["row"], 0.24, withTexture=False),
            ]
            active = [
                self.addColorBox(x, y + 3, 38, row_width, Gump.theme["selectedRow"], 0.86, withTexture=True),
                self.addColorBox(x, y + 3, 38, 3, Gump.theme["frameHighlight"], 0.95, withTexture=False),
                self.addColorBox(x + 3, y + 4, 1, row_width - 6, Gump.theme["frameHighlight"], 0.32, withTexture=False),
                self.addColorBox(x + 3, y + 40, 1, row_width - 6, Gump.theme["frameHighlight"], 0.28, withTexture=False),
            ]
            for element in active:
                element.IsVisible = False
            display_text = label or name
            text = self.addTtfLabel(
                display_text.upper(),
                x + 2,
                y + 3,
                row_width - 4,
                36,
                12,
                Gump.theme["buttonText"],
                "center",
                self.onClick(onClick),
            )
            hitTarget = API.CreateGumpColorBox(0.01, "#000000")
            hitTarget.SetX(x)
            hitTarget.SetY(y)
            hitTarget.SetWidth(row_width)
            hitTarget.SetHeight(45)
            API.AddControlOnClick(hitTarget, self.onClick(onClick))
            self._addToGump(hitTarget)
            self.buttons.append({"slot": slot, "button": hitTarget, "label": text, "active": active})
        else:
            slot = [
                self.addColorBox(x - 4, y - 4, 60, 58, Gump.theme["frameOuter"], 1, withTexture=False),
                self.addColorBox(x - 2, y - 2, 56, 54, Gump.theme["frameInner"], 0.95, withTexture=False),
                self.addColorBox(x, y, 52, 50, Gump.theme["bgInset"], 0.96, withTexture=True),
            ]
            btn = self.addButton(label, x + 6, y + 6, iconType, self.onClick(onClick), isDarkMode)
            self.buttons.append({"slot": slot, "button": btn})
        tabGump = self.createSubGump(gumpWidth, self.height, "right", withStatus, False)
        tabGump.gump.IsVisible = False
        state = self._subGumpStates.get(tabGump)
        if state is not None:
            state["visible"] = False
        self.tabGumps[name] = tabGump
        self.tabButtons[name] = self.buttons[-1]
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
            self._addToGump(border)
            borders.append(border)
        textbox = API.CreateGumpTextBox(str(clampedValue), width, height, False)
        textbox.SetX(x)
        textbox.SetY(y)
        self._addToGump(textbox)
        self.skillTextBoxes.append((textbox, minValue, maxValue, borders))
        return textbox

    def _setBackground(self):
        if not self.bg:
            self.bg = API.CreateGumpColorBox(1, Gump.theme["bgOuter"])
            self._addToGump(self.bg)
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
        self._addToGump(self.statusLabel)

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
        x, y = self._subGumpPositionFromMain(gx, gy, width, height, position)
        self._setGumpPosition(gump, x, y)
