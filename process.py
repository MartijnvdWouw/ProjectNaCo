# GOAL
# 1. Number of finished cells per time step
# 2. Average distance to finish zone of all cells per time step
# 3. Average time spent 'inefficient' per cell per time step (boxplot)

from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import re
from collections import defaultdict

DOWN_TIME_BUFFER = 0
CHEMOKINE_IDENTIFIER = "CHEMOKINES"

PARAMS_EAT = [6,7,8,9,10]
PARAMS_LAMBDA = [50,100,150]
PARAMS_SEED = [1,2,3]

GRADIENT_IDENTIFIER = "GRADIENT"

def read_all_results(path: Path):
    return {p: read_results(p) for p in path.iterdir()}
    # #for e in PARAMS_EAT:
    #  #   for l in PARAMS_LAMBDA:

    # for s in PARAMS_SEED:
    #     #file_name = file_name + "_" + s + ".txt"      #_{l}_{e}"

    #     file_path = "{}/{}{}.txt".format(path, file_name, s)
    #     print("reading " + file_path)
    #     r = read_results(file_path)
    #     accumulator.append(r)
    # return accumulator
    
def group(path: Path):
    seed_re = re.compile(r"_s\d+")

    groups = defaultdict(list)

    for p in path.iterdir():
        key = seed_re.sub("_s", p.name)
        groups[key].append(p)

    return groups

def read_all_results_group(group):
    return {k: [read_results(p) for p in v]  for k, v in group.items()}


def read_results(file_name: Path):
    cell_data = []
    kill_data = []
    chemokine_data = []
    gradient_data: dict[str, list] = {}


    with open(file_name) as file:
        number_of_cells = int(file.readline())
        number_of_steps = int(file.readline())

        for line in file:
            res = line.split()

            if (len(res) > 0 and res[0] == CHEMOKINE_IDENTIFIER):
                chemokine_data.append((int(res[1]), float(res[2])))
            elif (len(res) > 0 and res[0] == GRADIENT_IDENTIFIER):
                id = res[2]
                value = float(res[3])
                if id in gradient_data:
                    gradient_data[id].append(value)
                else:
                    gradient_data[id] = [value]
            elif (len(res) == 5):
                cell_data.append({
                    "step": int(res[0]),
                    "id": int(res[1]),
                    "kind": int(res[2]),
                    "x": round(float(res[3])),
                    "y": round(float(res[4]))
                })
            elif (len(res) == 2):
                kill_data.append((int(res[0]), int(res[1])))

    return number_of_cells, number_of_steps, cell_data, kill_data, chemokine_data, gradient_data

def read_distances(file_name: str): 
    with open(file_name) as file:
        grid_size = file.readline().split()
        distances = [[-1 for _ in range(int(grid_size[1]))] for _ in range(int(grid_size[0]))]

        for line in file:
            res = line.split()
            pix = {
                "x": int(res[0]),
                "y": int(res[1]),
                "dist": int(res[2])
            }
            if (pix["dist"] >= 0):
                distances[pix["x"]][pix["y"]] = pix["dist"]
            
    return distances
            
def kill_counts(nr_of_steps: int, kills: list[tuple[int, int]]):
    counts = []
    current_count = 0
    
    for step in range(nr_of_steps):
        if (current_count < len(kills)):
            if (kills[current_count][0] == step):
                current_count += 1

        counts.append(current_count)   
    return counts

def cell_distances(cell_data, distances):
    newlist = sorted(cell_data, key=lambda x: (x["id"], x["step"]))
    id_max = newlist[-1]["id"]
    
    distanceList = []
    for i in range(1,id_max+1):
        f = list(filter(lambda d: d['id'] == i, newlist))
        d_list = []
        for j in range(len(f)):
            d = distances[f[j]["x"]][f[j]["y"]]
            d_list.append(d)
        newlist[i]
        distanceList.append(d_list)
    #for i in range(1, id_max+1):
        #print("cell ",i-1,": ", distanceList[i-1])
    return distanceList

def down_time(cell_distances, n_steps):
    down_list = []
    for i in range(1,len(cell_distances)):
        down_time = 0
        last_best = cell_distances[i][0]
        for j in range(len(cell_distances[i])):
            if cell_distances[i][j] > (last_best) + DOWN_TIME_BUFFER:
                down_time+=1
            else :
                if (cell_distances[i][j] < last_best):
                    last_best = cell_distances[i][j]
        down_list.append(down_time)

    down_list = np.array(down_list)
    return down_list / n_steps * 100

def avg_distances(number_of_steps: int, cell_distances: list[list[int]], count_kills: bool):
    avg = []
    current_index = 0
    for _ in range(number_of_steps):
        count = 0
        total = 0

        for cell in range(len(cell_distances)):
            if (current_index < len(cell_distances[cell])):
                count += 1
                total += cell_distances[cell][current_index]

        if (count_kills):
            avg.append(total/len(cell_distances))
        else: 
            if count < 1:
                avg.append(0)
            else :
                avg.append(total/(count))
        current_index += 1
    return avg

