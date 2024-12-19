import numpy as np
import time, json, math
import ffs_assignment, ffs_cp_modules
from datetime import datetime
import random
import ffs_SA_hybrid
import ffs_GA_hybrid
import ffs_local_search
import ffs_tabu


def hybrid_mh(general, stages, process, job_stage_elig, transTimes, orders, job_list, WIPs, starting_solution, max_time,
              mh_to_run):
    print(datetime.now(), " - Start of Hybrid.")
    heur_sols = {}
    method_times = {key: round(max_time * mh_to_run['H'][key] / 100) for key in mh_to_run['H'].keys()}
    input_data = {"orders": orders, "stages": stages, "job_list": job_list, "job_stage_elig": job_stage_elig,
                  "process": process, "transTimes": transTimes, "WIPs": WIPs}

    total_results = []
    pop_size = 30

    ######### CALL SA

    initial_population, heurs_sols, results_sa = ffs_SA_hybrid.sa_hybrid(input_data, starting_solution, method_times['SA'])

    initial_population = dict(sorted(initial_population.items(), key=lambda x: x[1]['Obj'])[:pop_size])
    initial_population = {i: v for i, v in enumerate(initial_population.values())}
    total_results.extend(results_sa)
    ######### CALL GA

    final_values, results_ga = ffs_GA_hybrid.ga_hybrid(general, stages, process, job_stage_elig, transTimes, orders,
                                                        job_list, WIPs, pop_size, initial_population, method_times['GA'], method_times['SA'])

    total_results.extend(results_ga)
    ######### CALL LS
    sol_from_ga = list(final_values['init_order'])
    #heur_sols["LS"], results_ls = ffs_local_search.local_search(sol_from_ga, input_data, method_times['LS'], method_times['GA'] + method_times['SA'])
    #total_results.extend(results_ls)
    heur_sols, results_ts = ffs_tabu.tabu_search(sol_from_ga, input_data, method_times['TS'], method_times['GA'] + method_times['SA'])
    total_results.extend(results_ts)

    return heur_sols, total_results
