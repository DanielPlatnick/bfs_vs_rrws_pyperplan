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
    
    # add this if you want to run a specific domain
    # argparser.add_argument(dest="domain")
    argparser.add_argument(dest="algo")
    argparser.add_argument(dest="num_task_experiments")
    argparser.add_argument(dest="num_runs_per_task")
    
    args = argparser.parse_args()
    domain_list = os.listdir('benchmarks')

    domain_list.remove('.DS_Store')
    domain_list.remove('README.md')
    domain_list.remove('experiment_output')
    domain_list.remove('depot')
    domain_list.remove('freecell') 
    domain_list.remove('parcprinter')


    domain_list.remove('blocks')
    domain_list.remove('movie')
    domain_list.remove('tpp')
    domain_list.remove('transport')
    domain_list.remove('woodworking')
    domain_list.remove('pegsol')
    # domain_list.remove('elevators')
    # domain_list.remove('airport')
    # domain_list.remove('zenotravel')
    # domain_list.remove('psr-small')
    # domain_list.remove('gripper')
    # domain_list.remove('scanalyzer')
  

    # if want to do just 1 experiment, either remove loop or just set loop to 1 iteration and specify domain file
    for domain_experiment in domain_list:
        # domain = args.domain


        domain = domain_experiment
        # print(domain)

        # Get the operating system name
        os_name = platform.system()
        # print(os_name)
        # exit()

        # Check if it's Windows or mac and set path to domain file
        if os_name == 'Windows':
            domain_path = "benchmarks\\" + domain + "\\domain01.pddl"
            starting_problem_path = "benchmarks\\" + domain + "\\task01.pddl"
        elif os_name == 'Darwin':
            domain_path = "benchmarks/" + domain + "/domain01.pddl"
            starting_problem_path = "benchmarks/" + domain + "/task01.pddl"
        else:
            print(f"Unknown operating system: {os_name}")
            exit()


        starting_problem = 'tasks ' + starting_problem_path.split('k')[-1].split('.')[0]

        # Define the command and arguments

        experiment_prompt = ["pyperplan", "-H", "hff", "-s", args.algo, domain_path, starting_problem_path, args.num_task_experiments, args.num_runs_per_task]

        # exit()

        starting_problem_number = int(starting_problem.split('s')[-1])
        stopping_problem = starting_problem_number-1 + int(args.num_task_experiments)


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


        # # Extract task averages and calculate the overall average             ##maybe add code to get total experiment avg expansions
        # task_averages = []
        # for task_data in OUTPUT_dict.items():
        #     task_average_expansions = task_data['average expansions']
        #     task_averages.append(task_average_expansions)

        # overall_average = sum(task_averages) / len(task_averages)
        # print(overall_average)
        # exit()


        OUTPUT_dict = str(OUTPUT_dict)
        OUTPUT_dict = json.loads(OUTPUT_dict.replace("'", "\""))
        OUTPUT_dict = OrderedDict(sorted(OUTPUT_dict.items(), key=lambda t: int(t[0].split(' ')[1])))
        yaml_string = yaml.dump(OUTPUT_dict)
    
        print('Experiment Output:\n')

        print(yaml_string)
        # exit()

        if os_name == 'Windows':
            output_path = 'benchmarks\\experiment_output'
            with open(output_path + '\\' + 'luby_' + args.algo + '_' + domain + f'_tasks{starting_problem_number}-{stopping_problem}' +  '.yaml', 'w') as file:
                file.write(yaml_string)

        elif os_name == 'Darwin':
            output_path = 'benchmarks/experiment_output'
            # with open(output_path + '/' + 'lubyd2_' + args.algo + '_' + domain + f'_tasks{starting_problem_number}-{stopping_problem}' +  '.yaml', 'w') as file:
            with open(output_path + '/'  + args.algo + '_' + domain + f'_tasks{starting_problem_number}-{stopping_problem}' +  '.yaml', 'w') as file:
                file.write(yaml_string)


        # exit()

    # print(f'domain: {domain}')


if __name__ == "__main__":
    main()