import os
import re
from pathlib import Path

# === CONFIG ===
ENTRY_FILE = "Farm/DarkGuardians.py"
OUTPUT_FILE = "Farm/DarkGuardians.bundled.py"
ROOT_DIR = Path(".")

# === REGEX ===
IMPORT_RE = re.compile(
    r"^(?:\s*from\s+([\w\.]+)\s+import\s+[\w\*,\s]+|\s*import\s+([\w\.]+))\s*$",
    re.MULTILINE,
)

visited = set()

def find_in_subdirs(module_name: str) -> Path | None:
    """Search recursively for a .py file matching the module name."""
    target = f"{module_name}.py"
    for root, dirs, files in os.walk(ROOT_DIR):
        if target in files:
            return Path(root) / target
    return None

def resolve_module(module_name: str) -> Path | None:
    """Resolve a module name to a file path within ROOT_DIR."""
    rel_path = module_name.replace(".", "/") + ".py"
    direct = ROOT_DIR / rel_path
    if direct.exists():
        return direct
    alt = ROOT_DIR / f"{module_name}.py"
    if alt.exists():
        return alt
    return find_in_subdirs(module_name)

def inline_file(file_path: Path, depth=0) -> str:
    """Inline all local imports recursively and clean up code."""
    abs_path = file_path.resolve()
    if abs_path in visited:
        return ""
    visited.add(abs_path)

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"⚠️ Skipping unreadable file {file_path}: {e}")
        return ""

    # 1️⃣ Find imports
    imports = []
    for match in IMPORT_RE.finditer(code):
        module = match.group(1) or match.group(2)
        if not module:
            continue
        resolved = resolve_module(module)
        if resolved:
            imports.append(resolved)

    # 2️⃣ Inline dependencies first
    output = ""
    for dep in imports:
        output += inline_file(dep, depth + 1)

    # 3️⃣ Remove LegionPath & importlib lines safely
    cleaned_lines = []
    for line in code.splitlines():
        stripped = line.strip()
        # Skip these lines entirely
        if stripped.startswith("from LegionPath import LegionPath"):
            continue
        if stripped.startswith("LegionPath.addSubdirs()"):
            continue
        if stripped.startswith("importlib.reload("):
            continue

        # Skip inlined local imports
        match = IMPORT_RE.match(line)
        if match:
            module = match.group(1) or match.group(2)
            if resolve_module(module):
                continue

        cleaned_lines.append(line)

    cleaned_code = "\n".join(cleaned_lines)

    # 4️⃣ Clean extra colons / blank lines
    cleaned_code = re.sub(r"(?m)^\s*:\s*$", "", cleaned_code)
    cleaned_code = re.sub(r"\n{3,}", "\n\n", cleaned_code)

    header = f"\n# ==== {file_path.name} (inlined) ====\n"
    return output + header + cleaned_code.strip() + "\n"

def bundle():
    entry_path = ROOT_DIR / ENTRY_FILE
    print(f"🔗 Bundling {ENTRY_FILE} → {OUTPUT_FILE}")
    bundled_code = inline_file(entry_path).strip() + "\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(bundled_code)
    print(f"✅ Done! Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    bundle()
