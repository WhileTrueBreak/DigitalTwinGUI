import time

from colorama import init as colorama_init
from colorama import Fore, Back, Style

HIGHEST = 0
LAYER = 1

total = {}

def timing(func):
    def wrapper(*arg, **kw):
        global HIGHEST, LAYER
        LAYER += 1
        start = time.time_ns()
        out = func(*arg, **kw)
        end = time.time_ns()
        dt = (end-start)/1000
        LAYER -= 1
        fl = len(func.__qualname__)+LAYER*2
        HIGHEST = max(fl, HIGHEST)
        tab = f'{Fore.CYAN}|{Style.RESET_ALL} '
        print(f"{tab*LAYER}{func.__qualname__} time:{' '*(HIGHEST-fl)} {Fore.RED}{round(dt)}µs{Style.RESET_ALL}")
        return out
    return wrapper