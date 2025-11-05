#=========== Consolidated Imports ============#
import API


#=========== Start of .\Farm\stone-navrey.py ============#


class NavreyStoneActivator:
    stoneGraphicId = 0x03BF
    stoneHue = -1
    cooldown = 10

    def __init__(self):
        self.rangeMax = 3

    def run(self):
        itemFilter = API.Items.Filter()
        itemFilter.RangeMax = self.rangeMax
        if self.stoneHue != -1:
            itemFilter.Hue = self.stoneHue
        itemFilter.Graphics = [self.stoneGraphicId]

        stones = API.Items.ApplyFilter(itemFilter)

        if len(stones) == 0:
            API.Misc.SendMessage(
                "No Navrey stone found nearby. Check range and graphic ID.", 33
            )
            return

        for stone in stones:
            if stone.ItemID == self.stoneGraphicId:
                API.Items.UseItem(stone.Serial)
                return


NavreyStoneActivator().run()
#=========== End of .\Farm\stone-navrey.py ============#

