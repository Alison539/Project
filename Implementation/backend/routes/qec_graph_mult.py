from typing import List, Dict, Tuple

import matplotlib.pyplot
import stim
import matplotlib

matplotlib.use("agg")
import sinter
import os
import scipy.stats
import numpy as np

from .generate_stim_mult import generate_stim_given_processed_input, process_input
from .union_find_decoder import count_logical_errors


def calculate_threshold(fits, lowest_noise, highest_noise, num_distances):
    if len(fits) < 2:
        return None
    else:
        matrixA = np.ones((num_distances, 2))
        for i in range(0, num_distances):
            matrixA[i][0] = -fits[i].slope
        b = [fits[i].intercept for i in range(0, num_distances)]

        try:
            threshold, _, _, _ = np.linalg.lstsq(matrixA, b, rcond=None)
        except np.linalg.LinAlgError:
            return None
        print(threshold)
        if lowest_noise < threshold[0] < highest_noise:
            return threshold[0]
        else:
            return None


def use_surface_code_mult_uf(surface_code_circuits, noises, distances, rounds):
    num_distances = len(distances)

    num_shots = 100000
    xs = []
    ys = []
    log_ys = []
    for i in range(0, num_distances):
        xs.append(noises)
        ys.append([])
        log_ys.append([])
        r = rounds[i]
        for j, n in enumerate(noises):
            num_errors = count_logical_errors(
                surface_code_circuits[i][j], num_shots=num_shots
            )
            per_shot = num_errors / num_shots
            per_round = sinter.shot_error_rate_to_piece_error_rate(per_shot, pieces=r)
            ys[i].append(per_round)
            log_ys[i].append(np.log(per_round))

    return xs, ys, log_ys


def use_surface_code_mult_mwpm(surface_code_tasks, distances):
    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=int(os.cpu_count() or 0),
        tasks=surface_code_tasks,
        decoders=["pymatching"],
        max_shots=1_000_000,
        max_errors=100000,
        print_progress=False,
    )

    num_distances = len(distances)

    xs = [[] for _ in range(0, num_distances)]
    ys = [[] for _ in range(0, num_distances)]
    log_ys = [[] for _ in range(0, num_distances)]
    for stats in collected_surface_code_stats:
        n = stats.json_metadata["n"]
        i = stats.json_metadata["d_index"]
        r = stats.json_metadata["r"]
        per_shot = stats.errors / stats.shots
        per_round = sinter.shot_error_rate_to_piece_error_rate(per_shot, pieces=r)
        xs[i].append(n)
        ys[i].append(per_round)
        log_ys[i].append(np.log(per_round))

    return xs, ys, log_ys


def plot_graph(xs, ys, log_ys, distances, noises, step, name, graph_file):

    num_distances = len(distances)

    if num_distances > 1:
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "custom", ["#FFA500", "#8B0000"], N=num_distances
        )
        colours = [cmap(i / (num_distances - 1)) for i in range(num_distances)]
    else:
        colours = ["#8B0000"]

    fit = []
    for i in range(num_distances):
        fit.append(scipy.stats.linregress(xs[i], log_ys[i]))

    fig, ax = matplotlib.pyplot.subplots(1, 1)

    for i in range(num_distances):
        if num_distances == 1:
            newLabel = "Least Squares Line Fit"
        else:
            newLabel = "Distance = " + str(distances[i][0])
        ax.scatter(xs[i], ys[i], marker="x", color=colours[i])
        ax.plot(
            [noises[0], noises[-1]],
            [
                np.exp(fit[i].intercept + fit[i].slope * noises[0]),
                np.exp(fit[i].intercept + fit[i].slope * noises[-1]),
            ],
            linestyle="--",
            label=newLabel,
            color=colours[i],
        )

    ax.set_xlim(max(noises[0] - step, 0), noises[-1] + step)
    ax.set_title(name)
    ax.set_xlabel("Physical Error Rate")
    ax.set_ylabel("Logical Error Rate")
    ax.grid(which="major")
    ax.grid(which="minor")
    ax.legend()
    fig.savefig(graph_file, bbox_inches="tight")

    threshold = calculate_threshold(
        fits=fit,
        lowest_noise=noises[0],
        highest_noise=noises[-1],
        num_distances=num_distances,
    )
    return threshold


def generate_qec_graph_mult(
    coord_sys: int,
    qubit_operations: List[Dict],
    two_qubit_operations: List[List[List[int]]],
    noiseRange: List[float],
    noiseModel: List[float],
    step: float,
    ratio: float,
    num_cycles: int,
    distances: List[List],
    name: str,
    basis: int,
    decoder: int,
):
    distances = sorted(distances)

    noises = []
    noise = noiseRange[0]
    while noise <= noiseRange[1]:
        noises.append(noise)
        noise += step

    surface_code_tasks = []
    surface_code_circuits = []
    distances_used = []
    rounds = []
    for index, distance in enumerate(distances):
        distances_used.append(distance[0])

        processed_input = process_input(
            qubit_operations=qubit_operations,
            two_qubit_operations=two_qubit_operations,
            qubits_involved=distance[1],
        )

        if distance[0] == 0:
            num_rounds = num_cycles
        else:
            num_rounds = int(distance[0] * ratio)

        new_surface_code_tasks = []
        new_surface_code_circuits = []
        rounds.append(num_rounds)
        for n in noises:
            circuit = generate_stim_given_processed_input(
                coord_sys=coord_sys,
                qubit_operations=qubit_operations,
                two_qubit_operations=two_qubit_operations,
                noise=[n * noiseModel[i] for i in range(0, 5)],
                num_cycles=num_rounds,
                basis=basis,
                preprocessed_input=processed_input,
            )
            newTask = sinter.Task(
                circuit=circuit,
                json_metadata={"n": n, "d_index": index, "r": num_rounds},
            )
            new_surface_code_tasks.append(newTask)
            new_surface_code_circuits.append(circuit)
        surface_code_circuits.append(new_surface_code_circuits)
        surface_code_tasks = surface_code_tasks + new_surface_code_tasks

    if decoder == 0:
        xs, ys, log_ys = use_surface_code_mult_mwpm(
            surface_code_tasks=surface_code_tasks, distances=distances
        )
    elif decoder == 1:
        xs, ys, log_ys = use_surface_code_mult_uf(
            surface_code_circuits=surface_code_circuits,
            noises=noises,
            distances=distances,
            rounds=rounds,
        )

    threshold = plot_graph(
        xs=xs,
        ys=ys,
        log_ys=log_ys,
        distances=distances,
        noises=noises,
        step=step,
        name=name,
        graph_file="graph.png",
    )

    return threshold


def test():
    step = 0.01
    noises = [0.1 + i * step for i in range(0, 8)]
    distances = [3, 5, 7, 9, 11, 13, 15, 17]

    actual_surface_code_tasks = [
        sinter.Task(
            circuit=stim.Circuit.generated(
                "repetition_code:memory",
                rounds=d,
                distance=d,
                after_clifford_depolarization=n,
                after_reset_flip_probability=n,
                before_measure_flip_probability=n,
                before_round_data_depolarization=n,
            ),
            json_metadata={"n": n, "d_index": i, "r": d},
        )
        for n in noises
        for i, d in enumerate(distances)
    ]
    correctly_formed_distaces = [(i, i) for i in distances]
    use_surface_code_mult_mwpm(
        surface_code_tasks=actual_surface_code_tasks,
        graph_file="actual_graph2.png",
        noises=noises,
        step=step,
        name="Using Stim Generated",
        distances=correctly_formed_distaces,
    )


if __name__ == "__main__":
    test()
