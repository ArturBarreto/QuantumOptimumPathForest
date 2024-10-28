import time
from qiskit_optimization.problems import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer import AerSimulator
from qiskit.primitives import BackendSampler
from visualization.plotting import draw_solution
import networkx as nx

class QUBOProblem:
    def __init__(self, G, config):
        self.qubo = QuadraticProgram()
        self.G = G
        self.n = G.number_of_nodes()
        self.config = config
        self.solution = None
        self.execution_time = 0

    def configure_variables(self):
        # Edge inclusion variables y_{uv}
        for (u, v, w) in self.G.edges(data='weight'):
            var_name = f'y_{min(u, v)}_{max(u, v)}'
            self.qubo.binary_var(name=var_name)

    def define_objective_function(self):
        # Minimize the total cost of the included edges
        objective_terms = {
            f'y_{min(u, v)}_{max(u, v)}': w for (u, v, w) in self.G.edges(data='weight')
        }
        self.qubo.minimize(linear=objective_terms)

    def add_constraints(self):
        # 1. Edge Count Constraint: sum of y_{uv} = n - 1
        edge_count_constraint = {
            f'y_{min(u, v)}_{max(u, v)}': 1 for (u, v) in self.G.edges()
        }
        self.qubo.linear_constraint(
            linear=edge_count_constraint,
            sense='==',
            rhs=self.n - 1,
            name='edge_count_constraint'
        )

        # 2. Cycle Prevention Penalty Terms
        for cycle in nx.cycle_basis(self.G):
            cycle_edges = []
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i + 1) % len(cycle)]
                y_uv = f'y_{min(u, v)}_{max(u, v)}'
                cycle_edges.append(y_uv)

            # Add quadratic penalty terms for all pairs of edges in the cycle
            for i in range(len(cycle_edges)):
                for j in range(i + 1, len(cycle_edges)):
                    var_i = cycle_edges[i]
                    var_j = cycle_edges[j]
                    # Add penalty term
                    self.qubo.minimize(
                        quadratic={(var_i, var_j): 1e5}
                    )

        # 3. Connectivity Constraint
        # Ensure that the graph is connected.
        # For simplicity, we can enforce that each node is connected to at least one other node.

        for v in self.G.nodes():
            connected_edges = {
                f'y_{min(u, v)}_{max(u, v)}': 1 for u in self.G.neighbors(v)
            }
            self.qubo.linear_constraint(
                linear=connected_edges,
                sense='>=',
                rhs=1,
                name=f'connectivity_constraint_{v}'
            )

        # Note: This does not guarantee global connectivity but improves the likelihood.

    def configure_backend(self):
        if self.config.SIMULATION == "True":
            print("Proceeding with simulation...")
            backend = AerSimulator()
        else:
            print("Proceeding with IBM Quantum hardware...")
            service = QiskitRuntimeService(channel='ibm_quantum', token=self.config.QXToken)
            backend = service.least_busy(n_qubits=127, operational=True, simulator=False)
            print(f"Connected to {backend.name}!")
        return backend

    def solve_problem(self):
        backend = self.configure_backend()
        sampler = BackendSampler(backend=backend)

        # Setup optimizer and solver
        optimizer = COBYLA()
        p = 1  # QAOA circuit depth
        qaoa_mes = QAOA(sampler=sampler, optimizer=optimizer, reps=p)
        qaoa = MinimumEigenOptimizer(qaoa_mes)

        cycle_constraints = []  # List to store cycle constraints

        iteration = 0  # Iteration counter

        while True:
            iteration += 1
            print(f"\nIteration {iteration}")

            # Create a new QuadraticProgram for each iteration
            self.qubo = QuadraticProgram()

            # Define variables
            self.configure_variables()

            # Define the objective function
            self.define_objective_function()

            # Add initial constraints
            self.add_constraints()

            # Add accumulated cycle constraints
            for idx, (constraint_vars, rhs) in enumerate(cycle_constraints):
                constraint_name = f'cycle_constraint_{idx}'
                self.qubo.linear_constraint(
                    linear=constraint_vars,
                    sense='LE',
                    rhs=rhs,
                    name=constraint_name
                )

            # Solve the problem
            start_time = time.time()
            qaoa_result = qaoa.solve(self.qubo)
            end_time = time.time()
            self.execution_time = end_time - start_time
            print(f"Execution time: {self.execution_time} seconds")

            # Extract the solution
            solution = qaoa_result.variables_dict
            print(qaoa_result.prettyprint())

            # Extract selected edges based on the solution
            selected_edges = []
            for (u, v) in self.G.edges():
                y_var = f'y_{min(u, v)}_{max(u, v)}'
                if solution.get(y_var, 0) > 0.5:  # Use a threshold to account for numerical precision
                    selected_edges.append((u, v))

            # Build the subgraph of selected edges
            subgraph = nx.Graph()
            subgraph.add_edges_from(selected_edges)

            # Check for cycles in the subgraph
            cycles = list(nx.cycle_basis(subgraph))
            if not cycles:
                # No cycles detected, solution is a valid tree
                self.solution = solution
                print(
                    f"Solution found after {iteration} iterations with {len(cycle_constraints)} cycle constraints added.")
                # Exit the loop as we have a valid MST
                return self.solution
            else:
                draw_solution(self.G, solution, title=f'Iteration {iteration}')
                # Add constraints to eliminate detected cycles in the next iteration
                for cycle in cycles:
                    cycle_edges = []
                    for i in range(len(cycle)):
                        u = cycle[i]
                        v = cycle[(i + 1) % len(cycle)]  # Wrap around to form a cycle
                        y_uv = f'y_{min(u, v)}_{max(u, v)}'
                        cycle_edges.append(y_uv)

                    # Prepare constraint: sum of y_uv in the cycle <= len(cycle) - 1
                    constraint_vars = {y_uv: 1 for y_uv in cycle_edges}
                    rhs = len(cycle_edges) - 1

                    # Store the constraint to add it in the next iteration
                    cycle_constraints.append((constraint_vars, rhs))

                print(f"Added {len(cycles)} cycle constraints, total accumulated: {len(cycle_constraints)}")
