import time
import audio
import head_pose
import matplotlib.pyplot as plt
import numpy as np

PLOT_LENGTH = 200

#place holders
GLOBAL_CHEAT = 0
PERCENTAGE_CHEAT = 0
CHEAT_THRESH = 0
XDATA = list(range(200))
YDATA = [0]*200

def avg(current,previous):
    if previous > 1:
        return 0.65
    if current == 0:
        if previous < 0.01:
            return 0.01
        return previous / 1.01
    if previous == 0:
        return current
    return 1 * previous + 0.1 * current

