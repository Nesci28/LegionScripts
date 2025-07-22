import time
import hashlib

class Timer:
    timers = []
    
    @classmethod
    def create(cls, seconds, text, hue=21):
        cls.clear(seconds, text, hue)
        API.CreateCooldownBar(seconds, text, hue)
        hash = cls._hash(seconds, text, hue)
        cls.timers.append({
            "created": time.time(),
            "seconds": seconds,
            "hash": hash
        })

    @classmethod
    def exists(cls, seconds, text, hue=21):
        cls._cleanupExpired()
        hash = cls._hash(seconds, text, hue)
        for timer in cls.timers:
            if timer["hash"] == hash:
                return True
        return False
        
    @classmethod
    def clear(cls, seconds, text, hue):
        hash = cls._hash(seconds, text, hue)
        cls.timers = [t for t in cls.timers if t["hash"] != hash]
        
    @classmethod
    def _hash(cls, seconds, text, hue):
        s = f"{seconds}{text}{hue}"
        return hashlib.md5(s.encode("ascii")).hexdigest()
    
    @classmethod
    def _cleanupExpired(cls):
        now = time.time()
        cls.timers = [
            t for t in cls.timers
            if now - t["created"] < t["seconds"]
        ]