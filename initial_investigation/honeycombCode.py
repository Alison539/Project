# following Craig Gidney's youtube video - https://www.youtube.com/watch?v=E9yj0o1LGII
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


# writing test
def print_2d(values: Dict[complex, int]):
    assert all(v.real == int(v.real) for v in values)  # should all be integers
    assert all(v.imag == int(v.imag) for v in values)  # should all be integers
    assert all(v.real >= 0 and v.imag >= 0 for v in values)  # should be >= 0
    m = int(max((v.real for v in values), default=0) + 1)
    h = int(max((v.imag for v in values), default=0) + 1)
    s = ""
    for y in range(h):
        for x in range(m):
            s += str(
                values.get(x + y * 1j, "_")
            )  # means if not there default to underscore
        s += "\n"
    print(s)


# Because the honeycomb code is on a torus should be able to wrap around
def torus(c: complex, *, distance: int) -> complex:
    r = c.real % (distance * 4)
    i = c.imag % (distance * 6)
    return r + i * 1j


@dataclass
class EdgeType:
    pauli: str
    hex_to_hex_delta: complex
    hex_to_qubit_delta: complex


def sorted_complex(xs: Iterable[complex]) -> List[complex]:
    return sorted(xs, key=lambda v: (v.real, v.imag))


# basically this used to be in the original make_circuits function, but have taken out in order to make if noise is present a parameter
def generate_circuit_rounds_parameterized(
    *,
    noise: float,
    hex_centers: Dict[complex, int],
    distance: int,
    q2i: Dict[complex, int],
    edge_types,
    edges_around_hex,
    qubit_coordinates,
    detectors: bool,  # want initial rounds not to have detectors
) -> stim.Circuit:
    # we need to know when things happened
    measurement_times: Dict[FrozenSet[int], int] = {}
    current_time = 0
    measurements_per_round: int

    # now have enough info to make the circuit
    round_circuits = []
    for r in range(3):
        # there will be 3 given rounds one for each of x,y,z
        relevant_hexes = [h for h, category in hex_centers.items() if category == r]
        # want to spearately store x, y and z
        edge_groups: Dict[str, List[FrozenSet[complex]]] = {"X": [], "Y": [], "Z": []}

        for h in relevant_hexes:
            for edge_type in edge_types:
                q1 = torus(h + edge_type.hex_to_qubit_delta, distance=distance)
                q2 = torus(
                    h + edge_type.hex_to_hex_delta - edge_type.hex_to_qubit_delta,
                    distance=distance,
                )
                edge_groups[edge_type.pauli].append(frozenset([q1, q2]))

        circuit = stim.Circuit()
        # need to fix fact that some are X, some Y some Z - need to all be made in Z measurements that we want to do

        x_qubits = [q2i[q] for pair in edge_groups["X"] for q in sorted_complex(pair)]
        y_qubits = [q2i[q] for pair in edge_groups["Y"] for q in sorted_complex(pair)]
        # dont need z since default is Z

        # adding more errors
        # if noise > 0:
        #    circuit.append_operation("DEPOLARIZE1", [q2i[q] for q in qubit_coordinates], noise)

        # make all the parity operations Z basis parities
        circuit.append_operation("H", x_qubits)
        # for y qubits should rotate around X+Z
        circuit.append_operation("H_YZ", y_qubits)

        # turn parirty observables into single qubit observables
        # this involves CNOT operations between each of the pair targets
        pair_targets = [
            q2i[q]
            for group in edge_groups.values()
            for pair in group
            for q in sorted_complex(pair)  # the pair is the control and target
        ]
        # easiest place to put errors is on 2-qubit operations
        if noise > 0:  # so that slightly neater
            circuit.append_operation("DEPOLARIZE2", pair_targets, noise)
        circuit.append_operation("CNOT", pair_targets)

        # Measure = going to measure the second of the CNOT pairs as that is where the parity went
        for k in range(0, len(pair_targets), 2):
            edge_key = frozenset([pair_targets[k], pair_targets[k + 1]])
            measurement_times[edge_key] = current_time
            current_time += 1
        circuit.append_operation("M", pair_targets[1::2])

        # restore qubit bases
        circuit.append_operation("CNOT", pair_targets)
        circuit.append_operation("H_YZ", y_qubits)
        circuit.append_operation("H", x_qubits)

        included_measurements = []
        for group in edge_groups.values():
            for pair in group:
                a, b = pair
                if a.real == b.real == 1:
                    # this is one of the measurements to include in observable
                    edge_key = frozenset([q2i[a], q2i[b]])
                    included_measurements.append(
                        stim.target_rec(measurement_times[edge_key] - current_time)
                    )
        circuit.append_operation("OBSERVABLE_INCLUDE", included_measurements, 0)

        round_circuits.append(circuit)
    measurements_per_cycle = current_time
    measurements_per_round = measurements_per_cycle // 3

    # want to add the observable into the circuit
    # saying how to measure at the end of the circuit
    # say how to update it from round to round during the circuit

    # in order for observables to work need to be keeping track of from the start
    if detectors:
        # det_circuits = [] #kept detector separate as need to do a few rounds before stable - as in very first round nothing to compare to
        for r in range(3):
            # this is going to be running at the end of a cycle (so just did all 0s, all 1s, all 2s)
            circuit = stim.Circuit()
            relevant_hexes = [
                h for h, category in hex_centers.items() if category == (r + 1) % 3
            ]
            end_time = (r + 1) * measurements_per_round

            for h in relevant_hexes:
                record_targets = []
                for a, b in edges_around_hex:
                    q1 = torus(h + a, distance=distance)
                    q2 = torus(h + b, distance=distance)
                    edge_key = frozenset([q2i[q1], q2i[q2]])
                    # relative index of edge
                    relative_index = (
                        measurement_times[edge_key] - end_time
                    ) % measurements_per_cycle - measurements_per_cycle
                    record_targets.append(stim.target_rec(relative_index))
                    record_targets.append(
                        stim.target_rec(relative_index - measurements_per_cycle)
                    )

                circuit.append_operation(
                    "DETECTOR", record_targets, [h.real, h.imag, 0]
                )  # the 0 corresponds to the time coordinate
            # if just ran 0s, then before that 2s then enclosed the 1s
            circuit.append_operation(
                "SHIFT_COORDS", [], [0, 0, 1]
            )  # the 0 corresponds to the time coordinate
            round_circuits[r] += circuit
            # det_circuits.append(circuit)

    return round_circuits[0] + round_circuits[1] + round_circuits[2]


