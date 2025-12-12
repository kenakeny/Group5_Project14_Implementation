# Cloud Resource Allocation Using NSGA-II —

This project is for Group 5, Logic and AI module.
The project implements a Cloud & Fog Resource Allocation System using the NSGA-II (Non-Dominated Sorting Genetic Algorithm II).  
The application includes a full Python GUI built using **Tkinter** and **Matplotlib**, allowing users to configure environment parameters, load tasks, run the optimizer, and visualize the resulting Pareto-optimal solutions.

---

## Features

### NSGA2 Optimization
- Fast non-dominated sorting    
- Tournament,Roulette wheel and Random selection  
- Crossover and mutation operations  
- Multi-objective optimization for:
  - Execution time  
  - Energy consumption  

### GUI Application (Tkinter)
- Configure fog and cloud nodes
- Set NSGA-II parameters
- Visualize Pareto fronts (Matplotlib)
- View best Solutions
---

## Project Structure
```
Group5_Project14_Implementation/
├── src/                          # All source code files
│   ├── main.py                   # Main entry point
│   ├── NSGA.py                   # First algorithm implementation
│   ├── gui.py                    # GUI implementation
│   ├── utils.py                  # Helper functions and parameters
│
├── requirements.txt              # Required Python libraries
├── README.md                     # Setup and execution instructions
└── UserManual.pdf                # How to use your application
```
