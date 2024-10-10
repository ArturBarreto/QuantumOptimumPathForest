# Quantum Optimum-Path Forest Project

## Overview

This project aims to solve an optimization problem over a graph using quantum optimization techniques, specifically the **Quantum Approximate Optimization Algorithm (QAOA)**. The goal is to find an optimal configuration of the graph's edges that minimizes the total cost, considering a set of constraints that shape the problem into a **Minimum Spanning Tree (MST)** with additional rules regarding depth and connectivity.

## Project Structure

```
QuantumOptimumPathForest/
├── main.py
├── graph/
│   ├── __init__.py
│   └── graph.py
├── optimization/
│   ├── __init__.py
│   └── qubo_problem.py
├── visualization/
│   ├── __init__.py
│   └── plotting.py
├── utils/
│   ├── __init__.py
│   └── config.py
└── requirements.txt
```

- **main.py**: Entry point of the program. Coordinates the execution of modules.
- **graph/**: Contains the `Graph` class responsible for creating and manipulating the graph.
- **optimization/**: Contains the `QUBOProblem` class for setting up and solving the optimization problem.
- **visualization/**: Contains functions for visualizing the graph and the results.
- **utils/**: Contains configurations, tokens, and environment variables.
- **requirements.txt**: Lists all project dependencies.

## Features

- Constructs a weighted graph based on predefined edges and weights.
- Formulates the optimization problem as a **Quadratic Unconstrained Binary Optimization (QUBO)** problem.
- Implements constraints to ensure the solution represents a valid MST.
- Utilizes QAOA to find the optimal solution, either via simulation or on actual IBM Quantum hardware.
- Visualizes the original graph and the resulting MST.

## Installation

### Prerequisites

- **Python 3.8** or higher
- **Qiskit 1.0** or higher
- **pip** (Python package installer)
- (Optional) **IBM Quantum Platform** account for running on real quantum hardware

### Clone the Repository

```bash
git clone https://github.com/ArturBarreto/QuantumOptimumPathForest.git
cd QuantumOptimumPathForest
```

### Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

## Configuration

The project uses environment variables to manage configurations:

- **`QXToken`**: Your IBM Quantum Plataform API token.
- **`SIMULATION`**: Set to `"True"` to run the simulation locally or `"False"` to run on IBM Quantum hardware.

You can set these variables in your environment or modify them directly in the `utils/config.py` file.

### Setting Environment Variables

On Unix/Linux:

```bash
export QXToken='YOUR_IBM_QUANTUM_PLATAFORM_API_TOKEN'
export SIMULATION='True'  # or 'False' to use real hardware
```

On Windows:

```cmd
set QXToken=YOUR_IBM_QUANTUM_PLATAFORM_API_TOKEN
set SIMULATION=True  # or False to use real hardware
```

**Note**: Replace `'YOUR_IBM_QUANTUM_PLATAFORM_API_TOKEN'` with your actual IBM Quantum Plataform API token and update the contact information as needed.

## Usage

Run the main script:

```bash
python main.py
```

The program will:

1. Create a weighted graph based on predefined edges.
2. Display the graph.
3. Set up the QUBO problem with the appropriate variables and constraints.
4. Solve the problem using QAOA.
5. Display the execution time and solution details.
6. Visualize the MST solution on the graph.

## Example Output

- The program will print information about the graph, the execution time, and the solution.
- Graphical windows will display the original graph and the MST solution.

## Project Details

### Graph Construction

The graph is defined with 5 nodes and weighted edges:

```python
edges = [
    (0, 1, 2),
    (0, 2, 3),
    (1, 2, 1),
    (1, 3, 4),
    (2, 3, 5),
    (2, 4, 2),
    (3, 4, 1),
    (0, 3, 6),
    (1, 4, 3)
]
```

### QUBO Problem Formulation

- **Objective Function**: Minimize the total weight of the selected edges.
- **Constraints**:
  - **Edge Count Constraint**: The number of edges selected should be `n - 1`, where `n` is the number of nodes.
  - **Connectivity Constraints**: Ensure that each node (except the root) is connected to at least one other node.
  - **Degree Constraints**: Limit the degree of each node to prevent cycles and ensure a tree structure.

### Quantum Backend

- **Simulation**: Uses `qiskit_aer` for local simulation.
- **IBM Quantum Hardware**: Can run on the least busy IBM Quantum device available.

## Dependencies

The project relies on the following Python packages:

- **qiskit**
- **qiskit-aer**
- **qiskit-optimization**
- **qiskit-ibm-runtime**
- **matplotlib**
- **networkx**

These are specified in the `requirements.txt` file.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository.
2. **Create a new branch**: `git checkout -b feature-name`.
3. **Commit your changes**: `git commit -m 'Add feature'`.
4. **Push to the branch**: `git push origin feature-name`.
5. **Open a Pull Request**.

## License

This project is licensed under the **MIT License**.

## Contact

For questions or support, please contact:

- **Artur Gomes Barreto**
- Email: [artur.barreto@alu.ufc.br](mailto:artur.barreto@alu.ufc.br)

---
