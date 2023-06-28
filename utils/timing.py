import time

from colorama import init as colorama_init
from colorama import Fore, Back, Style

HIGHEST = 0
LAYER = 0

def timing(func):
    def wrapper(*arg, **kw):
        global HIGHEST, LAYER
        LAYER += 1
        start = time.time_ns()
        out = func(*arg, **kw)
        end = time.time_ns()
        LAYER -= 1
        fl = len(func.__qualname__)+LAYER*2
        if fl > HIGHEST:
            HIGHEST = fl
        tab = f'{Fore.CYAN}|{Style.RESET_ALL} '
        print(f"{tab*LAYER}{func.__qualname__} time:{' '*(HIGHEST-fl)} {Fore.RED}{int((end-start)/1000)}µs{Style.RESET_ALL}")
        return out
    return wrapper