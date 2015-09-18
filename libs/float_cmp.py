import sys


def feq(f1, f2):
    diff = abs(f1 - f2)
    largest = max(abs(f1), abs(f2))
    return diff <= largest * sys.float_info.epsilon * 4
