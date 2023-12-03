import os
import yaml
import pprint
import collections

"""
create_charts.py parses a directory of YAML files containing algorithm performance information. It stores this info
in dataframes and generates charts
"""

def ordered_dict_constructor(loader, node):
    if isinstance(node, yaml.MappingNode):
        return collections.OrderedDict(loader.construct_pairs(node))
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    else:
        return loader.construct_scalar(node)

yaml.add_constructor('tag:yaml.org,2002:python/object/apply:collections.OrderedDict', ordered_dict_constructor)



yaml_dir = 'benchmarks/experiment_output/'

yaml_dir_list = os.listdir(yaml_dir)

curr_yaml_file = yaml_dir + yaml_dir_list[1]
# Open the file
print(curr_yaml_file)

with open(curr_yaml_file, 'r') as stream:
    curr_file_output = yaml.load(stream, Loader=yaml.FullLoader)[0]


curr_file_name = curr_yaml_file.split('_')[-2]


for task_data in curr_file_output:
    task_dict = task_data[1]
    task_coverage = task_dict['Overall experiment coverage']
    task_avg_expansions = task_dict['average expansions']

    run_info = []
    for key, value in task_dict.items():
        if 'run' in key:
            run_info.append(value)
        
    print(run_info)
    print(curr_file_name)
    break

