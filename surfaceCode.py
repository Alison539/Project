import csv
import pathlib
import time
from dataclasses import dataclass
from typing import Callable, List, Dict, Any, Set, FrozenSet, Iterable, Tuple
import math
import pymatching
import networkx as nx
import stim
import matplotlib.pyplot as plt
from contextlib import redirect_stdout

translate_qubit_indeces = {
    0: 14,
    1: 2,
    2: 9,
    3: 16,
    4: 11,
    5: 18,
    6: 25,
    7:13,
    8:1,
    9:8,
    10:15,
    11:3,
    12:10,
    13:17,
    14:5,
    15:12,
    16:19
}

def sorted_complex(xs: Iterable[complex]) -> List[complex]:
    return sorted(xs, key=lambda v: (v.real, v.imag))

def target_pairs(
    measurement_qubit: complex,
    distance: int,
    time: int,
    type: int,
) -> List[complex]:
    
    pairs = []

    match time:
        case 0:
            data_qubit = measurement_qubit - 0.5 + 0.5*1j
        case 1:
            if type == 0:
                data_qubit = measurement_qubit - 0.5 - 0.5*1j
            else:
                data_qubit = measurement_qubit + 0.5 + 0.5*1j
        case 2:
            if type == 1:
                data_qubit = measurement_qubit - 0.5 - 0.5*1j
            else:
                data_qubit = measurement_qubit + 0.5 + 0.5*1j
        case 3:
            data_qubit = measurement_qubit + 0.5 - 0.5*1j

    if data_qubit.real >= 0 and data_qubit.real < distance and data_qubit.imag >= 0 and data_qubit.imag < distance:
        if type == 0:
            # measurement qubit is the control qubit
            pairs = [measurement_qubit,data_qubit]
        else:
            pairs = [data_qubit,measurement_qubit]
    
    return pairs

def generate_circuit_round(
    noise: float,
    distance: int,
    measurement_qubits: Dict[complex,int],
    q2i: Dict[complex,int],
    data_qubits: Set[complex],
    detectors: bool
) -> stim.Circuit:
    circuit = stim.Circuit()

    x_qubits = [q2i[q] for q,type in measurement_qubits.items() if type == 0]
    all_qubits = [q2i[q] for q,type in measurement_qubits.items()]

    circuit.append_operation("H", x_qubits)
    circuit.append_operation("TICK")

    for i in range(0, 4):
        pair_targets = [
            q2i[q]
            for measurement_qubit in measurement_qubits.keys()
            for q in target_pairs(measurement_qubit,distance,i,measurement_qubits[measurement_qubit])
        ]

        if noise > 0:
            circuit.append_operation("DEPOLARIZE2", pair_targets, noise)
            circuit.append_operation("TICK")
        circuit.append_operation("CNOT", pair_targets)
        circuit.append_operation("TICK")

    circuit.append_operation("H", x_qubits)
    circuit.append_operation("TICK")
    circuit.append_operation("MR", all_qubits)
    circuit.append_operation("TICK")

    if detectors:
        measurements_per_cycle = len(measurement_qubits)

        for m in measurement_qubits:
            record_target = []
            relative_index = q2i[m] - measurements_per_cycle
            record_target.append(stim.target_rec(relative_index))
            record_target.append(stim.target_rec(relative_index - measurements_per_cycle))

            circuit.append_operation("DETECTOR", record_target, [m*2 + 1, m.imag*2 + 1, 0])

        circuit.append_operation("SHIFT_COORDS", [], [0,0,1] )

    return circuit
    



def generate_surface_code(distance: int, rounds: int, noise: float) -> stim.Circuit:
    # step 1 = compute dictionary's and lists that say what all the points are, and edge types ...
    # need a coord system for centre of point - squared off

    # need to represent the diagram as coordinates in order to better coordinate
    data_qubits: Set[complex] = set()
    for row in range(0, distance):
        for col in range(0, distance):
            data_qubits.add(row + col * 1j)
    
    measure_qubits: Dict[complex, int] = {} #the int represent what types of measurement
    measurement_type = 0
    for row in range(0, distance - 1):
        measurement_type = 0
        for col in range(0, distance):
            location = row + 0.5 + col * 1j
            if row % 2 == 0:
                location -= 0.5 * 1j
            else:
                location += 0.5 * 1j
            measure_qubits[location] = measurement_type
            measurement_type = (measurement_type + 1) % 2
    for col in range(0, distance - 1):
        location = ((col + 1) % 2) * distance - 0.5 + (col + 0.5)*1j
        measure_qubits[location] = 1

    #need to index the qubits
    q2i: Dict[complex,int] = {
        q: i for i, q in enumerate(sorted_complex(measure_qubits) + sorted_complex(data_qubits))
    }

    full_circuit = stim.Circuit()

    # adding coordinate locations
    for q, i in (q2i.items()):
        full_circuit.append_operation("QUBIT_COORDS", [i], [q.real*2 + 1, q.imag*2 + 1])

    full_circuit.append_operation("R", q2i.values())
    full_circuit.append_operation("TICK")

    round_circuit_no_detectors = generate_circuit_round(
        noise=noise,
        distance=distance,
        measurement_qubits=measure_qubits,
        q2i=q2i,
        data_qubits=data_qubits,
        detectors=False
    )

    round_circuit_yes_detectors = generate_circuit_round(
        noise=noise,
        distance=distance,
        measurement_qubits=measure_qubits,
        q2i=q2i,
        data_qubits=data_qubits,
        detectors=True
    )

    full_circuit += (
        round_circuit_yes_detectors * rounds 
    )

    full_circuit.append_operation("M", [q2i[q] for q in data_qubits])
    full_circuit.append_operation("TICK")
    full_circuit.append_operation("OBSERVABLE_INCLUDE", [stim.target_rec(-(i+1)) for i in range(0, distance)], 0)

    return full_circuit

def main():
    with open('mycircuit.txt', 'w') as f:
        circuit = generate_surface_code(3,1,0)
        with redirect_stdout(f):
            print(circuit)
    with open('actual.txt','w') as f2:
        circuit = stim.Circuit.generated("surface_code:rotated_memory_z", distance=3,rounds=1)
        with redirect_stdout(f2):
            print(circuit)


if __name__ == "__main__":
    main()
