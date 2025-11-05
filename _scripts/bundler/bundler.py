import argparse
from pathlib import Path
from re import compile


class Bundler:
    def __init__(self, inputFile, outputFile, directories):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.directories = directories
        self.f = self._openOutputFile()
        self.importRegex = compile(
            r"^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)", flags=0 | 8
        )

    def bundle(self):
        dependencies = self._getDependencies()

        # --- Step 1: Collect all bundled module names (e.g. "_Utils.Gump")
        bundled_modules = {Path(dep).stem for dep in dependencies}
        # Also include the main input file name (to avoid self-import)
        bundled_modules.add(Path(self.inputFile).stem)

        all_imports = set()
        body_chunks = []

        def extract_imports(content):
            lines = content.splitlines()
            imports = []
            body = []
            for line in lines:
                stripped = line.strip()

                # 🧹 skip undesired lines
                if (
                    stripped.startswith("LegionPath.addSubdirs()")
                    or stripped.startswith("importlib.reload(")
                ):
                    continue

                # 🧩 separate imports and body
                if stripped.startswith("import ") or stripped.startswith("from "):
                    # Skip imports of bundled modules (handled above)
                    if any(bundled in stripped.split() for bundled in bundled_modules):
                        continue
                    imports.append(line)
                else:
                    body.append(line)

            return imports, "\n".join(body)


        # --- Step 2: Process dependencies
        for dependency in dependencies:
            contents = self._readFile(dependency)
            imports, body = extract_imports(contents)
            all_imports.update(imports)
            body_chunks.append((dependency, body))

        # --- Step 3: Process the main input file
        contents = self._readFile(self.inputFile)
        imports, body = extract_imports(contents)
        all_imports.update(imports)
        body_chunks.append((self.inputFile, body))

        # --- Step 4: Write imports (excluding bundled ones)
        self.f.write("#=========== Consolidated Imports ============#\n")
        for imp in sorted(all_imports):
            self.f.write(f"{imp}\n")
        self.f.write("\n\n")

        # --- Step 5: Write bundled file bodies
        for file_path, body in body_chunks:
            self.f.write(f"#=========== Start of {file_path} ============#\n")
            self.f.write(f"{body}\n")
            self.f.write(f"#=========== End of {file_path} ============#\n\n")

    def _openOutputFile(self):
        file = None
        try:
            file = open(self.outputFile, "x", encoding="utf-8")
        except:
            file = open(self.outputFile, "w", encoding="utf-8")
        return file

    def _readFile(self, filePath):
        return Path(filePath).read_text(encoding="utf-8", errors="ignore")

    def _getDependencies(self):
        visited = set()
        dependencies = []
        ignore_modules = {"API"}

        def resolveImports(file_path):
            if file_path in visited:
                return
            visited.add(file_path)
            content = self._readFile(file_path)
            imports = self.importRegex.findall(content)

            for imp in imports:
                if imp in ignore_modules:
                    continue
                for directory in self.directories:
                    possible_path = Path(directory) / f"{imp}.py"
                    if possible_path.exists():
                        resolveImports(possible_path)
                        if str(possible_path) not in dependencies:
                            dependencies.append(str(possible_path))

        resolveImports(self.inputFile)
        return dependencies


parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--inputFile",
    dest="inputFile",
    type=str,
    help="Your input file",
    required=True,
)
parser.add_argument(
    "-o",
    "--outputFile",
    dest="outputFile",
    type=str,
    help="Your bundled output file",
    required=True,
)
parser.add_argument(
    "-d",
    "--directories",
    dest="directories",
    nargs="+",
    help="List of folders to your modules",
    required=True,
)
args = parser.parse_args()
bundler = Bundler(args.inputFile, args.outputFile, args.directories)
bundler.bundle()
