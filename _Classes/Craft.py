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
        self.isBlocked = False

    def craft(self, isExceptional, bodSkillItem, resourceHue, material):
        if self.isBlocked:
            return None
        item = self.craft_item(
            bodSkillItem,
            resourceHue,
            material,
            require_exceptional=isExceptional,
            recycle_rejected=True,
        )
        if self.isBlocked:
            return None
        return item is not None

    def craft_item(
        self,
        item_def,
        resource_hue,
        material,
        require_exceptional=False,
        recycle_rejected=False,
    ):
        if self._checkResources(item_def, resource_hue) is False:
            return None
        if self._checkTools() is False:
            return None
        if self._useTool() is False:
            return None
        self._selectResource(material)

        before_serials = self._backpack_serials()
        API.ReplyGump(item_def["buttonId"], 460)
        API.Pause(3)

        new_items = self._new_backpack_items(before_serials)
        crafted_item = self._find_crafted_item(item_def, new_items)
        if not crafted_item:
            if new_items:
                return self._stopCrafting(
                    "Crafted unexpected item for {}: {}".format(
                        self._item_name(item_def),
                        ", ".join(self._describeItem(item) for item in new_items),
                    )
                )
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

    def _stopCrafting(self, message, hue=33):
        API.SysMsg(message, hue)
        self.isBlocked = True
        return False

    def _findResourceStack(self, resourceId, container, resourceHue, minAmount=0):
        resourceHue = self._int_value(resourceHue)
        resource = API.FindType(
            resourceId,
            container,
            hue=resourceHue,
            minamount=minAmount,
        )
        if (
            resource
            and resource.Graphic == resourceId
            and resource.Hue == resourceHue
            and resource.Amount >= minAmount
        ):
            return resource
        for item in Util.Util.itemsInContainer(container):
            if item.Graphic != resourceId or item.Hue != resourceHue:
                continue
            if item.Amount >= minAmount:
                return item
        return None

    def _resourceAmount(self, container, resourceId, resourceHue):
        resourceHue = self._int_value(resourceHue)
        total = 0
        for item in Util.Util.itemsInContainer(container):
            if item.Graphic == resourceId and item.Hue == resourceHue:
                total += item.Amount
        return total

    def _waitForResourceAmount(self, container, resourceId, resourceHue, minAmount):
        amount = self._resourceAmount(container, resourceId, resourceHue)
        for _ in range(12):
            if amount >= minAmount:
                return amount
            API.Pause(0.25)
            amount = self._resourceAmount(container, resourceId, resourceHue)
        return amount

    def _itemProps(self, item, attempts=5):
        for _ in range(attempts):
            props = API.ItemNameAndProps(item.Serial, True)
            if props:
                return props.split("\n")
            API.Pause(0.1)
        return []

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
        if buttonId:
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
            resourceHueForItem = self._int_value(resourceHueForItem)
            backpackTargetAmount = resource.get("backpackTargetAmount", 200)
            if backpackTargetAmount is None:
                resourceAmount = resourceMinAmount
            else:
                resourceAmount = max(self._int_value(backpackTargetAmount), resourceMinAmount)

            resourceInBackpack = self._findResourceStack(
                resourceId,
                API.Backpack,
                resourceHueForItem,
                resourceMinAmount,
            )
            if not resourceInBackpack:
                resourceInBackpack = self._findResourceStack(
                    resourceId,
                    API.Backpack,
                    resourceHueForItem,
                    0,
                )

            amountInBackpack = 0
            if resourceInBackpack:
                amountInBackpack = resourceInBackpack.Amount

            targetNeed = max(0, resourceAmount - amountInBackpack)
            requiredNeed = max(0, resourceMinAmount - amountInBackpack)
            if targetNeed:
                resourceInChest = self._findResourceStack(
                    resourceId,
                    self._container_serial(self.resourceChest),
                    resourceHueForItem,
                    targetNeed,
                )
                moveAmount = targetNeed
                if not resourceInChest and requiredNeed:
                    resourceInChest = self._findResourceStack(
                        resourceId,
                        self._container_serial(self.resourceChest),
                        resourceHueForItem,
                        requiredNeed,
                    )
                    if resourceInChest:
                        moveAmount = min(resourceInChest.Amount, targetNeed)
                        moveAmount = max(moveAmount, requiredNeed)
                if not resourceInChest:
                    if requiredNeed:
                        return self._stopCrafting(
                            "Missing resources: graphic {} hue {} amount {}".format(
                                resourceId, resourceHueForItem, requiredNeed
                            )
                        )
                else:
                    if not Util.Util.moveItem(
                        resourceInChest.Serial, API.Backpack, moveAmount
                    ):
                        return self._stopCrafting(
                            "Could not move resources: graphic {} hue {} amount {}".format(
                                resourceId, resourceHueForItem, moveAmount
                            )
                        )
                    amountInBackpack = self._waitForResourceAmount(
                        API.Backpack,
                        resourceId,
                        resourceHueForItem,
                        resourceMinAmount,
                    )
                    if amountInBackpack < resourceMinAmount:
                        return self._stopCrafting(
                            "Missing resources: graphic {} hue {} amount {}".format(
                                resourceId,
                                resourceHueForItem,
                                resourceMinAmount - amountInBackpack,
                            )
                        )
            self.resources.append({"graphic": resourceId, "hue": resourceHueForItem})
        return True

    def _openContainers(self):
        Util.Util.openContainer(API.Backpack)
        if self.resourceChest:
            Util.Util.openContainer(self.resourceChest)

    def _useTool(self):
        toolId = self._tool_graphic()
        tool = API.FindType(toolId, API.Backpack, hue=0)
        if not tool:
            return self._stopCrafting("No tool found!", 32)

        API.UseObject(tool)
        if API.HasGump(460) and not self.hasChangedTool:
            return True

        while not API.HasGump(460):
            API.UseObject(tool)
            API.Pause(0.1)
        self.hasChangedTool = False
        return True

    def _checkTools(self):
        self._openContainers()
        toolId = self._tool_graphic()
        toolButtonId = self.craftingInfo["tool"]["buttonId"]
        tools = len(Util.Util.findTypeAll(API.Backpack, toolId))
        if tools:
            return True

        if self._checkToolsResource() is False:
            return False
        return self._craftTool(toolId, toolButtonId) is not False

    def _craftTool(self, toolId, toolButtonId):
        self._openContainers()
        tinkerTool = API.FindType(0x1EB9, API.Backpack)
        if not tinkerTool:
            return self._stopCrafting("No tinker tool found!", 32)

        API.UseObject(tinkerTool)
        while not API.HasGump(460):
            API.UseObject(tinkerTool)
            API.Pause(0.1)

        API.ReplyGump(toolButtonId, 460)
        API.Pause(3)
        self.hasChangedTool = True
        return True

    def _checkToolsResource(self):
        self._openContainers()
        resourceId = 0x1BF2
        resourceHue = 0x0000
        resourceMinAmount = 20
        resourceAmount = 50

        resourceInBackpack = self._findResourceStack(
            resourceId,
            API.Backpack,
            resourceHue,
            resourceMinAmount,
        )
        if not resourceInBackpack:
            resourceInBackpack = self._findResourceStack(
                resourceId,
                API.Backpack,
                resourceHue,
                0,
            )

        amountInBackpack = 0
        if resourceInBackpack:
            amountInBackpack = resourceInBackpack.Amount

        targetNeed = max(0, resourceAmount - amountInBackpack)
        requiredNeed = max(0, resourceMinAmount - amountInBackpack)
        if targetNeed:
            resourceInChest = self._findResourceStack(
                resourceId,
                self._container_serial(self.resourceChest),
                resourceHue,
                targetNeed,
            )
            moveAmount = targetNeed
            if not resourceInChest and requiredNeed:
                resourceInChest = self._findResourceStack(
                    resourceId,
                    self._container_serial(self.resourceChest),
                    resourceHue,
                    requiredNeed,
                )
                if resourceInChest:
                    moveAmount = min(resourceInChest.Amount, targetNeed)
                    moveAmount = max(moveAmount, requiredNeed)
            if not resourceInChest:
                if requiredNeed:
                    return self._stopCrafting(
                        "Missing tool resources: graphic {} hue {} amount {}".format(
                            resourceId, resourceHue, requiredNeed
                        )
                    )
            else:
                if not Util.Util.moveItem(
                    resourceInChest.Serial, API.Backpack, moveAmount
                ):
                    return self._stopCrafting(
                        "Could not move tool resources: graphic {} hue {} amount {}".format(
                            resourceId, resourceHue, moveAmount
                        )
                    )
                amountInBackpack = self._waitForResourceAmount(
                    API.Backpack,
                    resourceId,
                    resourceHue,
                    resourceMinAmount,
                )
                if amountInBackpack < resourceMinAmount:
                    return self._stopCrafting(
                        "Missing tool resources: graphic {} hue {} amount {}".format(
                            resourceId,
                            resourceHue,
                            resourceMinAmount - amountInBackpack,
                        )
                    )
        return True

    def _new_backpack_items(self, before_serials):
        return [
            item
            for item in self._backpack_items()
            if item.Serial not in before_serials
        ]

    def _find_crafted_item(self, item_def, new_items):
        for item in new_items:
            if self._matches_item_def(item, item_def):
                return item
        return None

    def _describeItem(self, item):
        props = self._itemProps(item)
        name = props[0] if props else "item"
        return "{} graphic {} hue {}".format(
            name,
            getattr(item, "Graphic", None),
            getattr(item, "Hue", None),
        )

    def _matches_item_def(self, item, item_def):
        graphic = item_def.get("graphic")
        if graphic is not None and self._int_value(graphic) != getattr(item, "Graphic", 0):
            return False
        return True

    def _is_exceptional(self, item):
        props = self._itemProps(item)
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
