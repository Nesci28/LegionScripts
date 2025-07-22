class Item:
    @staticmethod
    def isItemContainer(item):
        isItemContainer = item.Graphic in [3702, 3709, 3649, 3705, 3701]
        return isItemContainer
    
    def __init__(self, item):
        self.isContainer = Item.isItemContainer(item)
        self.item = item