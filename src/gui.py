import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from NSGA import *  
from utils import * 

class FogCloudSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloud resource allocation Group 5")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        

        self.use_fog = tk.BooleanVar(value=True)
        self.use_cloud = tk.BooleanVar(value=True)
        self.num_fog = tk.IntVar(value=2)
        self.num_cloud = tk.IntVar(value=2)
        self.num_tasks = tk.IntVar(value=6)
        self.pop_size = tk.IntVar(value=40)
        self.generations = tk.IntVar(value=50)
        self.mutation_rate = tk.DoubleVar(value=0.1)
        self.variation_choice = tk.StringVar(value='1')

        self.delay_history = []
        self.energy_history = []
        self.fog_nodes = []
        self.cloud_nodes = []
        self.tasks = []
        self.final_population = []

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - deeh feeha Configuration
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        config_frame = ttk.LabelFrame(
            left_panel, text="Configuration", padding="15")
        config_frame.pack(fill=tk.BOTH, expand=True)

        # select nodes
        node_frame = ttk.LabelFrame(
            config_frame, text="Node Types", padding="10")
        node_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Checkbutton(node_frame, text="Enable Fog Nodes",
                        variable=self.use_fog).pack(anchor=tk.W)
        ttk.Checkbutton(node_frame, text="Enable Cloud Nodes",
                        variable=self.use_cloud).pack(anchor=tk.W)

        # variables for fog and cloud nodes and tasks
        infra_frame = ttk.LabelFrame(
            config_frame, text="Infrastructure", padding="10")
        infra_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(infra_frame, text="Number of Fog Nodes:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(infra_frame, from_=2, to=10, textvariable=self.num_fog,
                    width=15).grid(row=0, column=1, padx=5)

        ttk.Label(infra_frame, text="Number of Cloud Nodes:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(infra_frame, from_=2, to=10, textvariable=self.num_cloud,
                    width=15).grid(row=1, column=1, padx=5)

        ttk.Label(infra_frame, text="Number of Tasks:").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(infra_frame, from_=5, to=50, textvariable=self.num_tasks,
                    width=15).grid(row=2, column=1, padx=5)

        # Parameters Section
        algo_frame = ttk.LabelFrame(
            config_frame, text="NSGA-II Parameters", padding="10")
        algo_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(algo_frame, text="Population Size:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(algo_frame, from_=20, to=100, textvariable=self.pop_size,
                    width=15).grid(row=0, column=1, padx=5)

        ttk.Label(algo_frame, text="Generations:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(algo_frame, from_=10, to=200, textvariable=self.generations,
                    width=15).grid(row=1, column=1, padx=5)

        ttk.Label(algo_frame, text="Mutation Rate:").grid(
            row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(algo_frame, from_=0.0, to=1.0, increment=0.05,
                    textvariable=self.mutation_rate, width=15).grid(row=2, column=1, padx=5)

        # hena we have our selection method
        var_frame = ttk.LabelFrame(
            config_frame, text="Selection Method", padding="10")
        var_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Radiobutton(var_frame, text="Binary Tournament",
                        variable=self.variation_choice, value='1').pack(anchor=tk.W)
        ttk.Radiobutton(var_frame, text="Random Selection",
                        variable=self.variation_choice, value='2').pack(anchor=tk.W)
        ttk.Radiobutton(var_frame, text="Roulette Wheel",
                        variable=self.variation_choice, value='3').pack(anchor=tk.W)
        ttk.Separator(var_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        ttk.Radiobutton(var_frame, text="Compare All Methods",
                        variable=self.variation_choice, value='compare').pack(anchor=tk.W)
        # Control Buttons
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Start Optimization",
                   command=self.run_optimization).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Reset",
                   command=self.reset).pack(fill=tk.X, pady=2)

        # Right panel feeha Results and Visualization
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Top section progress wee Graph
        top_section = ttk.Frame(right_panel)
        top_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Progress Log trust
        log_frame = ttk.LabelFrame(
            top_section, text="Optimization Progress", padding="10")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=15, width=40, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Graphs
        graph_frame = ttk.LabelFrame(
            top_section, text="Convergence Graph", padding="10")
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        self.ax1.set_title('Best Delay per Generation')
        self.ax1.set_xlabel('Generation')
        self.ax1.set_ylabel('Delay')
        self.ax1.grid(True, alpha=0.3)

        self.ax2.set_title('Best Energy per Generation')
        self.ax2.set_xlabel('Generation')
        self.ax2.set_ylabel('Energy')
        self.ax2.grid(True, alpha=0.3)

        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bottom section - Results
        results_frame = ttk.LabelFrame(
            right_panel, text="Pareto-Optimal Solutions", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # dh el results
        columns = ('Solution', 'Delay', 'Energy', 'Assignment')
        self.results_tree = ttk.Treeview(
            results_frame, columns=columns, show='headings', height=10)

        self.results_tree.heading('Solution', text='Solution #')
        self.results_tree.heading('Delay', text='Delay')
        self.results_tree.heading('Energy', text='Energy')
        self.results_tree.heading('Assignment', text='Task Assignment')

        self.results_tree.column('Solution', width=80)
        self.results_tree.column('Delay', width=100)
        self.results_tree.column('Energy', width=100)
        self.results_tree.column('Assignment', width=600)

        scrollbar = ttk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status 
        self.status_var = tk.StringVar(value="Ready to start optimization")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log_message(self, message):  # Function to log messages using tkinter
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_graph(self):
        self.ax1.clear()
        self.ax2.clear()

        if self.delay_history:
            self.ax1.plot(range(1, len(self.delay_history) + 1),
                          self.delay_history, 'b-', linewidth=2)
            self.ax1.set_title('Best Delay per Generation')
            self.ax1.set_xlabel('Generation')
            self.ax1.set_ylabel('Delay')
            self.ax1.grid(True, alpha=0.3)

        if self.energy_history:
            self.ax2.plot(range(1, len(self.energy_history) + 1),
                          self.energy_history, 'r-', linewidth=2)
            self.ax2.set_title('Best Energy per Generation')
            self.ax2.set_xlabel('Generation')
            self.ax2.set_ylabel('Energy')
            self.ax2.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()
        self.root.update()

    def run_optimization(self):
        # Validate the inputs lw feeh moshkela
        if not self.use_fog.get() and not self.use_cloud.get():
            messagebox.showerror(
                "Error", "You must enable at least one node type!")
            return

        # Check if comparison mode is selected
        if self.variation_choice.get() == 'compare':
            self.compare_all_methods()
            return

        self.delay_history = []
        self.energy_history = []

        # Clear  results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.log_text.delete(1.0, tk.END)

        try:
            # Generate infrastructure and tasks
            self.status_var.set("Generating infrastructure and tasks")
            self.root.update()

            self.fog_nodes = generate_fog_nodes(
                self.num_fog.get()) if self.use_fog.get() else []
            self.cloud_nodes = generate_cloud_nodes(
                self.num_cloud.get()) if self.use_cloud.get() else []
            self.tasks = generate_tasks(self.num_tasks.get())

            self.log_message(
                f"Generated {len(self.fog_nodes)} fog nodes, {len(self.cloud_nodes)} cloud nodes, {len(self.tasks)} tasks")
            self.log_message("-" * 50)

            # Run NSGA-II
            self.status_var.set("Running NSGA-II optimization")
            self.root.update()

            config = {
                'pop_size': self.pop_size.get(),
                'generations': self.generations.get(),
                'mutation_rate': self.mutation_rate.get()
            }

            self.final_population = self.run_nsga2_with_gui(config)

            # Display results
            self.display_results()

            self.status_var.set("Optimization completed successfully!")
            self.log_message("Optimization completed!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during optimization")

    def run_nsga2_with_gui(self, config):
        pop_size = config['pop_size']
        generations = config['generations']
        mutation_rate = config['mutation_rate']
        num_fog = len(self.fog_nodes)
        num_cloud = len(self.cloud_nodes)
        num_tasks = len(self.tasks)

        population = [create_random_solution(
            num_fog, num_cloud, num_tasks) for i in range(pop_size)]
        population = [(ind, evaluate_solution(ind, self.fog_nodes,
                       self.cloud_nodes, self.tasks)) for ind in population]

        for gen in range(generations):
            offspring = []
            for i in range(pop_size):
                p1 = select_parent(population, self.variation_choice.get())[0]
                p2 = select_parent(population, self.variation_choice.get())[0]
                child = single_point_crossover(p1, p2, num_tasks)
                child = mutate_chromosome(
                    child, num_fog, num_cloud, mutation_rate)
                offspring.append((child, evaluate_solution(
                    child, self.fog_nodes, self.cloud_nodes, self.tasks)))

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

            first_front = [population[i]
                           for i in range(min(3, len(population)))]
            delays = [f[1][0] for f in first_front]
            energies = [f[1][1] for f in first_front]

            best_delay = min(delays)
            best_energy = min(energies)

            self.delay_history.append(best_delay)
            self.energy_history.append(best_energy)

            self.log_message(
                f"Generation {gen+1}/{generations}: Delay={best_delay:.2f}, Energy={best_energy:.2f}")
            self.update_graph()
            self.status_var.set(f"Generation {gen+1}/{generations}")

        return population

    def display_results(self):
        num_fog = len(self.fog_nodes)

        # Show top 10
        for idx, (sol, (delay, energy)) in enumerate(self.final_population[:10]):
            assignment_parts = []
            for task_index, node_id in enumerate(sol):
                if node_id < num_fog:
                    assignment_parts.append(f"T{task_index+1}→F{node_id}")
                else:
                    assignment_parts.append(
                        f"T{task_index+1}→C{node_id - num_fog}")

            assignment_str = ", ".join(assignment_parts)

            self.results_tree.insert('', tk.END, values=(
                f"#{idx+1}",
                f"{delay:.2f}",
                f"{energy:.2f}",
                assignment_str
            ))

    def reset(self):
        self.delay_history = []
        self.energy_history = []

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.log_text.delete(1.0, tk.END)

        self.ax1.clear()
        self.ax1.set_title('Best Delay per Generation')
        self.ax1.set_xlabel('Generation')
        self.ax1.set_ylabel('Delay')
        self.ax1.grid(True, alpha=0.3)

        self.ax2.clear()
        self.ax2.set_title('Best Energy per Generation')
        self.ax2.set_xlabel('Generation')
        self.ax2.set_ylabel('Energy')
        self.ax2.grid(True, alpha=0.3)

        self.canvas.draw()

        self.status_var.set("Ready to start optimization")
        self.log_message("System reset. Ready for new optimization.")

    def compare_all_methods(self):
        # Validate inputs
        if not self.use_fog.get() and not self.use_cloud.get():
            messagebox.showerror("Error", "You must enable at least one node type!")
            return
        # Clear  results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.log_text.delete(1.0, tk.END)
        try:
            # Generate infrastructure and tasks
            self.status_var.set("Generating infrastructure and tasks")
            self.root.update()

            self.fog_nodes = generate_fog_nodes(
                self.num_fog.get()) if self.use_fog.get() else []
            self.cloud_nodes = generate_cloud_nodes(
                self.num_cloud.get()) if self.use_cloud.get() else []
            self.tasks = generate_tasks(self.num_tasks.get())

            self.log_message("COMPARING ALL THREE SELECTION METHODS")
            self.log_message(
                f"Infrastructure: {len(self.fog_nodes)} fog nodes, {len(self.cloud_nodes)} cloud nodes, {len(self.tasks)} tasks")

            config = {
                'pop_size': self.pop_size.get(),
                'generations': self.generations.get(),
                'mutation_rate': self.mutation_rate.get()
            }

            results = {}
            method_names = {
                '1': 'Binary Tournament',
                '2': 'Random Selection',
                '3': 'Roulette Wheel'
            }

            for method_id, method_name in method_names.items():
                self.log_message(f"\n Running {method_name}")
                self.status_var.set(f"Running {method_name}")
                self.root.update()

                self.delay_history = []
                self.energy_history = []

                population = self.run_nsga2_with_method(config, method_id)

                if population:
                    best_solution = population[0]
                    results[method_id] = {
                        'name': method_name,
                        'population': population,
                        'best_delay': best_solution[1][0],
                        'best_energy': best_solution[1][1],
                        'delay_history': self.delay_history.copy(),
                        'energy_history': self.energy_history.copy()
                    }

                    self.log_message(
                        f" {method_name} completed - Best Delay: {best_solution[1][0]:.2f}, Best Energy: {best_solution[1][1]:.2f}")

            self.display_comparison_results(results)

            self.plot_comparison_graphs(results)

            self.status_var.set("Comparison completed!")

            self.log_message(" All methods compared successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during comparison")

    def run_nsga2_with_method(self, config, method_id):
        pop_size = config['pop_size']
        generations = config['generations']
        mutation_rate = config['mutation_rate']
        num_fog = len(self.fog_nodes)
        num_cloud = len(self.cloud_nodes)
        num_tasks = len(self.tasks)

        population = [create_random_solution(
            num_fog, num_cloud, num_tasks) for i in range(pop_size)]
        population = [(ind, evaluate_solution(ind, self.fog_nodes,
                       self.cloud_nodes, self.tasks)) for ind in population]

        for gen in range(generations):
            offspring = []
            for i in range(pop_size):
                p1 = select_parent(population, method_id)[0]
                p2 = select_parent(population, method_id)[0]
                child = single_point_crossover(p1, p2, num_tasks)
                child = mutate_chromosome(
                    child, num_fog, num_cloud, mutation_rate)
                offspring.append((child, evaluate_solution(
                    child, self.fog_nodes, self.cloud_nodes, self.tasks)))

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

            first_front = [population[i]
                           for i in range(min(3, len(population)))]
            delays = [f[1][0] for f in first_front]
            energies = [f[1][1] for f in first_front]

            best_delay = min(delays)
            best_energy = min(energies)

            self.delay_history.append(best_delay)
            self.energy_history.append(best_energy)

        return population

    def display_comparison_results(self, results):
        num_fog = len(self.fog_nodes)

        self.results_tree.insert('', tk.END, values=(
            'METHOD', 'BEST DELAY', 'BEST ENERGY', 'COMPARISON'
        ), tags=('header',))

        self.results_tree.tag_configure(
            'header', background='#e0e0e0', font=('Arial', 9, 'bold'))

        for method_id in ['1', '2', '3']:
            if method_id in results:
                result = results[method_id]
                sol, (delay, energy) = result['population'][0]

                assignment_parts = []
                for task_index, node_id in enumerate(sol[:5]):
                    if node_id < num_fog:
                        assignment_parts.append(f"T{task_index+1}→F{node_id}")
                    else:
                        assignment_parts.append(
                            f"T{task_index+1}→C{node_id - num_fog}")

                assignment_str = ", ".join(assignment_parts)
                if len(sol) > 5:
                    assignment_str += " "

                self.results_tree.insert('', tk.END, values=(
                    result['name'],
                    f"{delay:.2f}",
                    f"{energy:.2f}",
                    assignment_str
                ))

        self.results_tree.insert('', tk.END, values=('', '', '', ''))

        best_delay_method = min(
            results.items(), key=self.best_delay)
        best_energy_method = min(
            results.items(), key=self.best_energy)

        self.results_tree.insert('', tk.END, values=(
            ' Best Delay',
            best_delay_method[1]['name'],
            f"{best_delay_method[1]['best_delay']:.2f}",
            ''
        ), tags=('winner',))

        self.results_tree.insert('', tk.END, values=(
            ' Best Energy',
            best_energy_method[1]['name'],
            f"{best_energy_method[1]['best_energy']:.2f}",
            ''
        ), tags=('winner',))

        self.results_tree.tag_configure(
            'winner', background='#c8e6c9', font=('Arial', 9, 'bold'))

    def plot_comparison_graphs(self, results):
        self.ax1.clear()
        self.ax2.clear()

        colors = {'1': 'blue', '2': 'red', '3': 'green'}
        method_names = {
            '1': 'Binary Tournament',
            '2': 'Random Selection',
            '3': 'Roulette Wheel'
        }

        for method_id, result in results.items():
            generations = range(1, len(result['delay_history']) + 1)
            self.ax1.plot(generations, result['delay_history'],
                          color=colors[method_id], linewidth=2,
                          label=method_names[method_id], alpha=0.7)

        self.ax1.set_title('Delay Comparison - All Methods')
        self.ax1.set_xlabel('Generation')
        self.ax1.set_ylabel('Best Delay')
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)

        for method_id, result in results.items():
            generations = range(1, len(result['energy_history']) + 1)
            self.ax2.plot(generations, result['energy_history'],
                          color=colors[method_id], linewidth=2,
                          label=method_names[method_id], alpha=0.7)

        self.ax2.set_title('Energy Comparison - All Methods')
        self.ax2.set_xlabel('Generation')
        self.ax2.set_ylabel('Best Energy')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()
        self.root.update()
    def best_delay(self,item):
        return item[1]['best_delay']
    def best_energy(self,item):
        return item[1]['best_energy']


if __name__ == "__main__":
    root = tk.Tk()
    app = FogCloudSchedulerGUI(root)
    root.mainloop()
