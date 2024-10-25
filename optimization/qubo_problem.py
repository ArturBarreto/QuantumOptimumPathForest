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
        self.max_depth = None
        self.root_node = None
        self.execution_time = 0

    def configure_variables(self):
        # Define maximum depth (can be adjusted)
        # self.max_depth = self.n  # Assuming maximum depth equals the number of nodes
        self.max_depth = 1

        # Define root node (for simplicity, choosing node 0)
        self.root_node = 0

        # Binary variables for node depths x_{v,i}
        for v in self.G.nodes():
            for i in range(self.max_depth):
                self.qubo.binary_var(name=f'x_{v}_{i}')

        # Binary variables for edge inclusion y_{u_v}
        for (u, v) in self.G.edges():
            var_name = f'y_{min(u, v)}_{max(u, v)}'
            self.qubo.binary_var(name=var_name)

        # Binary variables for edge directions and depths x_{u_v_i}, x_{v_u_i}
        for (u, v) in self.G.edges():
            for i in range(1, self.max_depth):
                self.qubo.binary_var(name=f'x_{u}_{v}_{i}')
                self.qubo.binary_var(name=f'x_{v}_{u}_{i}')

    def define_objective_function(self):
        # Objective: Minimize total cost of the edges included
        objective_terms = {}
        for (u, v, w) in self.G.edges(data='weight'):
            for i in range(1, self.max_depth):
                objective_terms[f'x_{u}_{v}_{i}'] = w
                objective_terms[f'x_{v}_{u}_{i}'] = w
        self.qubo.minimize(linear=objective_terms)

    def add_constraints(self):
        # 1. Root Node Constraint: Exactly one root node at depth 0
        root_vars = {f'x_{v}_0': 1 for v in self.G.nodes()}
        self.qubo.linear_constraint(
            linear=root_vars,
            sense='==',
            rhs=1,
            name='root_node_constraint'
        )

        # 2. Vertex Depth Assignment: Each node must be assigned exactly one depth
        for v in self.G.nodes():
            depth_vars = {f'x_{v}_{i}': 1 for i in range(self.max_depth)}
            self.qubo.linear_constraint(
                linear=depth_vars,
                sense='==',
                rhs=1,
                name=f'depth_assignment_{v}'
            )

        # 3. Edge inclusion linked to edge depth variables
        for (u, v) in self.G.edges():
            edge_var = f'y_{min(u, v)}_{max(u, v)}'
            edge_depth_vars = {}
            for i in range(1, self.max_depth):
                edge_depth_vars[f'x_{u}_{v}_{i}'] = 1
                edge_depth_vars[f'x_{v}_{u}_{i}'] = 1
            constraint_vars = {edge_var: -1, **edge_depth_vars}
            self.qubo.linear_constraint(
                linear=constraint_vars,
                sense='==',
                rhs=0,
                name=f'edge_depth_link_{u}_{v}'
            )

        # 4. Connectivity Constraints: Each non-root node connects to exactly one parent
        for v in self.G.nodes():
            if v != self.root_node:
                for i in range(1, self.max_depth):
                    parent_edge_vars = {f'x_{u}_{v}_{i}': 1 for u in self.G.neighbors(v)}
                    self.qubo.linear_constraint(
                        linear=parent_edge_vars,
                        sense='==',
                        rhs=1,
                        name=f'connectivity_{v}_{i}'
                    )

        # 5. Degree Constraint: Degree of each node does not exceed max_degree
        max_degree = self.n - 1  # Adjust as needed
        for v in self.G.nodes():
            degree_vars = {f'y_{min(u, v)}_{max(u, v)}': 1 for u in self.G.neighbors(v)}
            self.qubo.linear_constraint(
                linear=degree_vars,
                sense='<=',
                rhs=max_degree,
                name=f'degree_constraint_{v}'
            )

        # 6. Depth consistency between nodes and edges
        for (u, v) in self.G.edges():
            for i in range(1, self.max_depth):
                # x_{u_v_i} <= x_{u_{i-1}}
                self.qubo.linear_constraint(
                    linear={f'x_{u}_{v}_{i}': 1, f'x_{u}_{i-1}': -1},
                    sense='<=',
                    rhs=0,
                    name=f'depth_consistency_u_{u}_{v}_{i}'
                )
                # x_{u_v_i} <= x_{v_i}
                self.qubo.linear_constraint(
                    linear={f'x_{u}_{v}_{i}': 1, f'x_{v}_{i}': -1},
                    sense='<=',
                    rhs=0,
                    name=f'depth_consistency_v_{u}_{v}_{i}'
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
