import math
import time
import numpy as np
from datetime import datetime


def warm_start(sols, transTimes, process, stages):
    print(datetime.now(), " - Start of Warm Start.")
    json_sols = {}
    best_method, best_Cmax = '', math.inf
    for i in sols.keys():
        json_sols[i] = sols[i]
        if sols[i]['metrics']['Cmax'] < best_Cmax:
            best_method = i
            best_Cmax = sols[i]['metrics']['Cmax']

    json_sols['best'] = sols[best_method]

    warm_start = {'X': {}, 'Y': {}, 'Cmax': best_Cmax, 'C': {}}

    for stage in sols[best_method]['seq']:
        for m in sols[best_method]['seq'][stage]:
            jobs = sols[best_method]['seq'][stage][m].split(';')[:-1]
            previous = 0
            for job in jobs:
                warm_start['Y'][(job, stage, m)] = 1
                pos_job = jobs.index(job)
                if previous != 0 and pos_job < len(jobs):
                    warm_start['X'][(previous, stage, job)] = 1
                previous = job


    for i in sols[best_method]['orders'].keys():
        for suborder in sols[best_method]['orders'][i].keys():
            for job in sols[best_method]['orders'][i][suborder].keys():
                for cell in sols[best_method]['orders'][i][suborder][job].keys():
                    for stage in stages.keys():
                        if cell in stages[stage]:
                            warm_start['C'][(job, stage)] = sols[best_method]['orders'][i][suborder][job][cell]['end']

    print(datetime.now(), " - End of Warm Start.")
    return warm_start
