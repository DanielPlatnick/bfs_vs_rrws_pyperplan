import yaml
import os
import matplotlib.pyplot as plt
import collections

def ordered_dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))

yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, ordered_dict_constructor)

directory = 'C:\\Users\\Owner\\Desktop\\thesis\\ehs_vs_ehrws_pyperplan\\benchmarks\\experiment_output'

ehs_expansions = {}
luby_expansions = {}

for filename in os.listdir(directory):
    if filename.endswith(".yaml"):
        with open(os.path.join(directory, filename), 'r') as file:
            data_list = yaml.load(file, Loader=yaml.FullLoader)
            for data in data_list:
                task_name = data[0]
                avg_expansions = data[1]['average expansions']

                if 'ehs' in filename:
                    ehs_expansions[task_name] = avg_expansions
                elif 'luby_ehrws' in filename:
                    luby_expansions[task_name] = avg_expansions

plt.figure(figsize=(10, 6))
tasks = sorted(ehs_expansions.keys(), key=lambda x: int(x.split(' ')[1]))
plt.plot(tasks, [ehs_expansions[task] for task in tasks], marker='o', label='EHS')
plt.plot(tasks, [luby_expansions[task] for task in tasks], marker='o', label='Luby EHRWS')
plt.xlabel('Tasks')
plt.ylabel('Average Expansions')
plt.title('Average Expansions per Task')
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.show()