# import API
import functools

def debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        method_name = func.__name__
        API.SysMsg(f"Start of {method_name}")
        result = func(*args, **kwargs)
        API.SysMsg(f"End of {method_name}")
        return result
    return wrapper