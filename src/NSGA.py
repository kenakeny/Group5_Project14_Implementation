import numpy as np
import random
from utils import *
# Set seed
random.seed(42)
np.random.seed(42)

# USER CONFIGURATION


def get_user_configuration():  # Get configuration from user input.
    print("FOG-CLOUD TASK SCHEDULER CONFIGURATION")

    use_fog = input("\nUse Fog Nodes? (yes/no) [yes]: ").strip().lower()
    use_fog = use_fog != 'no'

    use_cloud = input("Use Cloud Nodes? (yes/no) [yes]: ").strip().lower()
    use_cloud = use_cloud != 'no'

    if not use_fog and not use_cloud:
        print("You must enable at least one node type! will use both")
        use_fog = True
        use_cloud = True

    num_fog = int(input("\nNumber of Fog Nodes [2-10] (default: 2): ") or 2)
    num_cloud = int(input("Number of Cloud Nodes [2-10] (default: 2): ") or 2)
    num_tasks = int(input("\nNumber of Tasks [5-50] (default: 6): ") or 6)
    pop_size = int(input("\nPopulation Size [20-100] (default: 40): ") or 40)
    generations = int(
        input("Number of Generations [10-200] (default: 50): ") or 50)
    mutation_rate = float(
        input("\nMutation Rate [0.0-1.0] (default: 0.1): ") or 0.1)

    return {
        'use_fog': use_fog,
        'use_cloud': use_cloud,
        'num_fog': num_fog,
        'num_cloud': num_cloud,
        'num_tasks': num_tasks,
        'pop_size': pop_size,
        'generations': generations,
        'mutation_rate': mutation_rate
    }

# NSGA-II VARIATION SELECTION


# RANDOM INFRASTRUCTURE AND TASK GENERATION


def generate_fog_nodes(num_nodes):
    fog_nodes = []
    for i in range(num_nodes):
        node = {
            "cpu": random.randint(8, 15),
            "capacity": random.randint(30, 50),
            "power_consumption": round(random.uniform(2.5, 4.0), 2)
        }
        fog_nodes.append(node)
    return fog_nodes


def generate_cloud_nodes(num_nodes):
    cloud_nodes = []
    for i in range(num_nodes):
        node = {
            "cpu": random.randint(20, 30),
            "capacity": random.randint(80, 120),
            "power_consumption": round(random.uniform(1.0, 1.5), 2)
        }
        cloud_nodes.append(node)
    return cloud_nodes


def generate_tasks(num_tasks):
    tasks = []
    for i in range(num_tasks):
        task_size = random.randint(5, 25)
        urgency = random.choice([0, 1])
        tasks.append((task_size, urgency))
    return tasks

# DELAY AND ENERGY CALCULATION




def calculate_task_delay(task_size, urgency, node, is_fog_node=True):
    base_delay = FOG_BASE_DELAY if is_fog_node else CLOUD_BASE_DELAY
    delay_factor = FOG_DELAY_FACTOR if is_fog_node else CLOUD_DELAY_FACTOR
    processing_time = delay_factor * (task_size / node["cpu"])
    urgency_cost = URGENCY_PENALTY * urgency
    return base_delay + processing_time + urgency_cost


def calculate_energy_consumption(task_size, node, is_fog_node=True):
    execution_time = task_size / node["cpu"]
    return node["power_consumption"] * execution_time

# SOLUTION REPRESENTATION


def create_random_solution(num_fog, num_cloud, num_tasks):
    total_nodes = num_fog + num_cloud
    return [random.randint(0, total_nodes - 1) for i in range(num_tasks)]

# FITNESS EVALUATION


def evaluate_solution(chromosome, fog_nodes, cloud_nodes, tasks):
    num_fog = len(fog_nodes)
    num_cloud = len(cloud_nodes)
    total_delay = 0
    total_energy = 0
    constraint_penalty = 0
    fog_loads = [0]*num_fog
    cloud_loads = [0]*num_cloud

    for idx, node_id in enumerate(chromosome):
        task_size, urgency = tasks[idx]
        if node_id < num_fog:
            node = fog_nodes[node_id]
            is_fog = True
            fog_loads[node_id] += task_size
        else:
            node = cloud_nodes[node_id - num_fog]
            is_fog = False
            cloud_loads[node_id - num_fog] += task_size
        total_delay += calculate_task_delay(task_size, urgency, node, is_fog)
        total_energy += calculate_energy_consumption(task_size, node, is_fog)

    for i in range(num_fog):
        if fog_loads[i] > fog_nodes[i]["capacity"]:
            constraint_penalty += 10000
    for i in range(num_cloud):
        if cloud_loads[i] > cloud_nodes[i]["capacity"]:
            constraint_penalty += 10000

    return total_delay + constraint_penalty, total_energy + constraint_penalty


# PARETO DOMINANCE

def solution_a_dominates_b(fitness_a, fitness_b):
    delay_a, energy_a = fitness_a
    delay_b, energy_b = fitness_b
    no_worse = (delay_a <= delay_b) and (energy_a <= energy_b)
    strictly_better = (delay_a < delay_b) or (energy_a < energy_b)
    return no_worse and strictly_better


