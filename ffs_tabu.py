import random
import math
import ffs_assignment
import ffs_cp_modules
import time
import move
from datetime import datetime


def tabu_search(starting_sequence, data_for_cost_calculation, timelimit, start_t):
    def cost(sequence, data_for_cost_calculation, upper_cmax=10000):
        stages = data_for_cost_calculation["stages"]
        job_stage_elig = data_for_cost_calculation["job_stage_elig"]
        process = data_for_cost_calculation["process"]
        transTimes = data_for_cost_calculation["transTimes"]
        orders = data_for_cost_calculation["orders"]
        WIPs = data_for_cost_calculation["WIPs"]
        job_list = data_for_cost_calculation["job_list"]

        # big_M = 10000000

        C_max, job_order, loads, starting_times, completion_times, job_cell = ffs_assignment.ffs_assignment(
            sequence, stages, process, job_stage_elig, transTimes, orders, job_list, WIPs)

        C_max_wip, starting_times, completion_times, sols, cut_cp = ffs_cp_modules.ffs_wip(job_order, stages, process,
                                                                                           job_stage_elig, transTimes,
                                                                                           orders, job_list, WIPs,
                                                                                           job_cell,
                                                                                           C_max_upper=10000)

        return C_max_wip, sols, job_order, C_max

    # returns the best neighbor out of {num of neighbors} found neighbors
    def best_move(sequence):
        big_M = 10000
        best_neighbor_found = None
        best_cost_found = big_M
        best_sols_found = None
        best_job_order_found = None
        best_c_max_no_wip = big_M
        max_moves_reached = False
        short_tabu_list = []
        valid_neighbors_checked = 0
        num_of_moves = 0
        cps = 0
        # search the neighborhood
        while valid_neighbors_checked < max_moves:
            # random eligible neighbor
            found_neighbor = move.swap(sequence)
            num_of_moves += 1
            while found_neighbor in tabu_list or found_neighbor in short_tabu_list:
                # check that time is not exceeded
                if time.time() - start_time >= max_seconds:
                    break
                # check that max num of moves is not reached
                if num_of_moves == max_moves:
                    max_moves_reached = True
                    break
                found_neighbor = move.swap(sequence)
                num_of_moves += 1

            # continuously update
            time_limit_reached = time.time() - start_time > max_seconds

            if time_limit_reached:
                print(f"time limit reached ({max_seconds}s). Taking the best of {valid_neighbors_checked} neighbors")
                break

            if max_moves_reached:
                print(f"max moves reached ({max_moves}). Taking the best of {valid_neighbors_checked} neighbors")
                break

            found_cost, found_sols, found_job_orders, found_cmax_no_wip = cost(found_neighbor, data_for_cost_calculation, big_M)
            cps += 1
            short_tabu_list.append(found_neighbor)
            # print(f"found neighbor {found_neighbor} with cost {found_cost}")

            if found_cost < best_cost_found:
                # print(f"{found_neighbor} is better than old best")
                best_neighbor_found = found_neighbor
                best_cost_found = found_cost
                best_sols_found = found_sols
                best_job_order_found = found_job_orders
                best_c_max_no_wip = found_cmax_no_wip

            valid_neighbors_checked += 1

        return best_neighbor_found, best_cost_found, best_sols_found, best_job_order_found, best_c_max_no_wip, cps

    def update_tabu_list(sequence):
        # print("updating tabu list")
        tabu_list.append(sequence)
        if len(tabu_list) > list_size:
            tabu_list.pop(0)
        # print(tabu_list)

    max_seconds = timelimit
    time_found = 0
    # neighbors_to_check = 20
    max_moves = 30
    list_size = 20
    iterations = 50
    results = [list_size, iterations, max_moves, max_seconds]
    start_time = time.time()
    tabu_list = [[starting_sequence]]
    best_sequence_found = starting_sequence
    sequence = starting_sequence
    best_cost_found, best_sols_found, best_job_orders_found, best_c_max_no_wip = cost(starting_sequence,
                                                                                      data_for_cost_calculation)
    t = 0
    total_cps = 0
    while t < iterations and time.time() - start_time < timelimit:
        print(f"starting {t} iteration - {datetime.now()}")
        neighbor_sequence, neighbor_cost, sols, job_orders, c_max_no_wip, cps = best_move(sequence)
        total_cps += cps
        print(f"finished {t} iteration - {datetime.now()}")
        if neighbor_cost < best_cost_found:
            best_cost_found = neighbor_cost
            best_sequence_found = neighbor_sequence
            best_sols_found = sols
            best_job_orders_found = job_orders
            best_c_max_no_wip = c_max_no_wip
            time_found = round(time.time() - start_time,2) + start_t
        update_tabu_list(neighbor_sequence)
        sequence = neighbor_sequence
        t += 1

    cell_seq = {}
    for s in data_for_cost_calculation["stages"].keys():
        cell_seq[s] = {}
        for m in data_for_cost_calculation["stages"][s]:
            cell_seq[s][m] = ""
            for job in best_job_orders_found[m]:
                cell_seq[s][m] += str(job) + ';'

    metrics = {'Cmax': best_cost_found, 'Cmax_nowip': best_c_max_no_wip}
    results.extend([best_c_max_no_wip, best_cost_found, time_found, round(time.time() - start_time, 2), total_cps])
    heur_sols = {'metrics': metrics, 'seq': cell_seq, 'orders': best_sols_found, "init_order": best_sequence_found,
                 'starting_solution': starting_sequence}

    # print(f"final cost: {best_cost_found} from solution {best_sequence_found}")
    return heur_sols, results
