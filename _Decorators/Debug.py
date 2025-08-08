# import API
import functools
import traceback

def debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        method_name = func.__name__
        API.SysMsg(f"Start of {method_name}")
        result = func(*args, **kwargs)
        API.SysMsg(f"End of {method_name}")
        return result
    return wrapper

def tryExcept(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            API.SysMsg(str(e))
            API.SysMsg(traceback.format_exc())
    return wrapper