def generateHoneycomb(distance: int, rounds: int, noise: float) -> stim.Circuit:

    # step 1 = compute dictionary's and lists that say what all the points are, and edge types ...
    # need a coord system for centre of point - squared off

    # making a list of hex centers
    hex_centers: Dict[complex, int] = {}
    # look at unit square in diagram
    for row in range(3 * distance):
        for col in range(2 * distance):
            center = row * 2j + 2 * col - 1j * (col % 2)  # shifting the center when odd
            category = (-row - (col % 2)) % 3
            hex_centers[torus(center, distance=distance)] = category

    # next thing going to need is qubits as well as the types of edge data

    edge_types = [
        EdgeType(pauli="X", hex_to_hex_delta=2 - 3j, hex_to_qubit_delta=1 - 1j),
        EdgeType(pauli="Y", hex_to_hex_delta=2 + 3j, hex_to_qubit_delta=1 + 1j),
        EdgeType(pauli="Z", hex_to_hex_delta=4, hex_to_qubit_delta=1),
    ]

    qubit_coordinates: Set[complex] = set()
    for h in hex_centers:
        for edge_type in edge_types:
            for sign in [-1, +1]:
                q = h + edge_type.hex_to_qubit_delta * sign
                qubit_coordinates.add(torus(q, distance=distance))

    fused_dict = dict(hex_centers)
    for q in qubit_coordinates:
        fused_dict[q] = "q"
    # print_2d(fused_dict) # checking that hex_centers makes sense

    # need to index the qubits
    q2i: Dict[complex, int] = {
        q: i for i, q in enumerate(sorted_complex(qubit_coordinates))
    }

    # says what the edges would be that are the perimeter of a hex
    edges_around_hex: List[Tuple[complex, complex]] = [
        (-1 - 1j, +1 - 1j),
        (+1 - 1j, +1 - 0j),
        (+1 - 0j, +1 + 1j),
        (+1 + 1j, -1 + 1j),
        (-1 + 1j, -1 - 0j),
        (-1 - 0j, -1 - 1j),
    ]

    round_circuit_no_noise_no_detectors = generate_circuit_rounds_parameterized(
        noise=0,
        hex_centers=hex_centers,
        distance=distance,
        q2i=q2i,
        edge_types=edge_types,
        edges_around_hex=edges_around_hex,
        qubit_coordinates=qubit_coordinates,
        detectors=False,
    )
    round_circuit_no_noise_yes_detectors = generate_circuit_rounds_parameterized(
        noise=0,
        hex_centers=hex_centers,
        distance=distance,
        q2i=q2i,
        edge_types=edge_types,
        edges_around_hex=edges_around_hex,
        qubit_coordinates=qubit_coordinates,
        detectors=True,
    )
    round_circuit_yes_noise_yes_detectors = generate_circuit_rounds_parameterized(
        noise=noise,
        hex_centers=hex_centers,
        distance=distance,
        q2i=q2i,
        edge_types=edge_types,
        edges_around_hex=edges_around_hex,
        qubit_coordinates=qubit_coordinates,
        detectors=True,
    )

    # Quite important for a simulator to know 'where are the qubits' - eg are they laid out on a line?
    full_circuit = stim.Circuit()
    # adding coordinate locations
    for q, i in q2i.items():
        full_circuit.append_operation("QUBIT_COORDS", [i], [q.real, q.imag])

    """want to do an initialisation"""
    # intialize data qubit along logical observable column into correct basis for observable to be deterministic
    qubits_along_column = sorted(
        [q for q in qubit_coordinates if q.real == 1], key=lambda v: v.imag
    )
    # want to assign above bases XY space
    initial_bases_along_column = "ZY_ZX_" * distance

    x_initialised = [
        q2i[q]
        for q, b in zip(qubits_along_column, initial_bases_along_column)
        if b == "X"
    ]
    y_initialised = [
        q2i[q]
        for q, b in zip(qubits_along_column, initial_bases_along_column)
        if b == "Y"
    ]
    # default intialise to Z

    full_circuit.append_operation("H", x_initialised)
    full_circuit.append_operation("H_YZ", y_initialised)
    # H_YZ is a varient of the hadamard that rotates around YZ

    full_circuit += (
        round_circuit_no_noise_no_detectors * 2
        + round_circuit_no_noise_yes_detectors * 2
        + round_circuit_yes_noise_yes_detectors * rounds
        + round_circuit_no_noise_yes_detectors * 2
        + round_circuit_no_noise_no_detectors * 2
    )  # not sure where stabilises therefore conservatively large number

    # finish circuit with data measurements

    qubit_coords_to_measure = {
        q for q, b in zip(qubits_along_column, initial_bases_along_column) if b != "_"
    }
    qubit_indices_to_measure = [q2i[q] for q in qubit_coords_to_measure]
    order = {q: i for i, q in enumerate(qubit_coords_to_measure)}

    assert rounds % 2 == 0 # really mean cycles as if odd then logical observable not happy
    full_circuit.append_operation("H_YZ", y_initialised)
    full_circuit.append_operation("H", x_initialised)
    full_circuit.append_operation("M", qubit_indices_to_measure)

    full_circuit.append_operation(
        "OBSERVABLE_INCLUDE",
        [stim.target_rec(i - len(qubit_indices_to_measure)) for i in order.values()],
        0,
    )
    # print(full_circuit)
    return full_circuit

    # then need to figure out, what is the error correction meant to be working with, which measurement are meant to be compared in order to notice where errors are


