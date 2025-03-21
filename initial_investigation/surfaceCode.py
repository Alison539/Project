from typing import Callable, List, Dict, Any, Set, FrozenSet, Iterable, Tuple
import math
import pymatching
import stim
import matplotlib.pyplot as plt
from contextlib import redirect_stdout
import sinter
import os
import scipy.stats
import numpy as np


def sorted_complex(xs: Iterable[complex]) -> List[complex]:
    return sorted(xs, key=lambda v: (v.imag, v.real))


def target_pairs(
    measurement_qubit: complex,
    distance: int,
    time: int,
    type: int,
) -> List[complex]:

    pairs = []

    match time:
        case 0:
            data_qubit = measurement_qubit + 0.5 + 0.5 * 1j
        case 1:
            if type == 1:
                data_qubit = measurement_qubit + 0.5 - 0.5 * 1j
            else:
                data_qubit = measurement_qubit - 0.5 + 0.5 * 1j
        case 2:
            if type == 0:
                data_qubit = measurement_qubit + 0.5 - 0.5 * 1j
            else:
                data_qubit = measurement_qubit - 0.5 + 0.5 * 1j
        case 3:
            data_qubit = measurement_qubit - 0.5 - 0.5 * 1j

    if (
        data_qubit.real >= 0
        and data_qubit.real < distance
        and data_qubit.imag >= 0
        and data_qubit.imag < distance
    ):
        if type == 0:
            # measurement qubit is the control qubit
            pairs = [measurement_qubit, data_qubit]
        else:
            pairs = [data_qubit, measurement_qubit]

    return pairs


def generate_circuit_round(
    noise: float,
    distance: int,
    measurement_qubits: Dict[complex, int],
    q2i: Dict[complex, int],
    data_qubits: Set[complex],
    detectors: bool,
) -> stim.Circuit:
    circuit = stim.Circuit()

    x_qubits = [q2i[q] for q, type in measurement_qubits.items() if type == 0]
    all_measure_qubits = [q2i[q] for q, type in measurement_qubits.items()]
    all_measure_qubits.sort()

    data_indeces = [q2i[q] for q in data_qubits]
    data_indeces.sort()

    circuit.append_operation("TICK")
    circuit.append_operation("DEPOLARIZE1", data_indeces, noise)
    circuit.append_operation("H", x_qubits)
    circuit.append_operation("DEPOLARIZE1", x_qubits, noise)
    circuit.append_operation("TICK")

    for i in range(0, 4):
        pair_targets = [
            q2i[q]
            for measurement_qubit in measurement_qubits.keys()
            for q in target_pairs(
                measurement_qubit, distance, i, measurement_qubits[measurement_qubit]
            )
        ]

        circuit.append_operation("CNOT", pair_targets)
        if noise > 0:
            circuit.append_operation("DEPOLARIZE2", pair_targets, noise)
        circuit.append_operation("TICK")

    circuit.append_operation("H", x_qubits)
    circuit.append_operation("DEPOLARIZE1", x_qubits, noise)
    circuit.append_operation("TICK")
    circuit.append_operation("X_ERROR", all_measure_qubits, noise)
    circuit.append_operation("MR", all_measure_qubits)
    circuit.append_operation("X_ERROR", all_measure_qubits, noise)

    measurements_per_cycle = len(measurement_qubits)

    for m in measurement_qubits:
        record_target = []
        relative_index = q2i[m] - measurements_per_cycle
        record_target.append(stim.target_rec(relative_index))
        if detectors:
            record_target.append(
                stim.target_rec(relative_index - measurements_per_cycle)
            )
        if detectors or (not detectors and measurement_qubits[m] == 1):
            circuit.append_operation(
                "DETECTOR", record_target, [m.real * 2 + 1, m.imag * 2 + 1, 0]
            )

    circuit.append_operation("SHIFT_COORDS", [], [0, 0, 1])

    return circuit


