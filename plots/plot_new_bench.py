
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set()
plt.rc('text', usetex=True)

with open("data/new_log_data.csv", "r") as log_data:
    data = log_data.readlines()

inf_times, step_times, data_collect_times, opt_times = [], [], [], []
for d in data:
    d = d.rstrip()
    inf_time, step_time, data_collect, opt_time = list(map(float, d.split(",")))
    inf_times.append(inf_time)
    step_times.append(step_time)
    data_collect_times.append(data_collect)
    opt_times.append(opt_time)

inf_time = 128 * np.mean(inf_times)
step_time = 128 * np.mean(step_times)
data_collect = np.mean(data_collect_times)
opt_time = np.mean(opt_times)

plt.figure(figsize=(7, 5))
plt.bar(['Env Step\n(OpenSpiel)'], [128.0 * 0.038], color='red') # Computed in plot_perf
plt.bar(['Env Step\n(chessenv)'], step_time ,color='green') 
plt.bar(['Inference', 'BackProp'], [inf_time, opt_time], color=['black', 'black'])

plt.title("Benchmarking RL System Time Per Update, Batch Size of 16834")
plt.ylabel("Time (s)")
plt.savefig("plots/system_perf.png")
