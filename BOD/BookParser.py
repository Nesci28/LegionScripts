import API
import re
from datetime import datetime

inBackpackBodSerials = []

log_file_path = r"C:\Games\Taz_BleedingEdge\TazUO-Launcher.win-x64\TazUO\LegionScripts\parse.log"


def moveItem(item_serial, destination_serial, amount=0, max_retries=5):
    for attempt in range(max_retries):
        API.ClearJournal()
        API.MoveItem(item_serial, destination_serial, amount)
        API.Pause(1.0)

        if not API.InJournal("You must wait to perform another action."):
            return True

        API.SysMsg(f"Retrying move ({attempt + 1}/{max_retries})...", 33)
        API.Pause(1.0)

    API.SysMsg("Move failed after retries.", 33)
    return False


def selectBooks():
    toParseBookSerials = []
    toParseBooks = []
    API.SysMsg("Target books to parse. Retarget a book to end selection.")
    while True:
        toParseBookSerial = API.RequestTarget()
        if toParseBookSerial in toParseBookSerials:
            break
        toParseBook = API.FindItem(toParseBookSerial)
        toParseBooks.append(toParseBook)
        toParseBookSerials.append(toParseBookSerial)
    return toParseBooks


def getNumberOfDeeds(book):
    props = API.ItemNameAndProps(book.Serial).split("\n")
    for prop in props:
        if "Deeds In Book:" in prop:
            match = re.search(r"Deeds In Book:\s*(\d+)", prop)
            return match.group(1)
    return "0"


def displayProgress(current, total, bar_length=20):
    progress = int((current / total) * bar_length)
    bar = "#" * progress + "-" * (bar_length - progress)
    API.SysMsg(f"Parsing Progress: [{bar}] {current}/{total}", 88)


def openBook(bookSerial):
    while not API.HasGump(668):
        API.UseObject(bookSerial)
        API.Pause(1)


def parse(bookSerial, f, isLast):
    bods = API.FindTypeAll(0x2258, API.Backpack)
    while len(bods) == 0 or len(bods) == len(inBackpackBodSerials):
        openBook(bookSerial)
        API.ReplyGump(4, 668)
        API.Pause(1)
        bods = API.FindTypeAll(0x2258, API.Backpack)

    for bod in bods:
        if bod.Serial in inBackpackBodSerials:
            continue

        props = API.ItemNameAndProps(bod.Serial).split("\n")
        for prop in props:
            f.write(prop + "\n")
        if not isLast:
            f.write("#####################\n\n\n")
        else:
            f.write("\n\n")
        f.flush()

        moveItem(bod.Serial, bookSerial)


def main():
    bods = API.FindTypeAll(0x2258, API.Backpack)
    for bod in bods:
        inBackpackBodSerials.append(bod.Serial)

    toParseBooks = selectBooks()
    if len(toParseBooks) == 0:
        API.SysMsg("No book selected for parsing.", 33)
        return

    with open(log_file_path, "w", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("[%y/%m/%d][%H:%M:%S]")
        f.write(timestamp + "\n\n")
        for toParseBook in toParseBooks:
            nbrOfDeeds = int(getNumberOfDeeds(toParseBook))
            if nbrOfDeeds == 0:
                API.SysMsg(f"Book {toParseBook.Serial} is empty.", 33)
                continue

            API.SysMsg(f"Parsing book {toParseBook.Serial} with {nbrOfDeeds} deeds.", 88)
            API.UseObject(toParseBook)
            API.Pause(1)

            startingSerial = None

            for i in range(1, nbrOfDeeds + 1):
                if startingSerial == None:
                    parse(toParseBook.Serial, f, i == nbrOfDeeds + 1)

                displayProgress(i, nbrOfDeeds)

            API.SysMsg(f"Done parsing book {toParseBook.Serial}.", 88)


main()
