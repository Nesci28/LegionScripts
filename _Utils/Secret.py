import os

class Secret:
    @staticmethod
    def loadEnv(path=".\\TazUO\\LegionScripts\\.env"):
        if not os.path.exists(path):
            print(f"Warning: {path} file not found")
            return
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()