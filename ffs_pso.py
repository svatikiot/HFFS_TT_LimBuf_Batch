import random
import math
import ffs_assignment
import ffs_cp_modules
import time
import move
import numpy as np
import copy


def particle_swarm(data_for_cost_calculation):
    def cost(sequence, data_for_cost_calculation):
        stages = data_for_cost_calculation["stages"]
        job_stage_elig = data_for_cost_calculation["job_stage_elig"]
        process = data_for_cost_calculation["process"]
        transTimes = data_for_cost_calculation["transTimes"]
        orders = data_for_cost_calculation["orders"]
        WIPs = data_for_cost_calculation["WIPs"]
        job_list = data_for_cost_calculation["job_list"]

        big_M = 10000

        C_max, job_order, loads, starting_times, completion_times, job_cell = ffs_assignment.ffs_assignment(sequence,
                                                                                                            stages,
                                                                                                            process,
                                                                                                            job_stage_elig,
                                                                                                            transTimes,
                                                                                                            orders,
                                                                                                            job_list,
                                                                                                            WIPs)

        C_max_wip, starting_times, completion_times, sols, cut_cp = ffs_cp_modules.ffs_wip(job_order, stages, process,
                                                                                           job_stage_elig, transTimes,
                                                                                           orders, job_list, WIPs,
                                                                                           job_cell, big_M)

        return C_max_wip, sols, job_order, C_max

    def get_sequence_of_position(position):
        # produce the sequence based on the SPV rule
        # where index 0 will have the order mapped
        # to the first minarg of the position vector,
        # index 1 the order mapped to the second minarg etc.
        # (based on Dubey & Gupta, 2017 with proper modifications)
        position_copy = copy.deepcopy(position)
        sequence = []

        for _ in range(len(position)):
            spv = np.argmin(position_copy)
            position_copy[spv] = np.inf
            sequence.append(orders[spv])

        return sequence

    def produce_swarm(n_particles):
        particles = {}

        produced_positions = set()

        for particle_id in range(n_particles):
            # produce a random position
            particle_position = np.random.uniform(init_position_range[0], init_position_range[1], len(orders))

            # avoid overlap on initial positions of particles
            while str(particle_position) in produced_positions:
                particle_position = np.random.uniform(init_position_range[0], init_position_range[1], len(orders))
            produced_positions.add(str(particle_position))

            # compute the sequence of the position
            particle_sequence = get_sequence_of_position(particle_position)

            # compute the cost of the sequence
            C_max_wip, sols, job_order, C_max_no_wip = cost(particle_sequence, data_for_cost_calculation)
            # build the particle
            particles[particle_id] = {"sequence": particle_sequence, "position": particle_position,
                                      "C_max_wip": C_max_wip,
                                      "velocity": np.array([0 for _ in range(len(particle_position))]),
                                      "pbest": particle_position.copy(), 'C_max_no_wip': C_max_no_wip, "sols": sols,
                                      "job_order": job_order}

        return particles

    def get_gbest(particles):
        best_particle = min(particles.values(), key=lambda p: p["C_max_wip"])
        return best_particle["position"], best_particle["sequence"], best_particle["C_max_wip"]

    def position_distance(pos1, pos2):
        # maybe use sum(pos1 - pos2) to result
        # in a discrete number instead of a vector.
        return pos1 - pos2  # maybe square?

    def velocity_update_of(particle):
        r1 = random.uniform(0, 1)
        r2 = random.uniform(0, 1)
        particle_position = particle["position"]
        updated_velocity = (inertia_weight * particle["velocity"] + r1 * cognitive_weight * (
            position_distance(particle["pbest"], particle_position)) + r2 * social_weight * (
                                position_distance(gbest, particle_position)))
        # enforce upper and lower bound limits on velocity values
        for v_index, v_value in enumerate(updated_velocity.copy()):
            if v_value > v_max:
                updated_velocity[v_index] = v_max
            elif v_value < v_min:
                updated_velocity[v_index] = v_min

        return updated_velocity

    def update_positions(particles):
        counter = 0
        for particle in particles.values():
            old_particle_position = particle["position"]
            old_particle_cost = particle["C_max_wip"]
            particle["position"] = particle["position"] + particle["velocity"]

            if str(particle["position"]) == str(old_particle_position):
                # no need to update anything
                continue

            particle["sequence"] = get_sequence_of_position(particle["position"])
            particle["C_max_wip"], particle["sols"], particle["job_order"], particle["C_max_no_wip"] = cost(
                particle["sequence"], data_for_cost_calculation)
            counter += 1
            # update pbest if needed
            if particle["C_max_wip"] < old_particle_cost:
                particle["pbest"] = particle["position"]
        return counter

    iterations = 25
    swarm_size = 20
    v_min = -4  # lower bound for velocity values
    v_max = 4  # upper bound for velocity values
    inertia_weight = 0.9
    cognitive_weight = 2
    social_weight = 2
    init_position_range = (0, 4)  # the range of the initial position values
    counter = swarm_size
    final_values = {'params': {'swarm_size': swarm_size, 'iterations': iterations, 'inertia_w': inertia_weight,
                               'cognitive_w': cognitive_weight, 'social_w': social_weight}}
    results = [swarm_size, iterations, inertia_weight, cognitive_weight, social_weight]
    start_pso = time.time()
    orders = list(data_for_cost_calculation["orders"].keys())
    # can be 2 * sequences dimensions (Tasgetiren et al, 2004)

    particles = produce_swarm(swarm_size)
    time_found = round(time.time() - start_pso, 3)
    gbest, best_sequence, best_cost = get_gbest(particles)
    t = 0
    while t < iterations and time.time() - start_pso <= 3600:
        # gbest, g_sequence, g_cost = get_gbest(particles)
        print(counter)

        for particle in particles.values():
            particle["velocity"] = velocity_update_of(particle)

        counter += update_positions(particles)

        gbest, g_sequence, g_cost = get_gbest(particles)

        if g_cost < best_cost:
            time_found = round(time.time() - start_pso, 3)
            best_cost = g_cost
            best_sequence = g_sequence
            print(f"new global best: {best_cost}")

        t += 1
    total_time = round(time.time() - start_pso, 3)
    solution = dict(sorted(particles.items(), key=lambda x: x[1]['C_max_wip']))[0]
    final_values['metrics'] = {'C_max_wip': solution['C_max_wip'], 'C_max_no_wip': solution['C_max_no_wip']}
    final_values['init_order'] = solution['sequence']
    final_values['orders'] = solution['sols']
    final_values['run_time'] = total_time
    final_values['total_CPs'] = counter
    results.extend([solution['C_max_no_wip'], solution['C_max_wip'], time_found, total_time, counter])
    return final_values, results