def process_group_kills(results: List[Tuple]):
    (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data, gradient_data) = results[0]
    kc = kill_counts(nr_of_steps, kill_data)
    acc = np.array(kc)

    for r in results[1:]:
        (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data, gradient_data) = r
        kc = kill_counts(nr_of_steps, kill_data)
        acc += (np.array(kc))

    avg = acc / len(results)
    avg_list = avg.tolist()
    return avg_list


def process_avg_kills(results: Dict[str, List[Tuple]]):
    keys = list(results.keys())
    def data(i):
        return results[keys[i]]

    min_key = list(results.keys())[0]
    max_key = list(results.keys())[0]
    min_k = process_group_kills(data(0))
    max_k = process_group_kills(data(0))
    acc = np.zeros(len(process_group_kills(data(0))))
    for k, v in results.items():
        avg = process_group_kills(v)
        if avg[-1] < min_k[-1]:
            min_k = avg
            min_key = k
        if avg[-1] > max_k[-1]:
            max_k = avg
            max_key = k
        acc += (np.array(avg))
    
    avg = acc / len(results)
    avg_list = avg.tolist()
    print(f"Kills:\t\tmin:\t{str(min_key)}\tmax:\t{str(max_key)}\tamounts: {min_k[-1]}\t{avg[-1]}\t{max_k[-1]}")
    plot_kills(avg_list, min_k, max_k)

def process_group_distances(distances, results: List[Tuple]):
    (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data, gradient_data) = results[0]
    avg_d = avg_distances(nr_of_steps, cell_distances(cell_data, distances), True)
    acc = np.array(avg_d)

    for r in results[1:]:
        (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data, gradient_data) = r
        avg_d = avg_distances(nr_of_steps, cell_distances(cell_data, distances), True)
        # acc1 += np.array(avg_d1)
        acc += np.array(avg_d)

    avg = acc / len(results)
    avg_list = avg.tolist()
    return avg_list


def process_avg_distances(distances, results: Dict[str, List[Tuple]]):
    keys = list(results.keys())
    def data(i):
        return results[keys[i]]
    
    min_d = process_group_distances(distances, data(0))
    max_d = process_group_distances(distances, data(0))
    min_key = list(results.keys())[0]
    max_key = list(results.keys())[0]
    acc = np.zeros(len(process_group_distances(distances, data(0))))

    for k, v in results.items():
        avg = process_group_distances(distances, v)
        if avg[-1] < min_d[-1]:
            min_d = avg
            min_key = k
        if avg[-1] > max_d[-1]:
            max_d = avg
            max_key = k
        acc += (np.array(avg))
    
    avg = acc / len(results)
    avg_list = avg.tolist()
    
    print(f"Distances:\tmin:\t{str(min_key)}\tmax:\t{str(max_key)}\tamounts: {min_d[-1]}\t{avg[-1]}\t{max_d[-1]}")
    plot_dist_finish(None, avg_list, min_d, max_d)

def process_group_downtimes(distances, results: List[Tuple]):
    dt = []

    for r in results:
        (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data, gradient_data) = r
        dists = cell_distances(cell_data, distances)
        x = down_time(dists, nr_of_steps)
        dt.extend(x)
    
    return dt


def process_all_downtimes(distances, results: Dict[str, List[Tuple]]):
    keys = list(results.keys())
    def data(i):
        return results[keys[i]]

    dt0 = process_group_downtimes(distances, data(0))
    avgs = [sum(dt0) / len(dt0)]
    min_d = sum(dt0) / len(dt0)
    max_d = sum(dt0) / len(dt0)
    mi = dt0
    ma = dt0

    min_key = list(results.keys())[0]
    max_key = list(results.keys())[0]

    for k, v in results.items():
        dt2 = process_group_downtimes(distances, v)
        mean = sum(dt2) / len(dt2)
        if mean < min_d:
            min_d = mean
            min_key = k
            mi = dt2
        if mean > max_d:
            max_d = mean
            max_key = k
            ma = dt2
            
        avgs.append(mean)

    print(f"Downtimes:\tmin:\t{str(min_key)}\tmax:\t{str(max_key)}\tamounts: {min_d}\t{sum(avgs)/len(avgs)}\t{max_d}")
    plot_down_time([avgs, mi, ma])

