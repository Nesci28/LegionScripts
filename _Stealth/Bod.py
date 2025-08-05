from enum import Enum
from typing import NewType
from py_stealth import *
from datetime import datetime, timedelta

# Constants
VENDOR_CONTEXT_MENU = 1
BOD_TYPE = 0x2258
WAIT_TIME = 700
WAIT_LAG_TIME = 5000
BOD_INTERVAL = timedelta(minutes=60 * 18 + 1)  # 6hours 1minute
BOD_GUMP_ID = 455  # adjust to your shard's BOD gump id
LUNA_COORDINATES = (986, 519)  # unused, kept for reference

VendorID = NewType("VendorID", int)
ColorCode = NewType("ColorCode", int)
ItemID = NewType("ItemID", int)
GumpID = NewType("GumpID", int)


class BodType(Enum):
    BLACKSMITH = {"bod_book_name": "BS", "vendor": 0x0009B4F7, "bod_color": 0x044E}
    TAILORING = {"bod_book_name": "TS", "vendor": 0x00583C97, "bod_color": 0x0483}


class Profile:
    def __init__(self, name: str, bod_type: BodType, active: bool = True):
        self.name = name
        self.active = active
        self.bod_type = bod_type
        self.last_time = datetime.now() - timedelta(days=1)
        self.vendor = bod_type.value["vendor"]

    def __str__(self) -> str:
        return self.name

    def can_get_bod(self) -> bool:
        time_since_last = datetime.now() - self.last_time
        time_left = BOD_INTERVAL - time_since_last
        if time_left > timedelta(0):
            minutes_left = int(time_left.total_seconds() // 60)
            print(f"{minutes_left} minutes left to get a bod {self.name}")
            return False
        return True

    def should_connect(self) -> bool:
        # avoid reconnect thrash if we just touched the char
        return (datetime.now() - self.last_time) >= timedelta(minutes=1)


def disconnect():
    # bounded disconnect loop to avoid permanent hang
    attempts = 0
    while Connected() and attempts < 10:
        Disconnect()
        Wait(WAIT_LAG_TIME)
        attempts += 1


def connect():
    # bounded connect loop to avoid permanent hang
    attempts = 0
    while not Connected() and attempts < 10:
        Connect()
        Wait(WAIT_LAG_TIME)
        attempts += 1


def close_gumps():
    # close all closable gumps from top to bottom
    changed = True
    rounds = 0
    while IsGump() and changed and rounds < 10:
        changed = False
        count = GetGumpsCount()
        for i in reversed(range(count)):
            if IsGumpCanBeClosed(i):
                CloseSimpleGump(i)
                Wait(WAIT_TIME)
                changed = True
        rounds += 1


def load_profile(profile: Profile):
    if not profile.should_connect():
        print(f"Skipping {profile.name}, as it's too soon to reconnect.")
        return

    print(f"Loading profile {profile} {datetime.now().strftime('%H:%M:%S')}")
    disconnect()
    ChangeProfile(profile.name)
    connect()
    close_gumps()
    UseObject(Backpack())  # wake up backpack tooltip cache
    Wait(WAIT_TIME)


def _press_bod_gump_button_if_present() -> bool:
    """Return True if we saw the expected BOD gump and pressed button 1."""
    cnt = GetGumpsCount()
    if cnt <= 0:
        return False
    for i in range(cnt):
        info = GetGumpInfo(i)
        if info and "GumpID" in info and info["GumpID"] == BOD_GUMP_ID:
            # Press first button on that gump. WaitGump('1') presses on the last gump usually,
            # but many shards only open one BOD gump at a time; this is acceptable.
            WaitGump("1")
            CheckLag(50000)
            return True
    return False


def _request_once(profile: Profile) -> tuple[bool, int]:
    """Return (got_bod, delta_count) using the success phrase + count delta."""
    ClearJournal()
    pre = CountEx(BOD_TYPE, profile.bod_type.value["bod_color"], Backpack())

    SetContextMenuHook(profile.vendor, VENDOR_CONTEXT_MENU)
    Wait(WAIT_TIME)
    RequestContextMenu(profile.vendor)
    Wait(WAIT_TIME)
    CheckLag(60_000)

    _press_bod_gump_button_if_present()
    Wait(500)

    got = False
    idx = HighJournal()
    while idx < HighJournal():
        idx += 1
        if "in your backpack" in (Journal(idx) or "").lower():
            got = True

    post = CountEx(BOD_TYPE, profile.bod_type.value["bod_color"], Backpack())
    return got, max(0, post - pre)


def get_bod(profile: Profile) -> bool:
    # First attempt
    got, delta = _request_once(profile)
    if got or delta > 0:
        profile.last_time = datetime.now()
        print("Got BOD; probing once to infer cooldown…")
        Wait(500)
        return get_bod(profile)

    # No success; short conservative backoff
    print("No BOD")
    profile.last_time = datetime.now()
    return False


def process_profiles(_profiles):
    while True:
        for profile in _profiles:
            if profile.active and profile.can_get_bod():
                load_profile(profile)
                try:
                    Wait(10 * 1000)
                    get_bod(profile)
                except Exception as e:
                    print(f"Error while getting BOD for {profile.name}: {e}")
                disconnect()
                # Wait 2 minutes 30 seconds before loading the next profile
                print("Waiting 2m30s before switching to the next profile...")
                Wait((2 * 60 + 30) * 1000)

        Wait(1 * 60 * 1000)


if __name__ == "__main__":
    profiles = [
        Profile("NesciD5 - Atlantic - Juicy", BodType.TAILORING),
        Profile("NesciD5 - Atlantic - Bezos", BodType.TAILORING),
        Profile("NesciD5 - Atlantic - Beastcaller", BodType.TAILORING),
        Profile("NesciD5 - Atlantic - Vladokami", BodType.TAILORING),
        Profile("NesciD5 - Atlantic - Bobber Bill", BodType.TAILORING),
        Profile("NesciD5 - Atlantic - Strongback", BodType.TAILORING),
    ]
    process_profiles(profiles)