def fast_nondominated_sort(population):
    num_solutions = len(population)
    dominated = {p: [] for p in range(num_solutions)}
    domination_count = {p: 0 for p in range(num_solutions)}
    fronts = [[]]

    for p in range(num_solutions):
        for q in range(num_solutions):
            if solution_a_dominates_b(population[p][1], population[q][1]):
                dominated[p].append(q)
            elif solution_a_dominates_b(population[q][1], population[p][1]):
                domination_count[p] += 1
        if domination_count[p] == 0:
            fronts[0].append(p)

    current_front = 0
    while len(fronts[current_front]) > 0:
        next_front = []
        for p in fronts[current_front]:
            for q in dominated[p]:
                domination_count[q] -= 1
                if domination_count[q] == 0:
                    next_front.append(q)
        current_front += 1
        fronts.append(next_front)
    return fronts[:-1]

# SELECTION METHODS


def binary_tournament_selection(population):
    """Binary tournament selection for NSGA-II.
    Randomly selects two solutions and returns the one that dominates
    """
    a, b = random.choice(population), random.choice(population)
    return a if solution_a_dominates_b(a[1], b[1]) else b


def random_selection(population):
    return random.choice(population)  # Just a random selection


def roulette_wheel_selection(population):
    """
    Roulette selection for NSGA-II.
    Converts multi-objective (delay, energy) into a single score:
    score = 1 / (delay + energy)
    Lower delay+energy gets higher probability.
    """
    epsilon = 1e-9  # avoid divide-by-zero

    # Compute scores
    scores = []
    for ind, fitness in population:
        delay, energy = fitness
        total = delay + energy
        score = 1 / (total + epsilon)
        scores.append(score)

    # Normalize probabilities
    total_score = sum(scores)
    probabilities = [s / total_score for s in scores]

    # Spin roulette wheel
    r = random.random()
    cumulative = 0
    for i, p in enumerate(probabilities):
        cumulative += p
        if r <= cumulative:
            return population[i]

    # fallback
    return population[-1]


def select_parent(population, variation_choice):
    if variation_choice == '1':
        return binary_tournament_selection(population)
    elif variation_choice == '2':
        return random_selection(population)
    elif variation_choice == '3':
        return roulette_wheel_selection(population)

# CROSSOVER AND MUTATION


def single_point_crossover(parent1, parent2, num_tasks):
    point = random.randint(1, num_tasks-1)
    return parent1[:point]+parent2[point:]


def mutate_chromosome(chromosome, num_fog, num_cloud, mutation_rate):
    total_nodes = num_fog + num_cloud
    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            chromosome[i] = random.randint(0, total_nodes-1)
    return chromosome


# NSGA-II MAIN

def run_nsga2_optimization(config, fog_nodes, cloud_nodes, tasks):
    pop_size = config['pop_size']
    generations = config['generations']
    mutation_rate = config['mutation_rate']
    num_fog = len(fog_nodes)
    num_cloud = len(cloud_nodes)
    num_tasks = len(tasks)

    population = [create_random_solution(
        num_fog, num_cloud, num_tasks) for i in range(pop_size)]
    population = [(ind, evaluate_solution(ind, fog_nodes, cloud_nodes, tasks))
                  for ind in population]

    for gen in range(generations):
        offspring = []
        for i in range(pop_size):
            p1 = select_parent(population)[0]
            p2 = select_parent(population)[0]
            child = single_point_crossover(p1, p2, num_tasks)
            child = mutate_chromosome(child, num_fog, num_cloud, mutation_rate)
            offspring.append((child, evaluate_solution(
                child, fog_nodes, cloud_nodes, tasks)))

        combined = population + offspring
        fronts = fast_nondominated_sort(combined)
        new_pop = []
        for front in fronts:
            if len(new_pop)+len(front) <= pop_size:
                new_pop.extend([combined[i] for i in front])
            else:
                remaining = pop_size-len(new_pop)
                new_pop.extend([combined[i] for i in front[:remaining]])
                break
        population = new_pop

        first_front = [population[i] for i in range(min(3, len(population)))]
        delays = [f[1][0] for f in first_front]
        energies = [f[1][1] for f in first_front]
        print(
            f"Generation {gen+1}: Best Delay={min(delays):.4f}, Best Energy={min(energies):.4f}")

    return population

    # EXECUTION
if __name__ == "__main__":

    config = get_user_configuration()
    fog_nodes = generate_fog_nodes(
        config['num_fog']) if config['use_fog'] else []
    cloud_nodes = generate_cloud_nodes(
        config['num_cloud']) if config['use_cloud'] else []
    tasks = generate_tasks(config['num_tasks'])

    print(
        f"\nGenerated {len(fog_nodes)} fog nodes, {len(cloud_nodes)} cloud nodes, {len(tasks)} tasks")
    final_front = run_nsga2_optimization(config, fog_nodes, cloud_nodes, tasks)

    print("\nFINAL PARETO-OPTIMAL SOLUTIONS")

    num_fog = len(fog_nodes)

    for sol, (delay, energy) in final_front:
        assignment_str = ""
        for task_index, node_id in enumerate(sol):
            if node_id < num_fog:
                assignment_str += f"Task {task_index+1} -> Fog {node_id}, "
            else:
                assignment_str += f"Task {task_index+1} -> Cloud {node_id - num_fog}, "

        assignment_str = assignment_str.rstrip(
            ", ")
        print(f"{assignment_str}\n  → Delay: {delay:.2f}, Energy: {energy:.2f}\n")
