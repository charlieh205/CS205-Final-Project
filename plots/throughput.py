
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()
plt.rc('text', usetex=True)

with open("data/gcp_bench.csv", "r") as env_file:
    data = env_file.readlines()

mean = {'cchessenv': {}, "pyspiel_sequential": {}}
for d in data:
    d = d.split(",")
    name = d[0] 
    batch_size = d[1]
    float_data = list(map(float, d[2:]))

    mean[name][batch_size] = np.mean(float_data)

delta =  {}
for n in mean['cchessenv'].keys():
    delta[int(n)] = (mean['pyspiel_sequential'][n] - mean['cchessenv'][n])


actual_time = []
ideal_time = []
pyspiel_time = []
n_envs = [16, 32, 64, 128, 256, 512, 1024]
for n in n_envs:
    with open(f"data/log_{n}.txt", "r") as log_data:
        data = log_data.readlines()
    
    inf_times, step_times, data_collect_times, opt_times = [], [], [], []
    for d in data:
        d = d.rstrip()
        inf_time, step_time, data_collect, opt_time = list(map(float, d.split(",")))
        inf_times.append(inf_time)
        step_times.append(step_time)
        data_collect_times.append(data_collect)
        opt_times.append(opt_time)
    
    data_collect = np.mean(data_collect_times)
    opt_time = np.mean(opt_times)
    
    total = data_collect + opt_time

    ideal_total = opt_time + (data_collect - (16384 / n) * np.mean(step_time))
    pyspiel = opt_time + (data_collect + (16384 / n) * delta[n])

    actual_time.append(1/total)
    ideal_time.append(1/ideal_total)
    pyspiel_time.append(1/pyspiel)

plt.title("Efficiency for Batches Of Size 16834")
plt.ylabel("Batches per Second (b/s)")
plt.xlabel("Number of Environments")
plt.plot(n_envs, pyspiel_time, color='red')
plt.plot(n_envs, actual_time, color='green')
plt.plot(n_envs, ideal_time, color='black', ls='--')
plt.legend(["OpenSpiel", "chessenv", "Ideal"])
plt.savefig("plots/throughput.png")
