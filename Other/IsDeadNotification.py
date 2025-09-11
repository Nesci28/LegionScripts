import API
from datetime import datetime, timedelta
import importlib
from LegionPath import LegionPath

LegionPath.addSubdirs()

import Notification

importlib.reload(Notification)

from Notification import Notification


class IsDeadNotification:
    lastNotificationDate = None
    
    def __init__(self):
        self.notification = Notification()

    def main(self):
        while True:
            if API.Player.IsDead:
                now = datetime.now()
                if (
                    not self.lastNotificationDate
                    or now - self.lastNotificationDate > timedelta(minutes=1)
                ):
                    self.notification.sendNotification("Player DEAD")
                    self.lastNotificationDate = now
            API.Pause(0.5)


IsDeadNotification().main()
