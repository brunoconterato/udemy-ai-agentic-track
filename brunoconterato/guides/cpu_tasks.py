import time


def cpu_bound(n):
    # trabalho CPU-intenso simples
    s = 0
    for i in range(2000000):
        s += (i * i) % (n + 1)
    return s
