class GumpControlMixin(object):
    def _callback(self, fn):
        return self.gump.onClick(lambda: self._run_action(fn))

    def _set_status(self, text):
        if not self.gump:
            return
        self.gump.setStatus(text)
        for tabGump in self.gump.tabGumps.values():
            tabGump.setStatus(text)

    def _ui_gump(self):
        return self._drawGump or self.gump

    def _resize(self, width, height):
        try:
            self.gump.gump.SetWidth(width)
            self.gump.gump.SetHeight(height)
        except Exception:
            pass

    def _remember(self, obj, group):
        controls = list(self._iter_controls(obj))
        if group == "main":
            self.mainControls.extend(controls)
        if group == "picker":
            self.pickerControls.extend(controls)
        return obj

    def _iter_controls(self, obj):
        if obj is None:
            return
        if isinstance(obj, dict):
            for value in obj.values():
                for control in self._iter_controls(value):
                    yield control
            return
        if isinstance(obj, (list, tuple)):
            for value in obj:
                for control in self._iter_controls(value):
                    yield control
            return
        if hasattr(obj, "IsVisible"):
            yield obj

    def _set_visible(self, obj, visible):
        for control in self._iter_controls(obj):
            try:
                control.IsVisible = visible
            except Exception:
                pass

    def _set_text(self, control, text):
        if not control:
            return
        text = str(text)
        try:
            if hasattr(control, "SetText"):
                control.SetText(text)
            else:
                control.Text = text
        except Exception:
            try:
                control.Text = text
            except Exception:
                pass

    def _set_hue(self, control, hue):
        if not control:
            return
        try:
            control.Hue = hue
        except Exception:
            pass

    def _set_checked(self, control, checked):
        if not control:
            return
        try:
            if hasattr(control, "SetIsChecked"):
                control.SetIsChecked(checked)
            else:
                control.IsChecked = checked
        except Exception:
            try:
                control.IsChecked = checked
            except Exception:
                pass

    def _set_input_text(self, control, text):
        self._set_text(control, text)

    def _addLabel(self, text, x, y, hue=None, group="main"):
        return self._remember(self._ui_gump().addLabel(text, x, y, hue), group)

    def _addBoundedLabel(self, text, x, y, width, height=16, fontSize=9, color=None, group="main", align="left"):
        if color is None:
            color = self.Gump.theme["buttonText"]
        control = self._ui_gump().addTtfLabel(str(text), x, y, width, height, fontSize, color, align, None)
        return self._remember(control, group) if group else control

    def _truncate_text(self, text, max_chars):
        text = str(text or "")
        if len(text) <= max_chars:
            return text
        if max_chars <= 3:
            return text[:max_chars]
        return text[:max_chars - 3].rstrip() + "..."

    def _addPanel(self, x, y, width, height, title=None, group="main"):
        ui = self._ui_gump()
        panel = ui.addSectionPanel("", title, x, y, width, height) if title else ui.addPanel(x, y, width, height, None, withTexture=True)
        self._remember(panel["elements"], group)
        return panel

    def _addSectionPanel(self, number, title, x, y, width, height, group="main"):
        panel = self._ui_gump().addSectionPanel(number, title, x, y, width, height)
        self._remember(panel["elements"], group)
        return panel

    def _addSectionTitle(self, number, title, x, y, width, group="main"):
        control = self._ui_gump().addSectionTitle(number, title, x, y, width)
        self._remember(control, group)
        return control

    def _addFlatRow(self, x, y, width, height, group="main"):
        control = self._ui_gump().addFlatRow(x, y, width, height)
        return self._remember(control, group) if group else control

    def _addButton(self, text, x, y, width, height=24, callback=None, fontSize=11, group="main"):
        cb = self._callback(callback) if callback else None
        control = self._ui_gump().addTextButton(text, x, y, width, height, cb, fontSize)
        return self._remember(control, group) if group else control

    def _addGemDot(self, x, y, color, group="main", callback=None):
        cb = self._callback(callback) if callback else None
        control = self._ui_gump().addGemDot(x, y, color, cb)
        return self._remember(control, group) if group else control

    def _addInput(self, defaultValue, x, y, minValue=0, maxValue=120, width=60, height=24, group="main"):
        control = self._ui_gump().addSkillTextBox(defaultValue, x, y, minValue, maxValue, width, height)
        return self._remember(control, group) if group else control

    def _addRadio(self, label, x, y, isChecked, callback, hue=None, group="main", hitWidth=110):
        cb = self._callback(callback) if callback else None
        control = self._ui_gump().addRadio(
            label,
            x,
            y,
            6200,
            isChecked,
            cb,
            hue,
            labelYOffset=3,
            boxYOffset=2,
            boxSize=18,
            labelGap=28,
            hitWidth=hitWidth,
            hitHeight=22,
            fillColor="#69be37",
        )
        return self._remember(control, group) if group else control

    def _addReadOnlyRadio(self, label, x, y, isChecked, hue=None, group="main"):
        if hue is None:
            hue = self.Gump.hues["muted"]
        control = self._ui_gump().addRadio(
            label,
            x,
            y,
            6201,
            isChecked,
            None,
            hue,
            labelYOffset=3,
            boxYOffset=2,
            boxSize=18,
            labelGap=28,
            hitWidth=110,
            hitHeight=22,
            fillColor="#69be37",
        )
        return self._remember(control, group) if group else control

    def _addNativeCircleButton(self, button_type, x, y, callback=None, group="main"):
        cb = self._callback(callback) if callback else None
        button = self._ui_gump().addButton("", x, y, button_type, cb)
        return self._remember(button, group) if group else button

    def _addMaxButton(self, x, y, callback, group="main"):
        return self._addNativeCircleButton("radioGreen", x, y, callback, group)

    def _addSettingAction(self, text, x, y, callback, group="main", width=286):
        cb = self._callback(callback) if callback else None
        control = self._ui_gump().addSettingAction(text, x, y, cb, width)
        return self._remember(control, group) if group else control
