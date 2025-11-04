class Item:
    @staticmethod
    def isItemContainer(item):
        isItemContainer = item.Graphic in [3702, 3709, 3649, 3705, 3701]
        return isItemContainer
    
    @staticmethod
    def isRunebookOrAtlas(item):
        isRunebookOrAtlas = item.Graphic in [8901, 39958]
        return isRunebookOrAtlas


    def __init__(self, item):
        self.isContainer = Item.isItemContainer(item)
        self.isRunebook = self._isRunebook(item)
        self.isAtlas = self._isAtlas(item)
        self.item = item

    def recall(self, index):
        if self.isRunebook:
            while not API.HasGump(89):
                API.UseObject(self.item.Serial)
                API.WaitForGump(89)
            API.ReplyGump(75 + index, 89)
        if self.isAtlas:
            while not API.HasGump(498):
                API.UseObject(self.item.Serial)
                API.WaitForGump(498)
            API.ReplyGump(50000 + index, 498)
            API.Pause(0.1)
            API.ReplyGump(4000, 498)
        API.Pause(4)

    def _isRunebook(self, item):
        return item.Graphic == 8901
    
    def _isAtlas(self, item):
        return item.Graphic == 39958
    