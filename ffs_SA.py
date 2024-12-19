import copy
import random
import math
import ffs_assignment
import ffs_cp_modules
import time
from datetime import datetime

def simulated_annealing(data_for_cost_calculation, sequence):
    def cost(sequence, data_for_cost_calculation):
        stages = data_for_cost_calculation["stages"]
        job_stage_elig = data_for_cost_calculation["job_stage_elig"]
        process = data_for_cost_calculation["process"]
        transTimes = data_for_cost_calculation["transTimes"]
        orders = data_for_cost_calculation["orders"]
        WIPs = data_for_cost_calculation["WIPs"]
        job_list = data_for_cost_calculation["job_list"]

        big_M = 10000

        C_max, job_order, loads, starting_times, completion_times, job_cell = ffs_assignment.ffs_assignment(
            sequence, stages, process, job_stage_elig, transTimes, orders, job_list, WIPs)

        C_max_wip, starting_times, completion_times, sols, cut_cp = ffs_cp_modules.ffs_wip(job_order, stages, process,
                                                                                           job_stage_elig, transTimes,
                                                                                           orders, job_list, WIPs,
                                                                                           job_cell, big_M)

        return C_max_wip, sols, job_order, C_max

    # Inner swap method
    def get_neighbor(seq):
        neighbor = seq[:]
        i, j = random.sample(range(len(seq)), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        return neighbor

    initial_makespan, initial_sols, initial_job_orders, initial_makespan_no_wip = cost(sequence, data_for_cost_calculation)

    result_list = []
    current_solution = sequence[:]
    current_makespan = initial_makespan
    best_solution = current_solution[:]
    best_makespan = current_makespan
    best_makespan_no_wip = initial_makespan_no_wip
    best_sols = copy.deepcopy(initial_sols)
    best_job_orders = copy.deepcopy(initial_job_orders)
    time_found = 0
    Tc, Tcry, q, iterations = 200, 1, 0.9, 50
    T = Tc
    start_time = time.time()
    while T > Tcry:
        # time_iter = time.time()
        for i in range(iterations):
            new_solution = get_neighbor(current_solution)  # Swaps
            new_makespan, sols, job_orders, new_makespan_no_wip = cost(new_solution, data_for_cost_calculation)

            delta = new_makespan - current_makespan
            U = random.uniform(0, 1)

            if ((U < math.exp(-delta / T) and delta >= 0) or delta < 0) and new_makespan < math.inf:
                current_solution = new_solution
                current_makespan = new_makespan

            if current_makespan < best_makespan:
                best_solution = current_solution
                best_makespan = current_makespan
                best_makespan_no_wip = new_makespan_no_wip
                best_sols = copy.deepcopy(sols)
                best_job_orders = copy.deepcopy(job_orders)
                time_found = round(time.time() - start_time, 3)
            # print(new_solution)
        T *= q
        print(datetime.now(), " - End of iter. with", T, '-', Tcry)
    end_time = time.time()
    print("Optimized Sequence:", best_solution)
    print("Optimized Makespan:", best_makespan)

    cell_seq = {}
    for s in data_for_cost_calculation["stages"].keys():
        cell_seq[s] = {}
        for m in data_for_cost_calculation["stages"][s]:
            cell_seq[s][m] = ""
            for job in best_job_orders[m]:
                cell_seq[s][m] += str(job) + ';'

    metrics = {'Cmax': best_makespan, 'Cmax_no_wip': best_makespan_no_wip}
    heur_sols = {'params': {'Tc': Tc, 'Tcry': Tcry, 'q': q, 'Iterations': iterations}, 'metrics': metrics,
                 'seq': cell_seq, 'orders': best_sols, "init_order": best_solution, 'starting_solution': sequence}
    result_list.extend([Tc, Tcry, q, iterations, math.ceil(best_makespan_no_wip), math.ceil(best_makespan), time_found,
                        round(end_time - start_time, 3)])

    return heur_sols, result_list
