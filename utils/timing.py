import time

from colorama import init as colorama_init
from colorama import Fore, Back, Style

HIGHEST = 0
MAX_N = 0
LAYER = 0

total = [0]

def timing(func):
    def wrapper(*arg, **kw):
        global HIGHEST, LAYER, MAX_N
        LAYER += 1
        total.append(0)
        start = time.time_ns()
        out = func(*arg, **kw)
        end = time.time_ns()
        dt = (end-start)/1000
        total[LAYER-1] += dt
        tracked = total.pop()
        fl = len(func.__qualname__)+LAYER*2
        tl = len(f'{round(dt)}')
        MAX_N = max(MAX_N, tl)
        HIGHEST = max(fl, HIGHEST)
        tab = f'{Fore.CYAN}|{Style.RESET_ALL} '
        print(f"{tab*LAYER}{func.__qualname__} time:{' '*(HIGHEST-fl)} {Fore.RED}{round(dt)}µs{Style.RESET_ALL}{' '*(MAX_N-tl)} {Fore.BLUE}-{round(tracked)}µs{Style.RESET_ALL}")
        LAYER -= 1
        return out
    return wrapper