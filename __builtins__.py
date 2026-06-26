try:
    from typing import TYPE_CHECKING
except Exception:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    import API
    pass
# API is injected by TazUO at runtime; the import above is IDE-only.