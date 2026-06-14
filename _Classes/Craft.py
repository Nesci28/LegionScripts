from LegionPath import LegionPath

LegionPath.addSubdirs()

import Util


class Craft:
    def __init__(self, bodSkill, craftingInfo, resourceChest):
        self.bodSkill = bodSkill
        self.craftingInfo = craftingInfo
        self.resourceChest = resourceChest
        self.resources = []
        self.selectedMaterialButton = None
        self.hasChangedTool = True

    def craft(self, isExceptional, bodSkillItem, resourceHue, material):
        item = self.craft_item(
            bodSkillItem,
            resourceHue,
            material,
            require_exceptional=isExceptional,
            recycle_rejected=True,
        )
        return item is not None

    def craft_item(
        self,
        item_def,
        resource_hue,
        material,
        require_exceptional=False,
        recycle_rejected=False,
    ):
        self._checkResources(item_def, resource_hue)
        self._checkTools()
        self._useTool()
        self._selectResource(material)

        before_serials = self._backpack_serials()
        API.ReplyGump(item_def["buttonId"], 460)
        API.Pause(3)

        crafted_item = self._find_crafted_item(item_def, before_serials)
        if not crafted_item:
            API.SysMsg("Crafting did not create {}".format(self._item_name(item_def)), 33)
            return None

        if not self._matches_item_def(crafted_item, item_def):
            API.SysMsg(
                "Crafted item did not match {}".format(self._item_name(item_def)),
                33,
            )
            if recycle_rejected:
                self.dispose_item(crafted_item, item_def)
            return None

        if require_exceptional and not self._is_exceptional(crafted_item):
            if recycle_rejected:
                self.dispose_item(crafted_item, item_def)
            return None

        return crafted_item

    def dispose_item(self, item, item_def):
        if not item:
            return False
        return self._disposeItem(item, item_def)

    def emptyResource(self):
        for resource in self.resources:
            resourceInBackpack = Util.Util.findTypeWithSpecialHue(
                resourceId=resource["graphic"],
                container=API.Backpack,
                minAmount=0,
                resourceHue=resource["hue"],
            )
            if resourceInBackpack:
                Util.Util.moveItem(
                    resourceInBackpack.Serial,
                    self._container_serial(self.resourceChest),
                )

    def _selectResource(self, material):
        buttonId = material.get("buttonId") if material else None
        if buttonId and buttonId != self.selectedMaterialButton:
            API.ReplyGump(buttonId, 460)
            self.selectedMaterialButton = buttonId
            API.Pause(1)

    def _checkItems(self, isExceptional, bodSkillItem):
        graphic = self._int_value(bodSkillItem.get("graphic", 0))
        items = API.FindTypeAll(graphic, API.Backpack)
        if len(items) == 0:
            return False

        count = 0
        for item in items:
            if isExceptional and not self._is_exceptional(item):
                self._disposeItem(item, bodSkillItem)
            else:
                count += 1
        return count

    def _disposeItem(self, item, item_def):
        self._openContainers()
        disposeMethod = item_def.get("disposeMethod", "Salvage Bag")

        if disposeMethod == "Trash":
            trash = API.FindType(0x0E77, 4294967295, 2)
            if not trash:
                API.SysMsg("Trash barrel not found; keeping rejected item.", 33)
                return False
            trashContents = Util.Util.getContents(trash)
            if trashContents and trashContents.get("items") == 125:
                API.SysMsg("Trash barrel is full; keeping rejected item.", 33)
                return False
            Util.Util.moveItem(item.Serial, trash.Serial)
            return True

        if disposeMethod == "Salvage Bag":
            salvageBag = API.FindType(0x0E76, API.Backpack, hue=0x024E)
            if not salvageBag:
                API.SysMsg("Salvage bag not found; keeping rejected item.", 33)
                return False
            Util.Util.moveItem(item.Serial, salvageBag.Serial)
            API.ContextMenu(salvageBag.Serial, 910)
            API.Pause(1)
            return True

        API.SysMsg("Unknown dispose method {}; keeping rejected item.".format(disposeMethod), 33)
        return False

    def _checkResources(self, item_def, resourceHue):
        self._openContainers()
        resources = item_def.get("resources", [])
        for resource in resources:
            resourceMinAmount = resource["amount"]
            resourceId = self._int_value(resource["graphic"])
            resourceHueForItem = resourceHue
            if not resource.get("hasSpecialHue", False):
                resourceHueForItem = 0
            backpackTargetAmount = resource.get("backpackTargetAmount", 200)
            if backpackTargetAmount is None:
                resourceAmount = resourceMinAmount
            else:
                resourceAmount = max(self._int_value(backpackTargetAmount), resourceMinAmount)

            resourceInBackpack = Util.Util.findTypeWithSpecialHue(
                resourceId,
                API.Backpack,
                resourceMinAmount,
                resourceHueForItem,
            )
            if not resourceInBackpack:
                resourceInBackpack = Util.Util.findTypeWithSpecialHue(
                    resourceId,
                    API.Backpack,
                    0,
                    resourceHueForItem,
                )

            amountInBackpack = 0
            if resourceInBackpack:
                amountInBackpack = resourceInBackpack.Amount

            needed = max(0, resourceAmount - amountInBackpack)
            if needed:
                resourceInChest = Util.Util.findTypeWithSpecialHue(
                    resourceId,
                    self._container_serial(self.resourceChest),
                    needed,
                    resourceHueForItem,
                )
                if not resourceInChest:
                    API.SysMsg("Missing resources", 33)
                    API.Stop()
                Util.Util.moveItem(resourceInChest.Serial, API.Backpack, needed)
            self.resources.append({"graphic": resourceId, "hue": resourceHueForItem})

    def _openContainers(self):
        Util.Util.openContainer(API.Backpack)
        if self.resourceChest:
            Util.Util.openContainer(self.resourceChest)

    def _useTool(self):
        toolId = self._tool_graphic()
        tool = API.FindType(toolId, API.Backpack, hue=0)
        if not tool:
            API.SysMsg("No tool found!", 32)
            API.Stop()

        API.UseObject(tool)
        if API.HasGump(460) and not self.hasChangedTool:
            return

        while not API.HasGump(460):
            API.UseObject(tool)
            API.Pause(0.1)
        self.hasChangedTool = False

    def _checkTools(self):
        self._openContainers()
        toolId = self._tool_graphic()
        toolButtonId = self.craftingInfo["tool"]["buttonId"]
        self._checkToolsResource()
        tools = len(Util.Util.findTypeAll(API.Backpack, toolId))
        while tools < 3:
            self._craftTool(toolId, toolButtonId)
            tools = len(Util.Util.findTypeAll(API.Backpack, toolId))

    def _craftTool(self, toolId, toolButtonId):
        self._openContainers()
        tinkerTool = API.FindType(0x1EB9, API.Backpack)
        if not tinkerTool:
            API.SysMsg("No tinker tool found!", 32)
            API.Stop()

        API.UseObject(tinkerTool)
        while not API.HasGump(460):
            API.UseObject(tinkerTool)
            API.Pause(0.1)

        API.ReplyGump(toolButtonId, 460)
        API.Pause(3)
        self.hasChangedTool = True

    def _checkToolsResource(self):
        self._openContainers()
        resourceId = 0x1BF2
        resourceHue = 0x0000
        resourceMinAmount = 20
        resourceAmount = 50

        resourceInBackpack = API.FindType(
            resourceId,
            API.Backpack,
            hue=resourceHue,
            minamount=resourceMinAmount,
        )
        if not resourceInBackpack:
            resourceInBackpack = API.FindType(resourceId, API.Backpack, hue=resourceHue)

        amountInBackpack = 0
        if resourceInBackpack:
            amountInBackpack = resourceInBackpack.Amount

        needed = max(0, resourceAmount - amountInBackpack)
        if needed:
            resourceInChest = API.FindType(
                resourceId,
                self._container_serial(self.resourceChest),
                hue=resourceHue,
                minamount=needed,
            )
            if not resourceInChest:
                API.SysMsg("Missing resources", 33)
                API.Stop()
            Util.Util.moveItem(resourceInChest.Serial, API.Backpack, needed)

    def _find_crafted_item(self, item_def, before_serials):
        for item in self._backpack_items():
            if item.Serial in before_serials:
                continue
            if self._matches_item_def(item, item_def):
                return item

        for item in self._backpack_items():
            if item.Serial not in before_serials:
                return item
        return None

    def _matches_item_def(self, item, item_def):
        graphic = item_def.get("graphic")
        if graphic is not None and self._int_value(graphic) != getattr(item, "Graphic", 0):
            return False

        expected_name = item_def.get("name")
        if expected_name:
            props = API.ItemNameAndProps(item.Serial, True).split("\n")
            if not props or expected_name.lower() not in props[0].lower():
                return False
        return True

    def _is_exceptional(self, item):
        props = API.ItemNameAndProps(item.Serial, True).split("\n")
        return any("exceptional" in prop.lower() for prop in props)

    def _backpack_items(self):
        try:
            return API.ItemsInContainer(API.Backpack, False) or []
        except Exception:
            return []

    def _backpack_serials(self):
        return set(item.Serial for item in self._backpack_items())

    def _tool_graphic(self):
        tool = self.craftingInfo["tool"]
        return self._int_value(tool.get("graphic", tool.get("id")))

    def _container_serial(self, container):
        return getattr(container, "Serial", container)

    def _item_name(self, item_def):
        return item_def.get("name") or str(item_def.get("graphic", "item"))

    def _int_value(self, value):
        if isinstance(value, str):
            if value.lower().startswith("0x"):
                return int(value, 16)
            return int(value)
        return int(value)
