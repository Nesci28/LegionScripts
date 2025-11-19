import API
import re

gump = API.GetGump(460)
lines = API.GetGumpContents(460)
match = re.search(r'([A-Za-z/ ]+)\([0-9]+\)\s*\*', lines)
API.SysMsg(match.group(1).strip())