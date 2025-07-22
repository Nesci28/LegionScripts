import importlib
import sys

sys.path.append(
    r".\\TazUO\\LegionScripts\\_Utils"
)

import Magic
import Util
import Math

importlib.reload(Magic)
importlib.reload(Util)
importlib.reload(Math)


class Music:
    instrumentIds = [3740, 3741, 3762, 3763]

    @staticmethod
    def validate():
        errors = []
        instruments = Music._findInstruments()
        if len(instruments) == 0:
            errors.append("Music - Missing instruments")
        return errors
    
    @staticmethod
    def _findInstruments():
        instruments = []
        for instrumentId in Music.instrumentIds:
            items = Util.Util.findTypeAll(API.Backpack, instrumentId)
            if len(items) > 0:
                instruments.extend(items)
        return instruments
            