import copy
import random
import math
import ffs_assignment
import ffs_cp_modules
import time
import move
from datetime import datetime


def local_search(sequence, data_for_cost_calculation, max_time, start_time):
    def cost(sequence, data_for_cost_calculation, upper_cmax=10000):
        stages = data_for_cost_calculation["stages"]
        job_stage_elig = data_for_cost_calculation["job_stage_elig"]
        process = data_for_cost_calculation["process"]
        transTimes = data_for_cost_calculation["transTimes"]
        orders = data_for_cost_calculation["orders"]
        WIPs = data_for_cost_calculation["WIPs"]
        job_list = data_for_cost_calculation["job_list"]

        C_max_no_wip, job_order, loads, starting_times, completion_times, job_cell = ffs_assignment.ffs_assignment(
            sequence, stages, process, job_stage_elig, transTimes, orders, job_list, WIPs)

        C_max_wip, starting_times, completion_times, sols, cut_cp = ffs_cp_modules.ffs_wip(job_order, stages, process,
                                                                                           job_stage_elig, transTimes,
                                                                                           orders, job_list, WIPs,
                                                                                           job_cell,
                                                                                           C_max_upper=10000)

        return C_max_wip, sols, job_order, C_max_no_wip

    result_list = [max_time]
    current_sequence = sequence
    current_c_max, current_sols, current_job_orders, current_cmax_no_wip = cost(sequence, data_for_cost_calculation)
    start_time_ls = time.time()
    swaps_done = 0
    time_found = 0
    swaps_found = 0
    while time.time() - start_time_ls < max_time:
        new_sequence = move.swap(current_sequence)
        new_c_max, new_sols, new_job_orders, new_C_max_no_wip = cost(new_sequence, data_for_cost_calculation,
                                                             upper_cmax=10000)
        swaps_done += 1
        if new_c_max < current_c_max:
            current_sequence = new_sequence
            current_c_max = new_c_max
            current_sols = new_sols
            current_job_orders = new_job_orders
            current_cmax_no_wip = new_C_max_no_wip
            time_found = round(time.time() - start_time_ls,2) + start_time
            swaps_found = swaps_done
            print (f"{datetime.now()} - New sol found with makespan:", {current_c_max})


    end_time = time.time()
    cell_seq = {}
    for s in data_for_cost_calculation["stages"].keys():
        cell_seq[s] = {}
        for m in data_for_cost_calculation["stages"][s]:
            cell_seq[s][m] = ""
            for job in current_job_orders[m]:
                cell_seq[s][m] += str(job) + ';'

    metrics = {'Cmax': current_c_max, 'C_max_nwip': current_cmax_no_wip}


    heur_sols = {'metrics': metrics, 'seq': cell_seq, 'orders': current_sols, "init_order": sequence}

    result_list.extend([current_cmax_no_wip, current_c_max, time_found, round(end_time - start_time_ls, 3), swaps_found, swaps_done])
    return heur_sols, result_list
