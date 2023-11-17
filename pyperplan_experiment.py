import argparse
import subprocess
import yaml
import json
from collections import OrderedDict
import os
import platform

def main():
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argparser.add_argument(dest="algo")
    argparser.add_argument(dest="domain")
    argparser.add_argument(dest="num_task_experiments")
    argparser.add_argument(dest="num_runs_per_task")
    
    args = argparser.parse_args()

    domain = args.domain
    # print(domain)

    # Get the operating system name
    os_name = platform.system()
    print(os_name)
    # exit()

    # Check if it's Windows
    if os_name == 'Windows':
        domain_path = "benchmarks\\" + domain + "\\domain01.pddl"
        starting_problem_path = "benchmarks\\" + domain + "\\task01.pddl"
    elif os_name == 'Darwin':
        domain_path = "benchmarks/" + domain + "/domain01.pddl"
        starting_problem_path = "benchmarks/" + domain + "/task01.pddl"
    else:
        print(f"Unknown operating system: {os_name}")
        exit()

    print(domain_path, starting_problem_path)


    filename_windows = os.path.basename(starting_problem_path)

    starting_problem = 'tasks ' + starting_problem_path.split('k')[-1].split('.')[0]

    # starting_problem = 'tasks ' + starting_problem_path.split('/')[-1].split('.')[0].split('k')[-1]
    print(starting_problem)

    # Define the command and arguments

    experiment_prompt = ["pyperplan", "-H", "hff", "-s", args.algo, domain_path, starting_problem_path, args.num_task_experiments, args.num_runs_per_task]

    # exit()

    starting_problem_number = int(starting_problem.split('s')[-1])
    stopping_problem = starting_problem_number-1 + int(args.num_task_experiments)


    print(starting_problem_number, stopping_problem)
    stopping_problem = starting_problem_number-1 + int(args.num_task_experiments)


    print('\nRunning Experiments...\n')
    
    print(f'Executing {starting_problem}-{stopping_problem} each for {args.num_runs_per_task} runs\n')
    print('Time limit = 10 mins')
    # print('restart_depth = 10')


    print(f'Domain: {domain}')
    print(f'Algorithm: {args.algo}\n')


    # Run the command and capture the output
    proc = subprocess.run(experiment_prompt, capture_output=True, text=True)

    # Get the output
    output = proc.stdout
    error = proc.stderr

    print(output, error)
    task_list = output.split("task_splitter")[1:]

    # print(output.count('\n'))
    # print(task_list[1])
    OUTPUT_dict = {

        }

    for task_output in task_list:
        task_output = task_output.splitlines()[1:]
        task_number = task_output[0].split(' ')[-1]

        run_list = ('\n').join(task_output)
        run_list = run_list.split('run_splitter')[1:]

        OUTPUT_dict[f"task {task_number}"] = {}

        run_number = 0
        for run in run_list:
            run_number += 1
            run_output = run.splitlines()[1:]
            
            OUTPUT_dict[f"task {task_number}"][f'run {run_number}'] = {}


            for output in run_output:
                if 'Nodes expanded' in output:
                    expansions = output.split()
                    expansions = ' '.join(expansions[-3:-2])
                
                    OUTPUT_dict[f"task {task_number}"][f'run {run_number}']['expansions'] = expansions
            
                # print(output)

                if 'No solution could be found' in output:
                    OUTPUT_dict[f"task {task_number}"][f'run {run_number}']['expansions'] = 'timed out'


                if 'Plan length' in output:
                    plan_length = output.split()
                    plan_length = ' '.join(plan_length[-1:])
                    
                    OUTPUT_dict[f"task {task_number}"][f'run {run_number}']['plan length'] = plan_length
        # print(f'run number: {run_number}')

        task_total_expansions = 0

        count = 0
        for run_data in OUTPUT_dict[f"task {task_number}"].values():
            if run_data['expansions'] != 'timed out':
                count += 1

                task_total_expansions += int(run_data['expansions'])

        if count > 0: task_average_expansions = round(task_total_expansions / count, 2)
        else: task_average_expansions = 0
        OUTPUT_dict[f"task {task_number}"][f'average expansions'] = task_average_expansions




        run_number = 0
        # print("CHANGED task LOOOOOP")
    # print(OUTPUT_dict)

    total_cases = 0
    cases_without_timeout = 0

    for task in OUTPUT_dict.values():
        for run in task.values():
            if isinstance(run, dict) and 'expansions' in run:
                total_cases += 1
                if run['expansions'] != 'timed out':
                    cases_without_timeout += 1

    coverage = cases_without_timeout / total_cases if total_cases > 0 else 0
    OUTPUT_dict['task 1']['Overall experiment coverage'] = round(coverage, 3)
    # print(cases_without_timeout, total_cases)


    OUTPUT_dict = str(OUTPUT_dict)
    OUTPUT_dict = json.loads(OUTPUT_dict.replace("'", "\""))
    OUTPUT_dict = OrderedDict(sorted(OUTPUT_dict.items(), key=lambda t: int(t[0].split(' ')[1])))
    yaml_string = yaml.dump(OUTPUT_dict)
    # sorted_data = dict(sorted(yaml_string.items(), key=lambda item: int(item[0].split(' ')[1])))
    # print(OUTPUT_dict)
    print('Experiment Output:\n')

    print(yaml_string)
    # exit()

    if os_name == 'Windows':
        output_path = 'benchmarks\\experiment_output'
        with open(output_path + '\\' + args.algo + '_' + domain + f'_tasks{starting_problem_number}-{stopping_problem}' +  '.yaml', 'w') as file:
            file.write(yaml_string)

    elif os_name == 'Darwin':
        output_path = 'benchmarks/experiment_output'
        with open(output_path + '/' + args.algo + '_' + domain + f'_tasks{starting_problem_number}-{stopping_problem}' +  '.yaml', 'w') as file:
            file.write(yaml_string)


    

    # print(f'domain: {domain}')
    # print(OUTPUT_dict)
    print('test')






if __name__ == "__main__":
    main()