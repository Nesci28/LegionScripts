import API
import importlib
import sys

sys.path.append(r".\\TazUO\\LegionScripts\\_Classes")
sys.path.append(r".\\TazUO\\LegionScripts\\_Utils")

import Util
import Refinement
import Amalgator

importlib.reload(Util)
importlib.reload(Refinement)
importlib.reload(Amalgator)

from Amalgator import Amalgator
from Util import Util
from Refinement import Refinement


class RefinementManager:
    def __init__(self):
        self.containerSerials = {
            1: 0x43287397,
            2: 0x4336E8C3,
            3: 0x43AF8ED0,
            4: 0x437B1DAB,
            5: 0x469FA248,
        }

    def main(self):
        self._moveBackpackToContainers()
        for level in range(1, 6):
            if level != 5:
                self._mergeInUsedAmalgator(level)
            self._moveBackpackToContainers()
            if level != 5:
                self._mergeInNewAmalgator(level)
            self._moveBackpackToContainers()

    def _moveBackpackToContainers(self):
        refinements = []
        amalgators = []
        items = Util.itemsInContainer(API.Backpack)

        for item in items:
            if Refinement.isItemRefinement(item):
                r = Refinement(item)
                refinements.append(r)
            elif Amalgator.isItemAmalgator(item):
                a = Amalgator(item)
                amalgators.append(a)

        for refinement in refinements:
            if refinement.level in self.containerSerials:
                container = self.containerSerials[refinement.level]
                Util.moveItem(refinement.item.Serial, container)

        for amalgator in amalgators:
            targetLevel = amalgator.level if not amalgator.isEmpty else 5
            if targetLevel in self.containerSerials:
                container = self.containerSerials[targetLevel]
                Util.moveItem(amalgator.item.Serial, container)

    def _isCompatibleAmalgator(self, refinement, amalgator):
        return (
            refinement.type == amalgator.type
            and refinement.level == amalgator.level
            and refinement.armorType == amalgator.armorType
        )

    def _isCompatibleHash(self, refinement, hashStr):
        type, level, armorType = hashStr.split("-")
        return (
            refinement.type == type
            and refinement.level == int(level)
            and refinement.armorType == armorType
        )

    def _getRefinements(self, containerSerial):
        refinements = []
        items = Util.itemsInContainer(containerSerial)
        for item in items:
            if Refinement.isItemRefinement(item):
                refinement = Refinement(item)
                refinements.append(refinement)
        return refinements

    def _getAmalgators(self, containerSerial, isEmpty):
        amalgators = []
        for item in Util.itemsInContainer(containerSerial):
            if Amalgator.isItemAmalgator(item):
                a = Amalgator(item)
                if a.isEmpty == isEmpty:
                    amalgators.append(a)
        return amalgators

    def _mergeInUsedAmalgator(self, level):
        if level not in self.containerSerials:
            return
        containerSerial = self.containerSerials[level]
        Util.openContainer(API.FindItem(containerSerial))

        refinements = self._getRefinements(containerSerial)
        amalgators = self._getAmalgators(containerSerial, isEmpty=False)

        for refinement in refinements:
            for amalgator in amalgators:
                if self._isCompatibleAmalgator(refinement, amalgator):
                    Util.moveItem(refinement.item.Serial, API.Backpack)
                    Util.moveItem(amalgator.item.Serial, API.Backpack)
                    API.CancelTarget()
                    API.UseObject(amalgator.item)
                    API.WaitForTarget("any", 3)
                    API.Target(refinement.item.Serial)
                    break

    def _mergeInNewAmalgator(self, level):
        if level not in self.containerSerials:
            return
        containerSerial = self.containerSerials[level]
        Util.openContainer(API.FindItem(containerSerial))

        refinements = self._getRefinements(containerSerial)
        hashes = {}
        for r in refinements:
            h = f"{r.type}-{r.level}-{r.armorType}"
            hashes[h] = hashes.get(h, 0) + 1

        for h, count in hashes.items():
            if count <= 1:
                continue

            level5Serial = self.containerSerials[5]
            emptyAmalgators = self._getAmalgators(level5Serial, isEmpty=True)
            if not emptyAmalgators:
                API.SysMsg("No empty amalgators available.")
                break

            newAmalgator = emptyAmalgators[0]
            Util.moveItem(newAmalgator.item.Serial, API.Backpack)

            foundRefinements = [r for r in refinements if self._isCompatibleHash(r, h)]
            for r in foundRefinements:
                Util.moveItem(r.item.Serial, API.Backpack)

            for r in foundRefinements:
                API.UseObject(newAmalgator.item)
                API.WaitForTarget("any", 3)
                API.Target(r.item.Serial)
                API.Pause(1)


RefinementManager().main()
