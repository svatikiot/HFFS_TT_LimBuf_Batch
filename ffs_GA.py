import numpy as np
import time, json, math
import ffs_assignment, ffs_cp_modules
from datetime import datetime
import random


def genetic_alg(general, stages, process, job_stage_elig, transTimes, orders, job_list, WIPs):
    print(datetime.now(), " - Start of GA.")
    time_found = 0
    result_list = []
    sum_executions = 0
    sum_cut_cp = 0
    big_M = 1000000

    # GA PARAMETERS
    population_size = [50]
    generations_num = [200]
    cross_probability = [0.5]
    mutation_probability = [0.3]

    for pop_size in population_size:
        for generations in generations_num:
            for cross in cross_probability:
                for mut in mutation_probability:
                    gen_counter = 1
                    new_off = 0
                    start_ga = time.time()

                    while gen_counter <= generations and time.time() - start_ga <= 3600:
                        # GA initial population spawning

                        if gen_counter == 1:
                            print("Spawning")
                            population = spawning(pop_size, orders)

                            # Calculate fitness functions for initial population

                            for ch in population.keys():
                                population[ch]['Obj_no_wip'], population[ch][
                                    'job_order'], loads, starting_times, completion_times, job_cell = ffs_assignment.ffs_assignment(
                                    population[ch]['Order'], stages, process, job_stage_elig, transTimes, orders,
                                    job_list, WIPs)
                                population[ch]['Time_found'] = round(time.time() - start_ga, 3)
                                population[ch]['Obj'], population[ch]['start'], population[ch]['end'], population[ch][
                                    'sols'], cut_cp = ffs_cp_modules.ffs_wip(population[ch]['job_order'], stages,
                                                                             process, job_stage_elig, transTimes,
                                                                             orders, job_list, WIPs, job_cell, big_M)
                                print(datetime.now(), "Spawned", ch, population[ch]['Obj'])
                            population = dict(sorted(population.items(), key=lambda x: x[1]['Obj'])[:pop_size])
                            population = {i: v for i, v in enumerate(population.values())}
                            sol_cut_off = round(population[pop_size - 1]['Obj'], 2)
                            current_best = round(population[0]['Obj'], 2)
                            time_found = round(time.time() - start_ga, 3)
                        print(datetime.now(), "GENERATION", gen_counter, 'for orders', general['numOrders'])
                        # Crossover
                        poss_parents = list(range(pop_size))  # candidate parents
                        for ch in range(pop_size, pop_size * 2, 2):
                            population[ch], population[
                                ch + 1], child_exist = crossover(population, poss_parents, orders, cross, mut)

                            if child_exist:
                                new_off += 2
                                population[ch]['Obj_no_wip'], population[ch][
                                    'job_order'], loads, starting_times, completion_times, job_cell = ffs_assignment.ffs_assignment(
                                    population[ch]['Order'], stages, process, job_stage_elig, transTimes, orders,
                                    job_list, WIPs)

                                population[ch]['Obj'], population[ch]['start'], population[ch]['end'], population[ch][
                                    'sols'], cut_cp = ffs_cp_modules.ffs_wip(population[ch]['job_order'], stages,
                                                                             process, job_stage_elig, transTimes,
                                                                             orders, job_list, WIPs, job_cell,
                                                                             sol_cut_off - 1)
                                population[ch]['Time_found'] = round(time.time() - start_ga, 3)

                                if population[ch]['Obj'] < current_best:
                                    time_found = round(time.time() - start_ga, 3)

                                sum_executions += 1
                                sum_cut_cp += cut_cp
                                population[ch + 1]['Obj_no_wip'], population[ch + 1][
                                    'job_order'], loads, starting_times, completion_times, job_cell = ffs_assignment.ffs_assignment(
                                    population[ch + 1]['Order'], stages, process, job_stage_elig, transTimes, orders,
                                    job_list, WIPs)

                                population[ch + 1]['Obj'], population[ch + 1]['start'], population[ch + 1]['end'], \
                                    population[ch + 1]['sols'], cut_cp = ffs_cp_modules.ffs_wip(
                                    population[ch + 1]['job_order'], stages, process, job_stage_elig, transTimes,
                                    orders, job_list, WIPs, job_cell, sol_cut_off - 1)

                                if population[ch]['Obj'] < current_best:
                                    time_found = round(time.time() - start_ga, 3)

                                population[ch + 1]['Time_found'] = round(time.time() - start_ga, 3)
                                sum_executions += 1
                                sum_cut_cp += cut_cp

                        gen_counter += 1

                        # Survival

                        population = dict(sorted(population.items(), key=lambda x: x[1]['Obj'])[:pop_size])
                        population = {i: v for i, v in enumerate(population.values())}
                        sol_cut_off = round(population[pop_size - 1]['Obj'], 2)
                        current_best = round(population[0]['Obj'], 2)

                        print("SOL CUTOFF", sol_cut_off)
                        print("BEST", round(population[0]['Obj'], 2))
    sol_times = {}
    for key, item in population.items():
        sol_times[key] = population[key]['Time_found']
    solution_dict = dict(sorted(population.items(), key=lambda x: x[1]['Obj'])[:1])
    solution = solution_dict[0]
    cell_seq = {}
    for s in stages.keys():
        cell_seq[s] = {}
        for m in stages[s]:
            cell_seq[s][m] = ""
            for job in solution['job_order'][m]:
                cell_seq[s][m] += str(job) + ';'
    final_values = {
        'params': {'Pop_size': pop_size, 'Gens': generations, 'Gens_exec': gen_counter - 1, 'Cross': cross, 'Mut': mut},
        'metrics': {'Cmax': math.ceil(solution['Obj']), 'Cmax_no_wip': math.ceil(solution['Obj_no_wip'])},
        'seq': cell_seq, 'orders': solution['sols'], 'init_order': solution['Order'], 'sol_times': sol_times}

    end_ga = time.time()
    result_list.extend([pop_size, generations, gen_counter - 1, cross, mut, math.ceil(solution['Obj_no_wip']),
                        math.ceil(solution['Obj']), time_found, round(end_ga - start_ga, 3), sum_executions,
                        sum_cut_cp])

    final_values['run_time'] = round(end_ga - start_ga, 3)
    final_values['gens'] = gen_counter - 1

    print(datetime.now(), " - End of GA.")
    return final_values, result_list


