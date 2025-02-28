# Guy
# opensky.py
# Copyright 2025, Jonathan Koren
# Licensed under the Gnu Public License v3

from math import sqrt

def linear_scale(min_val, actual_val, max_val):
    if actual_val < min_val:
        raise ValueError('too small')
    if actual_val > max_val:
        raise ValueError('too big')
    return (actual_val - min_val) / (max_val - min_val)

def bin_cutoff(value, bins):
    '''Bins are a sorted array of lower bounds. For example: [0, 3, 6] would
    correspond to intervals [0, 3), [3, 6), and [6, inf). Returns the index of
    the bin containing `value`. If the `value` is less than the lower bound of
    the first interval, returns -1.'''
    start = 0
    end = len(bins)
    while start < end:
        mid = ((end - start) // 2) + start
        if value == bins[mid]:
            return mid
        elif value < bins[mid]:
            if mid == 0:
                return -1
            elif bins[mid - 1] <= value:
                return mid - 1
            end = mid
        else: # value > bin[mid]
            start = mid + 1
    return len(bins) - 1

def euclid(x0, y0, x1, y1):
    '''Returns the 2D euclidian distance between two points'''
    return sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
