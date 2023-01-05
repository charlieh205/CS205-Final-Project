
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()
plt.rc('text', usetex=True)

with open("data/gcp_bench.csv", "r") as env_file:
    data = env_file.readlines()

os_data = []
cenv_data = []

for d in data:
    d = d.split(",")
    name = d[0] 
    batch_size = d[1]
    float_data = list(map(float, d[2:]))

    if name == "cchessenv":
        cenv_data.append((batch_size, np.mean(float_data)))
    else:
        os_data.append((batch_size, np.mean(float_data)))

x, y = zip(*cenv_data)
plt.plot(x, y, color='green')

x, y = zip(*os_data)
plt.plot(x, y, color='red')
plt.legend(["chessenv", "Open Spiel"])

plt.xlabel("Parallel Environments")
plt.ylabel("Time Per Step")
plt.savefig("plots/scaling.png")
