import Util


class Craft:
    def __init__(self, bodSkill, craftingInfo, resourceChest):
        self.bodSkill = bodSkill
        self.craftingInfo = craftingInfo
        self.resourceChest = resourceChest
        self.resources = []
        self.materialSelected = False
        self.hasChangedTool = True

    def craft(self, isExceptional, bodSkillItem, resourceHue, material):
        self._checkResources(bodSkillItem, resourceHue)
        self._checkTools()
        self._useTool()
        self._selectResource(material)
        startingCount = self._checkItems(isExceptional, bodSkillItem)
        itemButtonId = bodSkillItem["buttonId"]
        API.ReplyGump(itemButtonId, 460)
        API.Pause(3)
        endingCount = self._checkItems(isExceptional, bodSkillItem)
        isValid = endingCount - startingCount == 1
        return isValid

    def emptyResource(self):
        for resource in self.resources:
            resourceInBackpack = Util.Util.findTypeWithSpecialHue(
                resourceId=resource["graphic"],
                container=API.Backpack,
                minAmount=0,
                resourceHue=resource["hue"],
            )
            if resourceInBackpack:
                Util.Util.moveItem(resourceInBackpack.Serial, self.resourceChest.Serial)

    def _selectResource(self, material):
        buttonId = material["buttonId"]
        if buttonId and not self.materialSelected:
            API.ReplyGump(buttonId, 460)
            self.materialSelected = True
            API.Pause(1)

    def _checkItems(self, isExceptional, bodSkillItem):
        graphic = bodSkillItem["graphic"]
        items = API.FindTypeAll(graphic, API.Backpack)
        if len(items) == 0:
            return False
        for item in items:
            isNormal = False
            props = API.ItemNameAndProps(item.Serial).split("\n")
            for prop in props:
                if prop == "Normal":
                    isNormal = True
                    break
            if isNormal and isExceptional:
                self._disposeItem(item, bodSkillItem)
        items = API.FindTypeAll(graphic, API.Backpack)
        return len(items)

    def _disposeItem(self, item, bodSkillItem):
        self._openContainers()
        disposeMethod = bodSkillItem["disposeMethod"]
        if disposeMethod == "Trash":
            trash = API.FindType(0x0E77, 4294967295, 2)
            trashContents = Util.Util.getContents(trash)
            while trashContents["items"] == 125:
                API.Pause(1)
                trashContents = Util.Util.getContents(trash)
            Util.Util.moveItem(item.Serial, trash.Serial)
        if disposeMethod == "Salvage Bag":
            salvageBag = API.FindType(0x0E76, API.Backpack, hue=0x024E)
            Util.Util.moveItem(item.Serial, salvageBag.Serial)
            API.ContextMenu(salvageBag.Serial, 910)

    def _checkResources(self, bodSkillItem, resourceHue):
        self._openContainers()
        resources = bodSkillItem["resources"]
        for resource in resources:
            resourceMinAmount = resource["amount"]
            resourceId = resource["graphic"]
            resourceAmount = 200
            resourceInBackpack = Util.Util.findTypeWithSpecialHue(
                resourceId,
                API.Backpack,
                resourceMinAmount,
                resourceHue,
            )
            if not resourceInBackpack:
                resourceInBackpack = Util.Util.findTypeWithSpecialHue(
                    resourceId,
                    API.Backpack,
                    0,
                    resourceHue,
                )
                amountInBackpack = 0
                if resourceInBackpack:
                    amountInBackpack = resourceInBackpack.Amount
                resourceInChest = Util.Util.findTypeWithSpecialHue(
                    resourceId,
                    self.resourceChest,
                    resourceAmount,
                    resourceHue,
                )
                if not resourceInChest:
                    API.SysMsg("Missing resources", 33)
                    API.Stop()
                Util.Util.moveItem(
                    resourceInChest, API.Backpack, resourceAmount - amountInBackpack
                )
                self.resources.append({"graphic": resourceId, "hue": resourceHue})

    def _openContainers(self):
        Util.Util.openContainer(API.Backpack)
        Util.Util.openContainer(self.resourceChest)

    def _useTool(self):
        toolId = self.craftingInfo["tool"]["graphic"]
        tool = API.FindType(toolId, API.Backpack, hue=0)
        API.UseObject(tool)
        if API.HasGump(460) and not self.hasChangedTool:
            return
        if not tool:
            API.SysMsg("No tool found!", 32)
            API.Stop()
        API.UseObject(tool)
        while not API.HasGump(460):
            API.UseObject(tool)
            API.Pause(0.1)
        self.hasChangedTool = False

    def _checkTools(self):
        self._openContainers()
        toolId = self.craftingInfo["tool"]["graphic"]
        toolButtonId = self.craftingInfo["tool"]["buttonId"]
        self._checkToolsResource()
        tinkerTools = len(Util.Util.findTypeAll(API.Backpack, 0x1EB9))
        while tinkerTools < 3:
            self._craftTool(0x1EB9, 11)
            tinkerTools = len(Util.Util.findTypeAll(API.Backpack, 0x1EB9))
        tools = len(Util.Util.findTypeAll(API.Backpack, toolId))
        while tools < 3:
            self._craftTool(0x1EB9, toolButtonId)
            tools = len(Util.Util.findTypeAll(API.Backpack, toolId))

    def _craftTool(self, toolId, toolButtonId):
        self._openContainers()
        tool = API.FindType(toolId, API.Backpack)
        if not tool:
            API.SysMsg("No tool found!", 32)
            API.Stop()
        API.UseObject(tool)
        while not API.HasGump(460):
            API.UseObject(tool)
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
            resourceId, API.Backpack, hue=resourceHue, minamount=resourceMinAmount
        )
        if not resourceInBackpack:
            resourceInBackpack = API.FindType(resourceId, API.Backpack, hue=resourceHue)
            amountInBackpack = 0
            if resourceInBackpack:
                amountInBackpack = resourceInBackpack.Amount
            resourceInChest = API.FindType(
                resourceId,
                self.resourceChest.Serial,
                hue=resourceHue,
                minamount=resourceAmount,
            )
            if not resourceInChest:
                API.SysMsg("Missing resources", 33)
                API.Stop()
            Util.Util.moveItem(
                resourceInChest, API.Backpack, resourceAmount - amountInBackpack
            )