def generate_surface_code(distance: int, rounds: int, noise: float) -> stim.Circuit:
    # step 1 = compute dictionary's and lists that say what all the points are, and edge types ...
    # need a coord system for centre of point - squared off

    # need to represent the diagram as coordinates in order to better coordinate
    data_qubits: Set[complex] = set()
    for row in range(0, distance):
        for col in range(0, distance):
            data_qubits.add(row + col * 1j)

    measure_qubits: Dict[complex, int] = (
        {}
    )  # the int represent what types of measurement
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
        location = ((col + 1) % 2) * distance - 0.5 + (col + 0.5) * 1j
        measure_qubits[location] = 1

    # need to index the qubits
    q2i: Dict[complex, int] = {
        q: i
        for i, q in enumerate(
            sorted_complex(measure_qubits) + sorted_complex(data_qubits)
        )
    }

    full_circuit = stim.Circuit()

    # adding coordinate locations
    for q, i in q2i.items():
        full_circuit.append_operation(
            "QUBIT_COORDS", [i], [q.real * 2 + 1, q.imag * 2 + 1]
        )

    full_circuit.append_operation("R", q2i.values())
    full_circuit.append_operation("X_ERROR", q2i.values(), noise)

    round_circuit_no_detectors = generate_circuit_round(
        noise=noise,
        distance=distance,
        measurement_qubits=measure_qubits,
        q2i=q2i,
        data_qubits=data_qubits,
        detectors=False,
    )

    round_circuit_yes_detectors = generate_circuit_round(
        noise=noise,
        distance=distance,
        measurement_qubits=measure_qubits,
        q2i=q2i,
        data_qubits=data_qubits,
        detectors=True,
    )

    full_circuit += round_circuit_no_detectors + round_circuit_yes_detectors * (
        rounds - 1
    )
    data_indeces = [q2i[q] for q in data_qubits]
    data_indeces.sort()

    full_circuit.append_operation("X_ERROR", data_indeces, noise)
    full_circuit.append_operation("M", data_indeces)

    num_data = len(data_qubits)
    num_measure = len(measure_qubits)
    number_of_detectors = 0
    # Basically seem to add a detector for each of the Z measurements
    for m in measure_qubits.keys():
        if measure_qubits[m] == 1:
            neighbours = []
            for j in range(0, 4):
                pairs = target_pairs(m, distance, j, 1)
                if len(pairs) > 0:
                    neighbours.append(pairs[0])

            relative_indeces = [
                stim.target_rec(-(num_data - (q2i[n] - num_measure)))
                for n in neighbours
            ]
            relative_indeces.append(stim.target_rec(q2i[m] - num_data - num_measure))
            full_circuit.append_operation(
                "DETECTOR", relative_indeces, [m.real * 2 + 1, m.imag * 2 + 1, 0]
            )
            number_of_detectors += 1

    full_circuit.append_operation(
        "OBSERVABLE_INCLUDE", [stim.target_rec(-(i + 1)) for i in range(0, distance)], 0
    )

    return full_circuit


def use_surface_code(surface_code_tasks, noise, graph_file):

    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=int(os.cpu_count() or 0),
        # num_workers=1,
        tasks=surface_code_tasks,
        decoders=["pymatching"],
        max_shots=1_000_000,
        max_errors=100,
        print_progress=False,
    )

    xs = []
    ys = []
    log_ys = []
    for stats in collected_surface_code_stats:
        d = stats.json_metadata["d"]
        if not stats.errors:
            print(f"Didn't see any errors for d={d}")
            continue
        per_shot = stats.errors / stats.shots
        per_round = sinter.shot_error_rate_to_piece_error_rate(
            per_shot, pieces=stats.json_metadata["r"]
        )
        xs.append(d)
        ys.append(per_round)
        log_ys.append(np.log(per_round))
    fit = scipy.stats.linregress(xs, log_ys)

    print(fit)

    fig, ax = plt.subplots(1, 1)
    ax.scatter(xs, ys, label=f"sampled logical error rate at p={noise[0]}")
    ax.plot(
        [0, 25],
        [np.exp(fit.intercept), np.exp(fit.intercept + fit.slope * 25)],
        linestyle="--",
        label="least squares line fit",
    )
    ax.set_ylim(1e-12, 1e-0)
    ax.set_xlim(0, 25)
    ax.semilogy()
    ax.set_title("Projecting distance needed to survive a trillion rounds")
    ax.set_xlabel("Code Distance")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which="major")
    ax.grid(which="minor")
    ax.legend()
    fig.savefig(graph_file)


def main():
    noise = 1e-3
    distance = 3
    rounds = 9
    ds = [3, 5, 7, 9]
    noises = [0.01, 0.005, 0.001]

    with open("mycircuit.txt", "w") as f:
        circuit = generate_surface_code(distance, rounds, noise)
        with redirect_stdout(f):
            print(circuit)
        circuit.diagram("detslice-with-ops-svg")
        circuit.diagram("timeline-svg")
    with open("actual.txt", "w") as f2:
        circuit = stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            distance=distance,
            rounds=rounds,
            after_clifford_depolarization=noise,
            before_measure_flip_probability=noise,
            before_round_data_depolarization=noise,
            after_reset_flip_probability=noise,
        )
        with redirect_stdout(f2):
            print(circuit)

    my_surface_code_tasks = [
        sinter.Task(
            circuit=generate_surface_code(rounds=d * 3, distance=d, noise=n),
            json_metadata={"d": d, "r": d * 3, "p": n},
        )
        for d in ds
        for n in noises
    ]
    use_surface_code(my_surface_code_tasks, noises, "my_graph.png")
    actual_surface_code_tasks = [
        sinter.Task(
            circuit=stim.Circuit.generated(
                "repetition_code:memory",
                rounds=1,
                distance=5,
                after_clifford_depolarization=0.01,
                after_reset_flip_probability=0.01,
                before_measure_flip_probability=0.01,
                before_round_data_depolarization=0.01,
            ),
            json_metadata={"d": d, "r": d * 3, "p": n},
        )
        for d in ds
        for n in noises
    ]
    use_surface_code(actual_surface_code_tasks, noises, "actual_graph.png")


def test():
    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=3,
        rounds=10000,
    )
    print(circuit)


if __name__ == "__main__":
    test()
