import time
from qiskit_optimization.problems import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer import AerSimulator
from qiskit.primitives import BackendSampler

class QUBOProblem:
    def __init__(self, G, config):
        self.qubo = QuadraticProgram()
        self.G = G
        self.n = G.number_of_nodes()
        self.config = config
        self.solution = None
        self.execution_time = 0

    def configure_variables(self):
        for (i, j, w) in self.G.edges(data='weight'):
            var_name = f'y_{min(i, j)}_{max(i, j)}'
            self.qubo.binary_var(name=var_name)

    def define_objective_function(self):
        objective_terms = {
            f'y_{min(i, j)}_{max(i, j)}': w for (i, j, w) in self.G.edges(data='weight')
        }
        self.qubo.minimize(linear=objective_terms)

    def add_constraints(self):
        # 1. Edge Count Constraint
        edge_count_constraint = {
            f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in self.G.edges()
        }
        self.qubo.linear_constraint(
            linear=edge_count_constraint,
            sense='==',
            rhs=self.n - 1,
            name='edge_count_constraint'
        )
        # 4. Connectivity Constraints
        for v in range(1, self.n):
            connectivity_constraint = {
                f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in self.G.edges(v)
            }
            self.qubo.linear_constraint(
                linear=connectivity_constraint,
                sense='>=',
                rhs=1,
                name=f'connectivity_{v}'
            )
        # 5. Degree Constraints
        max_degree = self.n - 1
        for v in range(self.n):
            degree_constraint = {
                f'y_{min(i, j)}_{max(i, j)}': 1 for (i, j) in self.G.edges(v)
            }
            self.qubo.linear_constraint(
                linear=degree_constraint,
                sense='<=',
                rhs=max_degree,
                name=f'degree_constraint_{v}'
            )

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
        optimizer = COBYLA()
        p = 1  # QAOA circuit depth
        qaoa_mes = QAOA(sampler=sampler, optimizer=optimizer, reps=p)
        qaoa = MinimumEigenOptimizer(qaoa_mes)

        start_time = time.time()
        qaoa_result = qaoa.solve(self.qubo)
        end_time = time.time()

        self.execution_time = end_time - start_time
        self.solution = qaoa_result.variables_dict
        print(f"Execution time: {self.execution_time} seconds")
        print(qaoa_result.prettyprint())
        return self.solution
