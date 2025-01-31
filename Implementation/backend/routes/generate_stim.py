from typing import List, Dict
import stim
import math

error = ["X_ERROR","Z_ERROR","Y_ERROR"]
measure_reset = ["MR","MRX","MRY"]
measure = ["M","MX","MY"]
reset = ["R","RX","RY"]

# currently all inputs are directly accessible apart from qubit operations - which is accessible as a map
def generate_stim(coord_sys: int,       
    qubit_operations: List[Dict],
    two_qubit_operations: List[List[List[int]]],
    noise: List[float],
    num_cycles: int,
    name: str,
    basis: int):

    def translate_coordinates(location_dict: Dict):
        x = location_dict.get("x")
        y = location_dict.get("y")
        if (coord_sys == 1):
            x = x + (y %2) *0.5
            y = y*math.sin(math.pi / 3)
        return [x,y]
    
    num_qubits: int = len(qubit_operations)

    data_qubits: List[int] = []
    measure_qubits = [[],[],[]]
    x_qubits: List[int] = []
    y_qubits: List[int] = []
    logical_observable_qubits: List[int] = []

    for i in range(0, num_qubits):
        qubit_info = qubit_operations[i]
        measurement = qubit_info.get("measurement")
        if measurement == 0:
            data_qubits.append(i)
        else:
            measure_qubits[measurement - 1].append(i)

        qubit_type = qubit_info.get("hadamard")
        if qubit_type == 1:
            x_qubits.append(i)
        elif qubit_type == 2:
            y_qubits.append(i)
        if qubit_info.get("logical_observable"):
            logical_observable_qubits.append(i)

    measure_qubits_given_basis = [
        list(set(measure_qubits[0]) - set(x_qubits) - set(y_qubits)),
        measure_qubits[1] + x_qubits,
        measure_qubits[2] + y_qubits,
    ]
    # TODO: currently basically saying only do hadamard when doing measurements in Z - if not true, code is broken

    num_qubit_measures = [len(measure_qubits[i]) for i in [0,1,2]]
    num_x_qubits = len(x_qubits)
    num_y_qubits = len(y_qubits)
    num_logical_observable = len(logical_observable_qubits)

    measurement_qubits = measure_qubits[0] + measure_qubits[1] + measure_qubits[2]
    measurements_per_cycle = len(measurement_qubits)

    not_used = [True for i in range(0, num_qubits)]
    cnot_operations: List[List[int]] = []
    for i in range(0, num_qubits):
        for j in range(0, num_qubits):
            timesteps = two_qubit_operations[i][j]
            if len(timesteps) > 0:
                not_used[i] = False
                not_used[j] = False
                for time in timesteps:
                    while time > len(cnot_operations):
                        cnot_operations.append([])
                    cnot_operations[time - 1].append(i)
                    cnot_operations[time - 1].append(j)

    not_used_qubits = []
    for i in range(0, num_qubits):
        if (not_used[i]):
            not_used_qubits.append(i)
    data_qubits = list(set(data_qubits) - set(not_used_qubits))
    num_data_qubits = len(data_qubits)


    def generate_circuit_round(detectors: bool):
        circuit = stim.Circuit()

        circuit.append_operation("TICK")
        if noise[3] > 0: circuit.append_operation("DEPOLARIZE1", data_qubits, noise[3])
        
        if num_x_qubits > 0:
            circuit.append_operation("H", x_qubits)
        if num_y_qubits > 0:
            circuit.append_operation("H_YZ", y_qubits)
        if (num_y_qubits + num_x_qubits) > 0:
            if noise[0] >0: circuit.append_operation("DEPOLARIZE1", x_qubits + y_qubits, noise[0])
            circuit.append_operation("TICK")
        
        for time in range(0, len(cnot_operations)):
            circuit.append_operation("CNOT", cnot_operations[time])
            if noise[1] > 0: circuit.append_operation("DEPOLARIZE2", cnot_operations[time], noise[1])
            circuit.append_operation("TICK")

        
        if num_y_qubits > 0:
            circuit.append_operation("H_YZ", y_qubits)
        if num_x_qubits > 0:
            circuit.append_operation("H", x_qubits)
        if (num_y_qubits + num_x_qubits) > 0:
            if noise[0] > 0: circuit.append_operation("DEPOLARIZE1", x_qubits + y_qubits, noise[0])
            circuit.append_operation("TICK")

        for i in range(0,3):
            if (num_qubit_measures[i] > 0):
                if noise[2] > 0 : circuit.append_operation(error[i], measure_qubits[i], noise[2])
                circuit.append_operation(measure_reset[i], measure_qubits[i])
                if noise[4] > 0 : circuit.append_operation(error[i], measure_qubits[i], noise[4])
        
        for m in range(0, measurements_per_cycle):
            mqubit_id = measurement_qubits[m]
            record_target = []
            relative_index = m - measurements_per_cycle
            record_target.append(stim.target_rec(relative_index))
            if detectors:
                record_target.append(stim.target_rec(relative_index - measurements_per_cycle))
            if detectors or (mqubit_id in measure_qubits_given_basis[basis]):
                coords = translate_coordinates(qubit_operations[mqubit_id].get("location"))
                circuit.append_operation("DETECTOR",record_target, coords + [0])
            
        circuit.append_operation("SHIFT_COORDS", [], [0,0,1] )

        return circuit

    def get_relative_indeces_for_basis_detectors(m):
        relative_indeces = []
        relative_index = measurement_qubits.index(m) - measurements_per_cycle - num_data_qubits
        relative_indeces.append(stim.target_rec(relative_index))
        for j in range(0, num_qubits):
            timesteps = two_qubit_operations[j][m]
            if len(timesteps) > 0:
                if j in data_qubits:               
                    relative_indeces.append(stim.target_rec(data_qubits.index(j)  - num_data_qubits))
            timesteps = two_qubit_operations[m][j]
            if len(timesteps) > 0:
                if j in data_qubits:
                    relative_indeces.append(stim.target_rec(data_qubits.index(j)   - num_data_qubits))
        return relative_indeces
    
    full_circuit = stim.Circuit()

    for i in range(0, num_qubits):
        if not not_used[i]:
            coords = translate_coordinates(qubit_operations[i].get("location"))
            full_circuit.append_operation("QUBIT_COORDS", [i], coords)

    
    full_circuit.append_operation(reset[basis], data_qubits )
    if noise[4] > 0: full_circuit.append_operation(error[basis], data_qubits, noise[4])

    for i in [0,1,2]:
        if num_qubit_measures[i] > 0:
            full_circuit.append_operation(reset[i], measure_qubits[i] )
            if noise[4] > 0: full_circuit.append_operation(error[i], measure_qubits[i] , noise[4])
    
    round_circuit_no_detectors = generate_circuit_round(detectors = False)
    round_circuit_yes_detectors = generate_circuit_round(detectors = True)

    full_circuit += (
        round_circuit_no_detectors +
        round_circuit_yes_detectors * (num_cycles - 1)
    )

    if noise[2] > 0: full_circuit.append_operation(error[basis],data_qubits,noise[2])
    full_circuit.append_operation(measure[basis],data_qubits)
    

    if (len(measure_qubits_given_basis[basis]) > 0):
        for m in (measure_qubits_given_basis[basis]):
                relative_indeces = get_relative_indeces_for_basis_detectors(m)
                coords = translate_coordinates(qubit_operations[m].get("location"))
                full_circuit.append_operation("DETECTOR",relative_indeces, coords + [0])

    relative_indeces = []
    for q in logical_observable_qubits:
        if q not in measurement_qubits:
            relative_indeces.append(stim.target_rec(data_qubits.index(q) - len(data_qubits)))
    if num_logical_observable   > 0:
        full_circuit.append_operation("OBSERVABLE_INCLUDE", relative_indeces, 0)

    return full_circuit