def plot_dist_finish(avg_dists1, avg_dists2, min, max):
    plt.figure(figsize=(10, 5))
    plt.plot(np.arange(len(avg_dists2)), avg_dists2, alpha=0.3, linewidth=2, color="blue", label="Average distance")
    #plt.plot(np.arange(len(avg_dists1)), avg_dists1, alpha=0.3, linewidth=2, color="blue", label="Average distance without kills")
    plt.plot(np.arange(len(min)), min, alpha=0.3, linewidth=2, color="green", label="Best average distance")
    plt.plot(np.arange(len(max)), max, alpha=0.3, linewidth=2, color="red", label="Worst average distance")

    plt.xlim(left=0)
    plt.ylim(bottom=0, top=104)
    plt.xlabel("Steps")
    plt.ylabel("Average distance")
    plt.title("Average distance to finish at each Monte Carlo step")
    plt.legend()
    plt.grid(True)
    plt.show()
    
def plot_kills(kill_counts: list[int], min, max):
    plt.figure(figsize=(10, 5))
    plt.step(np.arange(len(kill_counts)), kill_counts, where="post", alpha=0.3, linewidth=2, label="Finish count")
    plt.step(np.arange(len(min)), min, where="post", alpha=0.3, linewidth=2, label="Worst case finish count", color= "red")
    plt.step(np.arange(len(max)), max, where="post", alpha=0.3, linewidth=2, label="Best case finish count", color="green")
    plt.xlim(left=0)
    plt.ylim(bottom=0, top=20)
    plt.xlabel("Steps")
    plt.ylabel("Finished cells")
    plt.title("Number of finished cells at each Monte Carlo step")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_down_time(down_times):
    names = ["Avg (45)", "Best (1)", "Worst (1)"]
    plt.boxplot(down_times,  showmeans=True, meanprops={"marker":"x"})
    plt.title("Movement efficiency")
    plt.ylabel("Downtime (% of steps)")
    plt.grid(True)
    plt.show()


def process_group_chemokines(results: List[Tuple]):
    (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data, gradient_data) = results[0]
    if (len(chemokine_data) == 0): return []
    acc = np.array([c[1] for c in chemokine_data])

    for r in results[1:]:
        (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data, gradient_data) = r
        acc += np.array([c[1] for c in chemokine_data])

    avg = acc / len(results)
    avg_list = avg.tolist()
    return avg_list

def process_chemokines(results: Dict[str, List[Tuple]]):
    keys = list(results.keys())
    def data(i):
        return results[keys[i]]
    
    min_d = process_group_chemokines(data(0))
    max_d = process_group_chemokines(data(0))
    if min_d == []: return
    min_key = list(results.keys())[0]
    max_key = list(results.keys())[0]
    acc = np.zeros(len(process_group_chemokines(data(0))))

    for k, v in results.items():
        avg = process_group_chemokines(v)
        if avg == []: return
        if avg[-1] < min_d[-1]:
            min_d = avg
            min_key = k
        if avg[-1] > max_d[-1]:
            max_d = avg
            max_key = k
        acc += (np.array(avg))
    
    avg = acc / len(results)
    avg_list = avg.tolist()
    
    print(f"Chemokines:\tmin:\t{str(min_key)}\tmax:\t{str(max_key)}\tamounts: {min_d[-1]}\t{avg[-1]}\t{max_d[-1]}")
    plot_chemokines(avg_list, min_d, max_d)

def plot_chemokines(avg1, min_d, max_d):
    plt.figure(figsize=(10, 5))
    plt.plot(np.arange(len(avg1)), avg1, alpha=0.3, linewidth=2, label="Average total available chemokines")
    plt.step(np.arange(len(min_d)), min_d, where="post", alpha=0.3, linewidth=2, label="Minimal total available chemokines", color= "red")
    plt.step(np.arange(len(max_d)), max_d, where="post", alpha=0.3, linewidth=2, label="Maximal total available chemokines", color="green")
    plt.xlabel("Steps")
    plt.ylabel("Number of chemokines")
    plt.title("Average total chemokines in the grid per Monte Carlo step")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_gradient(gradient: dict[str, list]):
    plt.figure(figsize=(10, 5))
    for k, data in gradient.items():
        plt.plot(np.arange(len(data)), data, alpha=0.3, linewidth=2, label=f"Experienced gradient {k}")
    plt.xlabel("Steps")
    plt.ylabel("Gradient")
    plt.title("Experienced gradient over time")
    plt.grid(True)
    plt.show()

def main():
    # results = read_all_results(Path("results/blue"))
    distances = read_distances("mediumMaze.txt")

    r = read_all_results_group(group(Path("results/blue")))
    
    # Plot 1
    process_avg_kills(r)

    # Plot 2
    process_avg_distances(distances, r)
    
    # Plot 3    
    process_all_downtimes(distances, r)

    # Plot 4
    process_chemokines(r)

    # set key to the key of the group you want to inquire
    # second index is the seed
    # last index DO NOT CHANGE!
    # key = list(r.keys())[0]
    # plot_gradient(r[key][0][-1])
        
    
if __name__=="__main__":
    main()