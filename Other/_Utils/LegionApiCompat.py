API = None
Util = None


def configure_legion_api_compat(api, util):
    global API
    global Util
    API = api
    Util = util


def _require_runtime(name, value):
    if value is None:
        raise Exception("LegionApiCompat is missing runtime {}".format(name))
    return value


class _ItemProxy:
    def __init__(self, item):
        self._item = item

    @property
    def ItemID(self):
        return getattr(self._item, "Graphic", 0)

    def __getattr__(self, name):
        return getattr(self._item, name)


def _serial(obj):
    if obj is None:
        return 0
    return getattr(obj, "Serial", obj)


def _as_item(obj):
    if obj is None:
        return None
    if isinstance(obj, _ItemProxy):
        return obj
    return _ItemProxy(obj)


def _item_amount(item):
    try:
        amount = int(getattr(item, "Amount", 1) or 1)
    except Exception:
        amount = 1
    return max(1, amount)


def _count_matching_items(container, graphic_data, hue, recursive=False):
    graphics = graphic_data if isinstance(graphic_data, (tuple, list)) else (graphic_data,)
    try:
        contents = API.ItemsInContainer(container, recursive) or []
    except Exception:
        contents = []

    total = 0
    for item in contents:
        if getattr(item, "Graphic", 0) in graphics and getattr(item, "Hue", 0) == hue:
            total += _item_amount(item)
    return total


class Misc:
    @staticmethod
    def SendMessage(message, hue=946):
        _require_runtime("API", API).SysMsg(str(message), hue)

    @staticmethod
    def Pause(milliseconds):
        _require_runtime("API", API).Pause(float(milliseconds) / 1000.0)


class _BackpackProxy:
    @property
    def Serial(self):
        return API.Backpack

    @property
    def Contains(self):
        return [_as_item(item) for item in (API.ItemsInContainer(API.Backpack, False) or [])]


class Player:
    Backpack = _BackpackProxy()

    @property
    def Serial(self):
        return API.Player.Serial

    @staticmethod
    def UseSkill(skill):
        API.UseSkill(skill)


class Target:
    @staticmethod
    def PromptTarget(message):
        API.SysMsg(message, 55)
        target = API.RequestTarget(30)
        return target if target else -1

    @staticmethod
    def WaitForTarget(timeout=5000, harmful=False):
        return API.WaitForTarget("any", float(timeout) / 1000.0)

    @staticmethod
    def TargetExecute(serial):
        API.Target(serial)


class Items:
    @staticmethod
    def FindBySerial(serial):
        return _as_item(API.FindItem(serial))

    @staticmethod
    def FindAllByID(graphic, hue=0, container=0, recursive=False):
        graphics = graphic if isinstance(graphic, (tuple, list)) else (graphic,)
        found_items = []

        if container:
            try:
                Items.WaitForContents(container, 400)
                contents = API.ItemsInContainer(container, recursive) or []
            except Exception:
                contents = []

            for item in contents:
                if getattr(item, "Graphic", 0) in graphics and getattr(item, "Hue", 0) == hue:
                    found_items.append(_as_item(item))

            return found_items

        for item_graphic in graphics:
            found = API.FindType(item_graphic, container, hue=hue)
            if found:
                found_items.append(_as_item(found))
        return found_items

    @staticmethod
    def FindByID(graphic, hue=0, container=0):
        found_items = Items.FindAllByID(graphic, hue, container, recursive=False)
        if found_items:
            return found_items[0]
        return None

    @staticmethod
    def Move(item, destination, amount=0):
        return Util.moveItem(_serial(item), destination, amount)

    @staticmethod
    def WaitForContents(container, timeout=1000):
        API.UseObject(container)
        API.Pause(float(timeout) / 1000.0)

    @staticmethod
    def WaitForProps(item, timeout=1000):
        API.ItemNameAndProps(_serial(item), True, max(1, int(float(timeout) / 1000.0)))

    @staticmethod
    def GetPropStringList(item):
        props = API.ItemNameAndProps(_serial(item), True, 2)
        if not props:
            return []
        return [line.strip() for line in str(props).splitlines() if line.strip()]


class Gumps:
    @staticmethod
    def WaitForGump(gump_id, timeout=5000):
        return API.WaitForGump(gump_id, float(timeout) / 1000.0)

    @staticmethod
    def SendAction(gump_id, button_id):
        return API.ReplyGump(button_id, gump_id)

    @staticmethod
    def GetLineList(gump_id):
        contents = API.GetGumpContents(gump_id)
        if not contents:
            return []
        return [line.strip() for line in str(contents).splitlines() if line.strip()]

    @staticmethod
    def CloseGump(gump_id):
        return API.CloseGump(gump_id)


class Journal:
    @staticmethod
    def Clear():
        API.ClearJournal()

    @staticmethod
    def Search(text):
        return API.InJournal(text)
