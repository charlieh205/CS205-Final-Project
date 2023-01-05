
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plt.rcParams['text.usetex'] = True

def read_data(path):
    with open(path, 'r') as file_data:
        lines = file_data.readlines()
    
    data = {}
    for l in lines:
        l = l.rstrip()
        n_env, *vals = l.split(",")
        n_env = int(n_env)
        vals = list(map(float, vals))
        data[n_env] = vals
    return data

def get_mean(data):
    x = list(data.keys())
    y = [np.mean(data[k]) for k in x]
    return x, y

def get_std(data):
    x = list(data.keys())
    top = [np.mean(data[k]) + np.std(data[k]) for k in x]
    bottom = [np.mean(data[k]) - np.std(data[k]) for k in x]
    return x, top, bottom

def plot_one():
    seq_data = read_data("data/seq_data_python.csv")
    stack_data = read_data("data/stack_data_python.csv")
    cpp_seq_data = read_data("data/seq_data_cpp.csv")
    cpp_stack_data = read_data("data/stack_data_cpp.csv")

    plt.title("Runtime For Number of Environments")
    plt.xlabel("Number of Environments")
    plt.ylabel("Time Per Step (s)")

    plt.plot(*get_mean(seq_data), color='red')
    plt.plot(*get_mean(stack_data), color='blue')
    plt.plot(*get_mean(cpp_seq_data), color='green')
    plt.plot(*get_mean(cpp_stack_data), color='orange')
    plt.legend(["Sequential (python) ($\mu \pm \sigma$)", "Parallel (python) ($\mu \pm \sigma$)", "Sequential (C++) ($\mu \pm \sigma$)", "OpenMP (C++) ($\mu \pm \sigma$)"])

    plt.scatter(*get_mean(seq_data), color='red', marker='x')
    plt.fill_between(*get_std(seq_data), alpha=0.5, color='red')
    
    plt.scatter(*get_mean(stack_data), color='blue', marker='x')
    plt.fill_between(*get_std(stack_data), alpha=0.5, color='blue')

    plt.scatter(*get_mean(cpp_seq_data), color='green', marker='x')
    plt.fill_between(*get_std(cpp_seq_data), alpha=0.5, color='green')

    plt.scatter(*get_mean(cpp_stack_data), color='orange', marker='x')
    plt.fill_between(*get_std(cpp_stack_data), alpha=0.5, color='orange')
    plt.savefig("plots/python_runtime.png")

def to_throughput(data):
    for k in data.keys():
        data[k] = [k / x for x in data[k]]
    return data

def plot_two():
    seq_data = to_throughput(read_data("data/seq_data_python.csv"))
    stack_data = to_throughput(read_data("data/stack_data_python.csv"))
    cpp_seq_data = to_throughput(read_data("data/seq_data_cpp.csv"))
    cpp_stack_data = to_throughput(read_data("data/stack_data_cpp.csv"))

    plt.title("Throughput For Number of Environments")
    plt.xlabel("Number of Environments")
    plt.ylabel("Boards Per Second (b/s)")

    plt.plot(*get_mean(seq_data), color='red')
    plt.plot(*get_mean(stack_data), color='blue')
    plt.plot(*get_mean(cpp_seq_data), color='green')
    plt.plot(*get_mean(cpp_stack_data), color='orange')
    plt.legend(["Sequential (python) ($\mu \pm \sigma$)", "Parallel (python) ($\mu \pm \sigma$)", "Sequential (C++) ($\mu \pm \sigma$)", "OpenMP (C++) ($\mu \pm \sigma$)"])

    plt.scatter(*get_mean(seq_data), color='red', marker='x')
    plt.fill_between(*get_std(seq_data), alpha=0.5, color='red')
    
    plt.scatter(*get_mean(stack_data), color='blue', marker='x')
    plt.fill_between(*get_std(stack_data), alpha=0.5, color='blue')

    plt.scatter(*get_mean(cpp_seq_data), color='green', marker='x')
    plt.fill_between(*get_std(cpp_seq_data), alpha=0.5, color='green')

    plt.scatter(*get_mean(cpp_stack_data), color='orange', marker='x')
    plt.fill_between(*get_std(cpp_stack_data), alpha=0.5, color='orange')
    plt.savefig("plots/python_throughput.png")

