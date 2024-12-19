import json
# import numpy as np
import csv
import ffs_preprocessing
import ffs_heuristics
import time


def header_creation(mh):
    if mh == "GA":
        header = ["Instance", "Stages", "Orders", "Jobs", "Trial", "Pop_size", "Generations", "Gens_exec", "Cross",
                  "Mut", "nWIP", "wWIP", "Time_of_best", "Time", "Exec_CP", "Cut_CP", "File"]
    elif mh == "SA":
        header = ["Instance", "Stages", "Orders", "Jobs", "Trial", "Tc", "Tcry", "q", "Iter", "nWIP", "wWIP",
                  "Time_of_best", "Time", "File"]
    elif mh == "LS":
        header = ["Instance", "Stages", "Orders", "Jobs", "Trial", "max_Time", "nWIP", "wWIP", "Time_found", "Time",
                  "CPs_exec", "File"]
    elif mh == "TS":
        header = ["Instance", "Stages", "Orders", "Jobs", "Trial", "List_size", "iterations", "neighbors",
                  "max_Time", "nWIP", "wWIP", "Time_found", "Time", "Total_CPs", "File"]
    elif mh == "PSO":
        header = ["Instance", "Stages", "Orders", "Jobs", "Trial", "Swarm_size", "iterations", "inertia_weight",
                  "cognitive_weight", "social_weight", "nWIP", "wWIP", "Time_found", "Time", "Total_CPs",
                  "Iterations exec", "File"]
    else:
        header = ["Instance", "Stages", "Orders", "Jobs", "Trial"]
    return header


if __name__ == "__main__":
    Trials = 5
    sol_dict = {}

    f = open(r"input_benchmark_HFFS_v2.json", )
    data = json.load(f)

    f3 = open(r"ls_times.json")
    times_ls = json.load(f3)

    # the meta-heuristic to apply after the application of heur_status methods
    metaheur_to_run = {'TS': 100}

    header = header_creation(metaheur_to_run)
    with open("Experiments_FFS.csv", "a", newline='') as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(header)
    output_name = str(time.time())
    for instance_number in data.keys():
        instance = data[instance_number]
        general, stages, process, job_stage_elig, stage_job_elig, transTimes, orders, jobs, WIPs, cells_per_stage = ffs_preprocessing.data_preprocessing_identical(
            instance)
        sol_dict[instance_number] = {}
        for trial in range(Trials):
            if general['wip'] == 0:
                max_time = times_ls[instance_number]
                tot_results = [instance_number, general['numStages'], general['numOrders'], general['numJobs'], trial]

                print("--------------------------------", instance_number, trial)

                # heuristics
                heur_sols, results = ffs_heuristics.heuristics(general, stages, process, job_stage_elig, transTimes,
                                                               orders, jobs, WIPs, metaheur_to_run, [],
                                                               max_time)
                sol_dict[instance_number][f"Trial-{trial}"] = heur_sols
                tot_results.extend(results)
                filename = f"Solutions-{output_name}-{metaheur_to_run}.json"
                with open(filename, "w") as outfile:
                    json.dump(sol_dict, outfile, indent=4)
                tot_results.append(filename)
                with open("Experiments_FFS.csv", "a", newline='') as fp:
                    wr = csv.writer(fp, dialect='excel')
                    wr.writerow(tot_results)
