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

    def _isRunebook(self, item):
        return item.Graphic == 8901
    
    def _isAtlas(self, item):
        return item.Graphic == 39958