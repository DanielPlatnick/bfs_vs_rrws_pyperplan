import os
import yaml
import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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


def extract_run_times(yaml_dir):
    yaml_dir_list = sorted(os.listdir(yaml_dir))
    ehrws_run_times_vector = []
    ehs_run_times_vector = []

    for yaml_output in yaml_dir_list:

        curr_yaml_file = yaml_dir + yaml_output

        if 'ehs' in yaml_output:
            algorithm_name = 'ehs'
        elif 'ehrws' in yaml_output:
            algorithm_name = 'ehrws'

        with open(curr_yaml_file, 'r') as stream:
            curr_file_output = yaml.load(stream, Loader=yaml.FullLoader)[0]

        task_name = curr_yaml_file.split('_')[-2]
        print(task_name)
        run_times_vector = []
        domain_coverage = curr_file_output[0][1]['Overall experiment coverage']

        for task_data in curr_file_output:
            # print(task_data)
            task_dict = task_data[1]
            
            task_avg_expansions = task_dict['average expansions']
            task_number = int(task_data[0].split(' ')[-1])
            run_info = []
            run_expansions = []
            run_plan_length = []

            ### Appending run dict info is broken
            for key, value in task_dict.items():
                # print(key, value)
                if 'run' in key:
                    run_expansions.append(value['expansions'])
                    run_times_vector.append(value['expansions'])

                # Adjust code to get plan lengths
                # if 'run' in key:
                #     print(curr_yaml_file)
                #     run_plan_length.append(value['plan length'])

                # run_info.append((run_expansions, run_plan_length))
            # print(run_times_vector)
            # exit('debug')

        curr_algorithm = curr_yaml_file.split('/')[-1].split('_')[0]
        # print(curr_algorithm)

        if algorithm_name == 'ehs':
            for run_time in run_times_vector:
                ehs_run_times_vector.append(run_time)

        if algorithm_name == 'ehrws':
            for run_time in run_times_vector:
                ehrws_run_times_vector.append(run_time)

    # run-times should be same length
    assert len(ehs_run_times_vector) == len(ehrws_run_times_vector)
    # replacing time-outs with infinity for charts
    ehs_run_times_vector = [1e6 if element == 'timed out' else element for element in ehs_run_times_vector]
    ehrws_run_times_vector = [1e6 if element == 'timed out' else element for element in ehrws_run_times_vector]

    return ehs_run_times_vector, ehrws_run_times_vector


def create_runtime_scatter(runtimes):

    ehs_runs, ehrws_runs = runtimes

    df = pd.DataFrame({
        'ehrws run-time': ehrws_runs,
        'ehs run-time': ehs_runs
    })

    df['ehrws run-time'] = pd.to_numeric(df['ehrws run-time'], errors='coerce')
    df['ehs run-time'] = pd.to_numeric(df['ehs run-time'], errors='coerce')

    print(df)
    scatter_point_size = 5
    plt.scatter(df['ehrws run-time'], df['ehs run-time'], label='Run Times', s=scatter_point_size)
    min_val = min(df['ehrws run-time'].min(), df['ehs run-time'].min())
    max_val = max(df['ehrws run-time'].max(), df['ehs run-time'].max())
    plt.plot([min_val, max_val], [min_val, max_val], linestyle='-', color='red')
    plt.title('Run-time Comparison on 6 Domains (6*15 tasks*5 runs)')
    plt.xlabel('EHRWS Run Time')
    plt.ylabel('EHS Run Time')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend()
    plt.grid(True)
    plt.show()


yaml_dir = 'benchmarks/experiment_output/'
ehs_runs, ehrws_runs = extract_run_times(yaml_dir=yaml_dir)

create_runtime_scatter((ehs_runs, ehrws_runs))
# print(ehs_runs)
# print(ehrws_runs)
