import time
from qiskit_optimization.problems import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer import AerSimulator
from qiskit.primitives import BackendSampler
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

        # 2. Cycle Prevention Constraints
        # For small graphs, we can list all cycles and ensure that not all edges in a cycle are included.
        # For larger graphs, this is impractical due to the exponential number of cycles.
        # Alternative: Use a penalty term in the objective function to penalize cycles.

        # Introduce quadratic penalties for cycles of length 3 (triangles)
        for cycle in nx.cycle_basis(self.G):
            if len(cycle) == 3:
                # Get edges in the cycle
                u, v, w = cycle
                y_uv = f'y_{min(u, v)}_{max(u, v)}'
                y_vw = f'y_{min(v, w)}_{max(v, w)}'
                y_wu = f'y_{min(w, u)}_{max(w, u)}'
                # Add penalty term to objective function
                self.qubo.minimize(
                    quadratic={(y_uv, y_vw): 1, (y_uv, y_wu): 1, (y_vw, y_wu): 1}
                )

        # Note: This approach only penalizes small cycles and may not eliminate all cycles in larger graphs.

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

        # Solve the problem
        start_time = time.time()
        qaoa_result = qaoa.solve(self.qubo)
        end_time = time.time()
        self.execution_time = end_time - start_time
        print(f"Execution time: {self.execution_time} seconds")

        # Extract the solution
        self.solution = qaoa_result.variables_dict
        print(qaoa_result.prettyprint())
        return self.solution
