import math
import time
import numpy as np
import json
from datetime import datetime
import random
import ffs_GA
import ffs_tabu
import ffs_local_search
import ffs_SA
import ffs_pso

def heuristics(general, stages, process, job_stage_elig, transTimes, orders, job_list, WIPs, metaheur_to_run,
               starting_solution, max_time):
    print(datetime.now(), " - Start of Heuristics.")
    heur_sols = {}

    input_data = {"orders": orders, "stages": stages, "job_list": job_list, "job_stage_elig": job_stage_elig,
                  "process": process, "transTimes": transTimes, "WIPs": WIPs}

    #print (starting_solution)
    # Create a random initial sequence (solution)
    if not starting_solution:
        starting_solution = list(orders.keys())
        random.shuffle(starting_solution)

    # Call metaheuristics

    if "TS" in metaheur_to_run.keys():
        # call tabu
        print("executing TABU")
        heur_sols["TABU"], results = ffs_tabu.tabu_search(starting_solution, input_data, max_time, 0)

    if "LS" in metaheur_to_run.keys():
        # call LS
        print("executing LS")
        heur_sols["LS"], results = ffs_local_search.local_search(starting_solution, input_data, max_time,0)

    if "SA" in metaheur_to_run.keys():
        # call SA
        print("executing SA")
        heur_sols["SA"], results = ffs_SA.simulated_annealing(input_data, starting_solution)

    if "GA" in metaheur_to_run.keys():
        print("executing GA")
        heur_sols['GA'], results = ffs_GA.genetic_alg(general, stages, process, job_stage_elig, transTimes, orders,
                                                      job_list, WIPs)

    if "PSO" in metaheur_to_run.keys():
        print("executing PSO")
        heur_sols['PSO'], results = ffs_pso.particle_swarm(input_data)


    print(datetime.now(), " - End of Heuristics.")
    # print (heur_sols)
    return heur_sols, results
