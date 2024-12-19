import math
import time
import numpy as np
from datetime import datetime


def json_output(sols, transTimes, process, stages):
    print(datetime.now(), " - Start of Json Output.")
    json_sols = {}
    best_method, best_Cmax = '', math.inf
    for i in sols.keys():
        json_sols[i] = sols[i]
        if sols[i]['metrics']['Cmax'] < best_Cmax:
            best_method = i
            best_Cmax = sols[i]['metrics']['Cmax']

    json_sols['best'] = {'method': best_method, 'sols': sols[best_method]}

    print(datetime.now(), " - End of Json Output.")
    return json_sols
