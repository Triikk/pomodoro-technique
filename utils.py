import math

def format_time(s: int):
    m = math.trunc(s / 60)
    s %= 60
    return "{:02d}:{:02d}".format(m, s)