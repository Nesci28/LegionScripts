import traceback
import datetime

class Error:
    @staticmethod
    def error(msg, isStopping = True):
        API.SysMsg(msg, 33)
        if isStopping:
            API.Stop()
        
    @staticmethod
    def logError(e, scriptName):
        error_message = f"{scriptName} e: {e}"
        tb = traceback.format_exc()
        API.SysMsg(error_message, 33)
        API.SysMsg(tb)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logFile = f"{timestamp}_{scriptName}_crash.log"
        with open(logFile, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {error_message}\n")
            f.write(f"{tb}\n\n")