# Craig's function on surface code to pymatching
def run_shots_correct_errors_return_num_correct(circuit: stim.Circuit, num_shots: int):
    """Collect statistics on how often logical errors occur when correcting using detections."""
    e = circuit.detector_error_model()
    m = detector_error_model_to_matching(e)

    t0 = time.monotonic()
    detector_samples = circuit.compile_detector_sampler().sample(
        num_shots, append_observables=True
    )
    t1 = time.monotonic()

    num_correct = 0
    for sample in detector_samples:
        actual_observable = sample[-1]
        detectors_only = sample.copy()
        detectors_only[-1] = 0
        predicted_observable = m.decode(detectors_only)[0]
        num_correct += actual_observable == predicted_observable
    t2 = time.monotonic()

    # decode_time = t2 - t1
    # sample_time = t1 - t0
    # print("decode", decode_time, "sample", sample_time)

    return num_correct


def detector_error_model_to_matching(
    model: stim.DetectorErrorModel,
) -> pymatching.Matching:
    """Convert stim error model into a pymatching graph."""
    det_offset = 0

    def _iter_model(
        m: stim.DetectorErrorModel,
        reps: int,
        callback: Callable[[float, List[int], List[int]], None],
    ):
        nonlocal det_offset
        for _ in range(reps):
            for instruction in m:
                if isinstance(instruction, stim.DemRepeatBlock):
                    _iter_model(
                        instruction.body_copy(), instruction.repeat_count, callback
                    )
                elif isinstance(instruction, stim.DemInstruction):
                    if instruction.type == "error":
                        dets = []
                        frames = []
                        for t in instruction.targets_copy():
                            v = str(t)
                            if v.startswith("D"):
                                dets.append(int(v[1:]) + det_offset)
                            elif v.startswith("L"):
                                frames.append(int(v[1:]))
                            else:
                                raise NotImplementedError()
                        p = instruction.args_copy()[0]
                        callback(p, dets, frames)
                    elif instruction.type == "shift_detectors":
                        det_offset += instruction.targets_copy()[0]
                    elif instruction.type == "detector":
                        pass
                    elif instruction.type == "logical_observable":
                        pass
                    else:
                        raise NotImplementedError()
                else:
                    raise NotImplementedError()

    g = nx.Graph()
    num_detectors = model.num_detectors
    for k in range(num_detectors):
        g.add_node(k)
    g.add_node(num_detectors, is_boundary=True)
    g.add_node(num_detectors + 1)
    for k in range(num_detectors + 1):
        g.add_edge(k, num_detectors + 1, weight=9999999999)

    def handle_error(p: float, dets: List[int], frame_changes: List[int]):
        if p == 0:
            return
        if len(dets) == 1:
            dets.append(num_detectors)
        if len(dets) != 2:
            return  # Just ignore correlated error mechanisms (e.g. Y errors / XX errors)
        g.add_edge(*dets, weight=-math.log(p), qubit_id=frame_changes)

    _iter_model(model, 1, handle_error)

    return pymatching.Matching(g)