def to_time_per_batch(data):
    for k in [1, 2, 4, 8, 16, 32]:
        data.pop(k)
    
    for k in [64, 128, 256, 512]:
        data[k] = [(512 / k) * x for x in data[k]]

    return data

def plot_three():
    seq_data = to_time_per_batch(read_data("data/seq_data_python.csv"))
    stack_data = to_time_per_batch(read_data("data/stack_data_python.csv"))
    cpp_seq_data = to_time_per_batch(read_data("data/seq_data_cpp.csv"))
    cpp_stack_data = to_time_per_batch(read_data("data/stack_data_cpp.csv"))

    plt.title("Time Per Batch For Number of Environments")
    plt.xlabel("Number of Environments")
    plt.ylabel("Time Per Batch of 512 (s)")

    plt.plot(*get_mean(seq_data), color='red')
    plt.plot(*get_mean(stack_data), color='blue')
    plt.plot(*get_mean(cpp_seq_data), color='green')
    plt.plot(*get_mean(cpp_stack_data), color='orange')
    plt.legend(["Sequential (python) ($\mu \pm \sigma$)", "Parallel (python) ($\mu \pm \sigma$)", "Sequential (C++) ($\mu \pm \sigma$)", "OpenMP (C++) ($\mu \pm \sigma$)"])

    plt.scatter(*get_mean(seq_data), color='red', marker='x')
    plt.fill_between(*get_std(seq_data), alpha=0.5, color='red')
    
    plt.scatter(*get_mean(stack_data), color='blue', marker='x')
    plt.fill_between(*get_std(stack_data), alpha=0.5, color='blue')

    plt.scatter(*get_mean(cpp_seq_data), color='green', marker='x')
    plt.fill_between(*get_std(cpp_seq_data), alpha=0.5, color='green')

    plt.scatter(*get_mean(cpp_stack_data), color='orange', marker='x')
    plt.fill_between(*get_std(cpp_stack_data), alpha=0.5, color='orange')
    plt.savefig("plots/python_512.png")

def to_model_adj_throughput(data, model_data):

    for (ms, k) in zip(model_data, data.keys()):
        data[k] = [1/ ( (512 / k) * (x + ms) ) for x in data[k]]

    return data

def plot_four():
    data = read_data("data/model_perf_a100.txt")
    _, inf_time = get_mean(data)

    seq_data = to_model_adj_throughput(read_data("data/seq_data_python.csv"), inf_time)
    stack_data = to_model_adj_throughput(read_data("data/stack_data_python.csv"), inf_time)
    cpp_seq_data = to_model_adj_throughput(read_data("data/seq_data_cpp.csv"), inf_time)
    cpp_stack_data = to_model_adj_throughput(read_data("data/stack_data_cpp.csv"), inf_time)

    theory_max = to_model_adj_throughput({k: [0.0] for k in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]}, inf_time)

    plt.title("Batch Throughput For Number of Environments")
    plt.xlabel("Number of Environments")
    plt.ylabel("Batches Per Second (b/s)")

    plt.plot(*get_mean(seq_data), color='red')
    plt.plot(*get_mean(stack_data), color='blue')
    plt.plot(*get_mean(cpp_seq_data), color='green')
    plt.plot(*get_mean(cpp_stack_data), color='orange')
    plt.legend(["Sequential (python) ($\mu \pm \sigma$)", "Parallel (python) ($\mu \pm \sigma$)", "Sequential (C++) ($\mu \pm \sigma$)", "Parallel (C++) ($\mu \pm \sigma$)"])

    plt.scatter(*get_mean(seq_data), color='red', marker='x')
    plt.fill_between(*get_std(seq_data), alpha=0.5, color='red')
    
    plt.scatter(*get_mean(stack_data), color='blue', marker='x')
    plt.fill_between(*get_std(stack_data), alpha=0.5, color='blue')

    plt.scatter(*get_mean(cpp_seq_data), color='green', marker='x')
    plt.fill_between(*get_std(cpp_seq_data), alpha=0.5, color='green')

    plt.scatter(*get_mean(cpp_stack_data), color='orange', marker='x')
    plt.fill_between(*get_std(cpp_stack_data), alpha=0.5, color='orange')

    plt.plot(*get_mean(theory_max), color='black', ls='--')
    plt.savefig("plots/batch_throughput.png")

if __name__ == '__main__':
    plot_one()
    plt.cla()
    plot_two()
    plt.cla()
    plot_three()
    plt.cla()
    plot_four()
