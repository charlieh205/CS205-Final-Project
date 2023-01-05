
import matplotlib.pyplot as plt
import numpy as np
from mllg import TrainStepInfo, ValidationInfo
import ast

import seaborn as sns
sns.set()
plt.rc('text', usetex=True)

with open("data/chess_rl_env.csv", "r") as env_file:
    data = env_file.readlines()

mean = {}
for d in data:
    d = d.split(",")
    name = d[0] 
    batch_size = d[1]

    float_data = list(map(float, d[2:]))

    mean[name] = 128.0 * np.mean(float_data)

delta =  {}
for n in mean.keys():
    print(mean[n])
    delta[n] = (mean[n] - mean['cchessenv'])

with open("data/chess_rl.log", "r") as perf_file:
    perf_data = perf_file.readlines()

train_data = []
eval_data = []
for p in perf_data:
    p = ast.literal_eval(p)
    if p['type'] == 'trainstep_info':
        train_data.append(TrainStepInfo.from_dict(p))
    else:
        eval_data.append(ValidationInfo.from_dict(p))

rolling_reward = []
times = []
for t in train_data:
    reward = list(filter(lambda x: x.loss_type == 'rolling_mean', t.losses))[0].loss
    rolling_reward.append(reward)
    times.append(t.time)

first_time = times[0]
for i in range(len(times)):
    times[i] = times[i] - first_time

colors = ['red', 'green']
i = 0
for n in ['pyspiel_sequential', 'cchessenv']:

    new_times = []
    for (idx, t) in enumerate(times):
        new_times.append(t + (idx + 1) * delta[n])

    plt.plot(new_times, rolling_reward, color=colors[i])
    i += 1

plt.title("Learning Speedup")
plt.legend(["OpenSpiel", "chessenv"])
plt.xlim([0, 4000])
plt.ylabel("Rolling Reward")
plt.xlabel("Time (s)")
plt.savefig("plots/learning_speedup.png")
