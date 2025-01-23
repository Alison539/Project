from flask import Blueprint, jsonify, request
from contextlib import redirect_stdout
from typing import List, Dict
import stim
import math

# currently all inputs are directly accessible apart from qubit operations - which is accessible as a map
def generate_stim(coord_sys: int,       
    qubit_operations: List[Dict],
    two_qubit_operations: List[List[List[int]]],
    noise: List[float],
    num_cycles: int):

    def translate_coordinates(location_dict: Dict):
        x = location_dict.get("x")
        y = location_dict.get("y")
        if (coord_sys == 1):
            x = x + (y %2) *0.5
            y = y*math.sin(math.pi / 3)
        return [x,y]
    
    num_qubits: int = len(qubit_operations)

    data_qubits: List[int] = []
    measurement_qubits: List[int] = []
    x_qubits: List[int] = []
    y_qubits: List[int] = []
    logical_observable_qubits: List[int] = []

    measurements_per_cycle = len(measurement_qubits)

    for i in range(0, num_qubits):
        qubit_info = qubit_operations[i]
        if qubit_info.get("measurement") == 0:
            data_qubits.append(i)
        else:
            measurement_qubits.append(i)
        qubit_type = qubit_info.get("hadamard")
        if qubit_type == 1:
            x_qubits.append(i)
        elif qubit_type == 2:
            y_qubits.append(i)
        if qubit_info.get("logical_observable"):
            logical_observable_qubits.append(i)

    cnot_operations: List[List[int]] = []
    for i in range(0, num_qubits):
        for j in range(0, num_qubits):
            timesteps = two_qubit_operations[i][j]
            if len(timesteps) > 0:
                for time in timesteps:
                    while time > len(cnot_operations):
                        cnot_operations.append([])
                    cnot_operations[time - 1].append(i)
                    cnot_operations[time - 1].append(j)
    
    
    def generate_circuit_round(detectors: bool):
        circuit = stim.Circuit()

        circuit.append_operation("TICK")
        circuit.append_operation("DEPOLARIZE1", data_qubits, noise[3])
        
        circuit.append_operation("H", x_qubits)
        circuit.append_operation("H_YZ", y_qubits)
        circuit.append_operation("DEPOLARIZE1", x_qubits + y_qubits, noise[0])
        circuit.append_operation("TICK")
        
        for time in range(0, len(cnot_operations)):
            circuit.append_operation("CNOT", cnot_operations[time])
            circuit.append_operation("DEPOLARIZE2", cnot_operations[time], noise[1])
            circuit.append_operation("TICK")

        
        circuit.append_operation("H_YZ", y_qubits)
        circuit.append_operation("H", x_qubits)
        circuit.append_operation("DEPOLARIZE1", x_qubits + y_qubits, noise[0])
        circuit.append_operation("TICK")

        circuit.append_operation("X_ERROR", measurement_qubits, noise[2])
        circuit.append_operation("MR", measurement_qubits)
        circuit.append_operation("X_ERROR", measurement_qubits, noise[4])
        
        for m in range(0, measurements_per_cycle):
            record_target = []
            relative_index = m - measurements_per_cycle
            record_target.append(stim.target_rec(relative_index))
            if detectors:
                record_target.append(stim.target_rec(relative_index - measurements_per_cycle))
                # TODO: if add basis add detectors if detectors not defined
                coords = translate_coordinates(measurement_qubits[m.get("location")])
                circuit.append_operation("DETECTOR",record_target, [coords] + [0])
            
        circuit.append_operation("SHIFT_COORDS", [], [0,0,1] )

        return circuit


    full_circuit = stim.Circuit()

    for i in range(0, num_qubits):
        coords = translate_coordinates(qubit_operations[i].get("location"))
        full_circuit.append_operation("QUBIT_COORDS", [i], coords)

    full_circuit.append_operation("R", [i for i in range(0, num_qubits)] )
    full_circuit.append_operation("X_ERROR", [i for i in range(0, num_qubits)], noise[4])

    round_circuit_no_detectors = generate_circuit_round(detectors = False)
    round_circuit_yes_detectors = generate_circuit_round(detectors = True)

    full_circuit += (
        round_circuit_no_detectors +
        round_circuit_yes_detectors * (num_cycles - 1)
    )

    full_circuit.append_operation("X_ERROR",data_qubits,noise[2])
    full_circuit.append_operation("M",data_qubits)

    # TODO: if add basis then add detectors on all measurements that are in that basis

    relative_indeces = []
    for q in logical_observable_qubits:
        # TODO: currently relies on fact that no measurement qubits are part of the logical observable (which is the only option that makes sense)
        relative_indeces.append(stim.target_rec(data_qubits.index(q) - len(data_qubits)))
    full_circuit.append_operation("OBSERVABLE_INCLUDE", relative_indeces, 0)

    return full_circuit
                


api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/qec_data', methods=['POST'])
def qec_data():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid or missing data"}), 400
    
    coord_sys = data.get('coordSys')
    qubit_operations = data.get('qubitOperations',[])
    two_qubit_operations = data.get("twoQubitOperations",[])
    noise = data.get("noise",[])
    num_cycles = data.get("numCycles")

    toReturn = ""
    with open('new_circuit.txt', 'w') as f:
        circuit = generate_stim(coord_sys=coord_sys, qubit_operations=qubit_operations, two_qubit_operations=two_qubit_operations,noise=noise,num_cycles=num_cycles)
        with redirect_stdout(f):
            print(circuit)
    with open('new_circuit.txt', 'r') as f:
        toReturn = f.read()
    
    return jsonify({"stimcode": (toReturn) })