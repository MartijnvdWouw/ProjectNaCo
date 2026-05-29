# GOAL
# 1. Number of finished cells per time step
# 2. Average distance to finish zone of all cells per time step
# 3. Average time spent 'inefficient' per cell per time step (boxplot)

import matplotlib.pyplot as plt
import numpy as np

DOWN_TIME_BUFFER = 0
CHEMOKINE_IDENTIFIER = "CHEMOKINES"

PARAMS_EAT = [6,7,8,9,10]
PARAMS_LAMBDA = [50,100,150]
PARAMS_SEED = [1,2,3]


def read_all_results(path: str, file_name:str):
    accumulator = []
    #for e in PARAMS_EAT:
     #   for l in PARAMS_LAMBDA:

    for s in PARAMS_SEED:
        #file_name = file_name + "_" + s + ".txt"      #_{l}_{e}"

        file_path = "{}/{}{}.txt".format(path, file_name, s)
        print("reading " + file_path)
        r = read_results(file_path)
        accumulator.append(r)
    return accumulator
    


def read_results(file_name: str):
    cell_data = []
    kill_data = []
    chemokine_data = []

    with open(file_name) as file:
        number_of_cells = int(file.readline())
        number_of_steps = int(file.readline())

        for line in file:
            res = line.split()

            if (len(res) > 0 and res[0] == CHEMOKINE_IDENTIFIER):
                chemokine_data.append((int(res[1]), float(res[2])))
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
    return number_of_cells, number_of_steps, cell_data, kill_data, chemokine_data

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

def down_time(cell_distances):
    down_list = []
    for i in range(1,len(cell_distances)):
        down_time = 0
        last_best = cell_distances[i][0]
        for j in range(len(cell_distances[i])):
            if cell_distances[i][j] > (last_best) + DOWN_TIME_BUFFER:
                down_time+=1
            else :
                if (cell_distances[i][j] != last_best):
                    print(i, " with ", j, ": ", last_best)
                if (cell_distances[i][j] < last_best):
                    last_best = cell_distances[i][j]
        down_list.append(down_time)
    return down_list

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

def process_avg_kills(results):
    (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data) = results[0]
    acc = np.array(kill_counts(nr_of_steps, kill_data))
    for i in range(1,len(PARAMS_SEED)):
        (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data) = results[i]
        kc = kill_counts(nr_of_steps, kill_data)
        acc += (np.array(kc))
    avg = acc / 3
    avg_list = avg.tolist()
    plot_kills(avg_list)

def plot_dist_finish(avg_dists1, avg_dists2):
    plt.figure(figsize=(10, 5))
    plt.plot(np.arange(len(avg_dists2)), avg_dists2, alpha=0.3, linewidth=2, color="red", label="Average distance with kills")
    plt.plot(np.arange(len(avg_dists1)), avg_dists1, alpha=0.3, linewidth=2, color="blue", label="Average distance without kills")
    plt.xlim(left=0)
    plt.ylim(bottom=0, top=104)
    plt.xlabel("Steps")
    plt.ylabel("Average distance")
    plt.title("Average distance to finish at each Monte Carlo step")
    plt.legend()
    plt.grid(True)
    plt.show()
    
def plot_kills(kill_counts: list[int]):
    plt.figure(figsize=(10, 5))
    plt.step(np.arange(len(kill_counts)), kill_counts, where="post", alpha=0.3, linewidth=2, label="Kill count")
    plt.xlim(left=0)
    plt.ylim(bottom=0, top=20)
    plt.xlabel("Steps")
    plt.ylabel("Killed cells")
    plt.title("Number of kills at each Monte Carlo step")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_down_time(down_times):
    plt.boxplot(down_times)
    plt.show()

def plot_chemokines(chemokines):
    data = [cd[1] for cd in chemokines]
    plt.figure(figsize=(10, 5))
    plt.plot(np.arange(len(data)), data, alpha=0.3, linewidth=2, label="Total available chemokines")
    plt.xlabel("Steps")
    plt.ylabel("Total available chemokines")
    plt.title("Total available chemokines in the grid per Monte Carlo step")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    #(nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data) = read_results(, "base1.txt")
    results = read_all_results("results/base","base")
    distances = read_distances("mediumMaze.txt")

    # Plot 1
    #plot_kills(kill_counts(nr_of_steps, kill_data))
    process_avg_kills(results)

    (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data) = results[0]
    print(cell_distances(cell_data, distances))
    acc1 = np.array(avg_distances(nr_of_steps, cell_distances(cell_data, distances), False))
    acc2 = np.array(avg_distances(nr_of_steps, cell_distances(cell_data, distances), True))
    
    for i in range(1,len(PARAMS_SEED)):
        (nr_of_cells, nr_of_steps, cell_data, kill_data, chemokine_data) = results[i]
        acc1 += np.array(avg_distances(nr_of_steps, cell_distances(cell_data, distances), False))
        acc2 += np.array(avg_distances(nr_of_steps, cell_distances(cell_data, distances), True))
    avg1 = acc1 / 3
    avg2 = acc2 / 3
    avg_dists1 = avg1.tolist()
    avg_dists2 = avg2.tolist()


    #dists = cell_distances(cell_data, distances)
    #avg_dists1 = avg_distances(nr_of_steps, dists, False)
    #avg_dists2 = avg_distances(nr_of_steps, dists, True)

    # Plot 2
    plot_dist_finish(avg_dists1, avg_dists2)
    
    down_times = down_time(dists)
    #print(down_times)

    # Plot 3
    plot_down_time(down_times)

    plot_chemokines(chemokine_data)
    

if __name__=="__main__":
    main()