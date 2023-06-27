import time

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

HIGHEST = 0

def timing(func):
    def wrapper(*arg, **kw):
        global HIGHEST
        start = time.time_ns()
        out = func(*arg, **kw)
        fl = len(func.__qualname__)
        if fl > HIGHEST:
            HIGHEST = fl
        print(f"{func.__qualname__} time:{' '*(HIGHEST-fl)} {Fore.RED}{int((time.time_ns()-start)/1000)}us{Style.RESET_ALL} to run")
        return out
    return wrapper