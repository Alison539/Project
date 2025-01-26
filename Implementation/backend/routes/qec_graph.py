from typing import List, Dict
import matplotlib.pyplot
import stim
import matplotlib
matplotlib.use('agg')
import sinter
import os
import scipy.stats
import numpy as np
from .generate_stim import generate_stim


def use_surface_code(surface_code_tasks, graph_file, noises, step, name, rounds):
    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=int(os.cpu_count() or 0),
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
        n = stats.json_metadata["n"]
        per_shot = stats.errors / stats.shots
        per_round = sinter.shot_error_rate_to_piece_error_rate(
            per_shot, pieces=rounds
        )

        xs.append(n)
        ys.append(per_round)
        log_ys.append(np.log(per_round))

    fit = scipy.stats.linregress(xs, log_ys)

    fig, ax = matplotlib.pyplot.subplots(1, 1)
    ax.scatter(xs, ys, marker='x')
    ax.plot(
        [noises[0], noises[-1]],
        [
            np.exp(fit.intercept + fit.slope * noises[0]),
            np.exp(fit.intercept + fit.slope * noises[-1]),
        ],
        linestyle="--",
        label="least squares line fit",
    )
    ax.set_xlim(max(noises[0] - step, 0), noises[-1] + step)
    ax.semilogy()
    ax.set_title(name)
    ax.set_xlabel("Physical Error Rate")
    ax.set_ylabel("Logical Error Rate")
    ax.grid(which="major")
    ax.grid(which="minor")
    ax.legend()
    fig.savefig(graph_file,bbox_inches="tight")

def generate_qec_graph(
    coord_sys: int,
    qubit_operations: List[Dict],
    two_qubit_operations: List[List[List[int]]],
    noiseRange: List[float],
    step: float,
    num_cycles: int,
    name: str,
    basis: int,
):
    
    noises = []
    noise = noiseRange[0]
    while noise <= noiseRange[1]:
        noises.append(noise)
        noise += step

    my_surface_code_tasks = [
        sinter.Task(
            circuit=generate_stim(
                coord_sys=coord_sys,
                qubit_operations=qubit_operations,
                two_qubit_operations=two_qubit_operations,
                noise=[n, n, n, n, n],
                num_cycles=num_cycles,
                name=name,
                basis=basis,
            ),
            json_metadata={"n": n},
        )
        for n in noises
    ]

    
    use_surface_code(my_surface_code_tasks, "graph.png", noises, step, name, num_cycles)

    return ("graph.png")

def test():
    noises = [0.01,0.012,0.014,0.016,0.018]

    actual_surface_code_tasks = [
        sinter.Task(
            circuit= stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                rounds=9,
                distance= 3,
                after_clifford_depolarization=n,
                after_reset_flip_probability=n,
                before_measure_flip_probability=n,
                before_round_data_depolarization=n,
            ),
            json_metadata={'n': n},
        )
        for n in noises
    ]
    use_surface_code(actual_surface_code_tasks, "actual_graph.png", noises, 0.002, "Using Stim Generated", 9 )
