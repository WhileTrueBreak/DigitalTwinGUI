import time

from colorama import Fore, Back, Style

MAX_F = 0
MAX_N = 0
LAYER = 0

total = [0]

def timing(func):
    def wrapper(*arg, **kw):
        global MAX_F, MAX_N, LAYER
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
        MAX_F = max(fl, MAX_F)
        tab = f'{Fore.CYAN}|{Style.RESET_ALL} '
        print(f"{tab*LAYER}{func.__qualname__} time:{' '*(MAX_F-fl)} {Fore.RED}{round(dt)}µs{Style.RESET_ALL}{' '*(MAX_N-tl)} {Fore.BLUE}-{round(tracked)}µs{Style.RESET_ALL}")
        LAYER -= 1
        return out
    return wrapper