def crossover(chromosomes, poss_parents, orders, cross, mut):
    # print (orders)
    # choose parents
    orders_list = list(orders.keys())
    # if you want to choose parents randomly:
    # p_1, p_2 = random.sample(poss_parents, 2)

    # the sum of all parent's makespan
    makespan_inverse_parent_sum = sum(1 / chromosomes[parent_pos]["Obj"] for parent_pos in poss_parents)

    # the selection probabilities of all possible parents (parents with less makespan have more chance to get picked)
    selection_probs = [(1 / chromosomes[parent_pos]["Obj"] / makespan_inverse_parent_sum) for parent_pos in
                       poss_parents]

    # check
    # for key, value in chromosomes.items():
    #    print(f"{key} -> {value['Obj']}")

    # print(selection_probs)
    # print(sum(selection_probs))
    # return

    # if you want to choose parents based on makespan (stochastic):
    p_1, p_2 = np.random.choice(poss_parents, replace=False, p=selection_probs, size=2)

    parent_1 = chromosomes[p_1]
    parent_2 = chromosomes[p_2]
    child_exist = True
    if random.random() < cross:
        # find splitting point on chromosomes
        split_pos = random.randint(1, min(len(parent_1['Order']), len(parent_2['Order'])) - 2)
        # create new chromosomes for children
        child_1 = {'Order': parent_1['Order'][:split_pos + 1] + parent_2['Order'][split_pos + 1:]}
        # rest_child_1 = {'Order': parent_2['Order'][split_pos + 1:], 'Perc': parent_2['Perc'][split_pos + 1:]}
        child_2 = {'Order': parent_2['Order'][:split_pos + 1] + parent_1['Order'][split_pos + 1:]}
        # rest_child_2 = {'Order': parent_1['Order'][split_pos + 1:], 'Perc': parent_1['Perc'][split_pos + 1:]}

        # fix child_1
        child_1 = fix_chromosomes(child_1, orders_list, split_pos)

        # fix child_2
        child_2 = fix_chromosomes(child_2, orders_list, split_pos)

        # Mutation

        if random.random() < mut:
            pos1 = random.randint(0, len(child_1['Order']) - 1)
            pos2 = random.choice(list(range(0, pos1)) + list(range(pos1 + 1, len(child_1['Order']) - 1)))
            child_1['Order'][pos1], child_1['Order'][pos2] = child_1['Order'][pos2], child_1['Order'][pos1]

        if random.random() < mut:
            pos1 = random.randint(0, len(child_2['Order']) - 1)
            pos2 = random.choice(list(range(0, pos1)) + list(range(pos1 + 1, len(child_2['Order']) - 1)))
            child_2['Order'][pos1], child_2['Order'][pos2] = child_2['Order'][pos2], child_2['Order'][pos1]

    else:
        child_1 = {'Obj': math.inf}
        child_2 = {'Obj': math.inf}
        child_exist = False
    # poss_parents = list(set(poss_parents) - set([p_1, p_2]))
    return child_1, child_2, child_exist


def fix_chromosomes(child, orders_list, split_pos):
    for i in orders_list:
        pos_i = np.where(np.array(child['Order']) == i)[0]
        if len(pos_i) == 0:
            child['Order'].insert(split_pos + 1, i)
        elif len(pos_i) > 1:
            while len(pos_i) > 1:
                del child['Order'][pos_i[0]]
                pos_i = np.where(np.array(child['Order']) == i)[0]

    return child


def spawning(size, orders):
    chromosomes = {}
    k = list(orders.keys())
    for i in range(size):
        seq = list(np.random.permutation(k))
        chromosomes[i] = {'Order': seq, 'Obj': 0}
    return chromosomes