# in order to test if code is correct then should look at how logical error varies with size
def compute_threshold(path, probabilities: List[float], distances: List[int], append: bool):
    with open(path, "a" if append else "w") as f:
        if not append:      
            print("distance,physical_error_rate,num_shots,num_correct", file=f)
        for d in distances:
            for p in probabilities:
                circuit = generateHoneycomb(distance=d, rounds=6, noise=p)
                num_shots = 10000
                num_correct = run_shots_correct_errors_return_num_correct(
                    num_shots=num_shots, circuit=circuit
                )
                logical_error_rate = (num_shots - num_correct) / num_shots
                print(f"{d},{p},{num_shots},{num_correct}", file=f)


@dataclass
class DistanceExperimentData:
    num_shots: int = 0
    num_correct: int = 0

    @property
    def logical_error_rate(self) -> float:
        return (self.num_shots - self.num_correct) / self.num_shots


# aim is draw physical error plots as distance changes


# writing code to plot and process the above csv file
def plot_data(path: str):
    # need a dict of distances to paires of probabilities
    # The key is the distance, 2nd key = physical error rate
    distance_to_noise_to_results: Dict[int, Dict[float, DistanceExperimentData]] = {}

    with open(path, "r") as f:
        for row in csv.DictReader(f):
            print(row)

            distance = int(row["distance"])
            physical_error_rate = float(row["physical_error_rate"])
            num_shots = int(row["num_shots"])
            num_correct = int(row["num_correct"])

            data = distance_to_noise_to_results \
                .setdefault(distance, {}) \
                .setdefault(physical_error_rate, DistanceExperimentData())

            data.num_shots = num_shots
            data.num_correct = num_correct

    for distance in sorted(distance_to_noise_to_results.keys()):
        group = distance_to_noise_to_results[distance]
        xs = []
        ys = []
        for physical_error_rate in sorted(group.keys()):
            xs.append(physical_error_rate)
            data = group[physical_error_rate]
            ys.append(-math.log10(data.logical_error_rate + 1e-11))
        plt.plot(xs, ys, label=f"d={distance}")

    plt.legend()
    plt.loglog()
    #plt.plot([0,1], [0.5,0.5],label="fully randomised")
    plt.show(block=True)


def main():
    #compute_threshold("data.csv", probabilities=[0.02,0.025,0.03,0.04,0.045],distances=[1,2,3,4],append=True)
    plot_data("data.csv")
    # to see if circuit makes sense look at circuit diagram
    # print(circuit)

    # samples = (circuit.compile_detector_sampler().sample(10))
    # for sample in samples:
    #    print("".join("_1"[e] for e in sample))

    # If the above is all _ then means that the detectors are working nicely

    # a stricter check would be to compute the error model
    # error_model = circuit.detector_error_model(decompose_errors=True)
    # print(error_model)


# adding in a main guard
if __name__ == "__main__":
    main()
