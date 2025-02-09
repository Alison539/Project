import stim, pymatching, sinter, matplotlib
import matplotlib.pyplot as plt
import sinter
from typing import List
import os
"""
#circuits are instances of the stim.Circuit class

#to create a new empty circuit
circuit = stim.Circuit() 

#to add operations to it: circuit.append(name_of_gate, list_of_targets)
# First, the circuit will initialize a Bell pair.
circuit.append("H", [0])
circuit.append("CNOT", [0, 1])

circuit.append("M", [0,1])

#representation of stim's circuit file syntax
print(repr(circuit))

#an annotated text diagram of the circuit
print(circuit.diagram())

#other types of diagrams exist - for example can specify timeline-svg - returns a scalable vector graphics picture
#print(circuit.diagram('timeline-svg'))

#can sample from the circuit by using the circuit.compile_sampler() method to get a sampler object, and then calling sample on that object.
sampler = circuit.compile_sampler()
print(sampler.sample(shots=10))

#stim circuits can include error correction annotations
#DETECTOR annotation will take two targets: the two measurements whose parity you are asserting should be consistent from run to run.
#point at the measurements using stim.target_rec method (short for targect measurement record)
#most recent measurement is stim.target_rec(-1), 2nd most recent -2, ...

#to indicate that the 2 previous measurements should be consistent
circuit.append("DETECTOR", [stim.target_rec(-1), stim.target_rec(-2)])
print(repr(circuit))
#detectors only assert parity under noiseless execution
#if want to annotate that a pair of measurements is always different use the same

#instead of sampling measurements can sample from detectors
detectorSampler = circuit.compile_detector_sampler()
print(detectorSampler.sample(shots=5))
#currently since there is no noise, all falses -> no detection events occurred
"""

#time to add some noise - can do DEPOLRAIZE1, Z_ERROR, X_ERROR
#probabilistically applies error to target, with each target independent
#the TICK indicates the progression of time
noisyCircuit = stim.Circuit("""
    H 0
    TICK

    CX 0 1
    X_ERROR(0.2) 0 1
    TICK

    M 0 1
    DETECTOR rec[-1] rec[-2]                      
""")
"""

#Can create a visual representation for the different times
noisyCircuit.diagram('timeslice-svg')

noisySampler = noisyCircuit.compile_detector_sampler()
print(noisySampler.sample(shots=10))
#now there is noise -> mix of falses and trues

#detector fraction = how often detectors fire on average
import numpy as np
print(np.sum(noisySampler.sample(shots = 10**6)) / 10**6)
#detector fires if both not the same ie both didnt get error so 0.8x0.2x2

#generating error correction circuits
#can use pregenerated code circuits
#by using different parameters can recreate different noise models
errorCircuit = stim.Circuit.generated(
    "repetition_code:memory",
    #how many times the stabilizers are measured
    rounds=25,
    #size fo the error code
    distance=9,
    #depoloarization will occur at each round on each data qubit with this prob
    before_round_data_depolarization=0.04,
    #means an x-error occurs with this probability each measurement operation
    before_measure_flip_probability=0.01)
    # ^^ is the phenomenological noise model

print(repr(errorCircuit))
errorCircuit.diagram('timeline-svg')


sampler = errorCircuit.compile_sampler()
one_sample = sampler.sample(shots=1)[0]
for k in range(0, len(one_sample), 8):
    timeslice = one_sample[k:k+8]
    print("".join("1" if e else "_" for e in timeslice))
#the 1s appear in streaks, this is because once an error occurs remains that way

detector_sampler = errorCircuit.compile_detector_sampler()
one_sample = detector_sampler.sample(shots=1)[0]
for k in range(0, len(one_sample), 8):
    timeslice = one_sample[k:k+8]
    print("".join("!" if e else "_" for e in timeslice))
#the ! are when actual errors occurred, come in pairs
#each ! mush be paired with either a ! or a boundary -> can perform error correction
#in a circuit generated by stim, logical observable = leftmost data qubit
#that is flipped for each ! paired with left boundary


#stim can make a circuit into a detector error model (a list of the independent error mechanisms in a circuit + symptoms (which detectors they set off) + frame changes (logical observables flipped))
dem = errorCircuit.detector_error_model()
print(repr(dem))
dem.diagram("matchgraph-svg")
#this creates a diagram of what we see with the surface error code, node = detector, edge = error mechanism
#when finding out errors occurred will try and minimise the number of edges between 2 errors
#looks good if specify coordinate data for its detectors
#decoders consume detector error model format
#some decoders need a weighted graph, use glue code to convert stim.DetectorErrorModel into a graph expected by a decoder

#pymatching is a package i can use instead of writing glue code
import pymatching

#will sample a circuit using stim
#will decode the circuit using pymatching + count when gets answer right


def count_logical_errors(circuit: stim.Circuit, num_shots: int) -> int:
    # Sample the circuit.

    #want to sample detection events (symptoms) and observable flips
        #create a sampler with circuit.compile_detector_sampler()
        #call sampler.sample(shots, separate_observables=True)
            #the argument means that retruned = a tuple, first = detection event data (to give to decoder), second = flip data decoder should predict
    sampler = circuit.compile_detector_sampler()
    detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

    # Configure a decoder using the circuit.
    #extract decoder info with stim.Circuit.detector_error_model(...)
    #create decoder pymatching.Matching.from_detector_error_model

    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(detector_error_model)

    # Run the decoder.
    #get predicted observable flips matching.predict
    predictions = matcher.decode_batch(detection_events)

    # Count the mistakes.
    #compare predictions with actual observable flip data (call this a logical error)
    num_errors = 0
    for shot in range(num_shots):
        actual_for_shot = observable_flips[shot]
        predicted_for_shot = predictions[shot]
        if not np.array_equal(actual_for_shot, predicted_for_shot):
            num_errors += 1
    return num_errors

#example with the repetition code circuit
circuit = stim.Circuit.generated("repetition_code:memory", rounds=100, distance=9, before_round_data_depolarization=0.03)
num_shots = 100_000
num_logical_errors = count_logical_errors(circuit, num_shots)
print("there were", num_logical_errors, "wrong predictions (logical errors) out of", num_shots, "shots")
#with increasing noise strength get more wrong predictions



#estimating the threshold = trying different physical error rates and code distances
#plot logical error rate vs physical error rate for each code distance and see where the curves cross
#typically increasing the distance should make logical error rate better, once past threshold that is where logical error rate gets worse



num_shots = 10_000
for d in [3, 5, 7]:
    xs = []
    ys = []
    for noise in [0.1, 0.2, 0.3, 0.4, 0.5]:
        circuit = stim.Circuit.generated(
            "repetition_code:memory",
            rounds=d * 3,
            distance=d,
            before_round_data_depolarization=noise)
        num_errors_sampled = count_logical_errors(circuit, num_shots)
        xs.append(noise)
        ys.append(num_errors_sampled / num_shots)
    plt.plot(xs, ys, label="d=" + str(d))
plt.loglog()
plt.xlabel("physical error rate")
plt.ylabel("logical error rate per shot")
plt.legend()
plt.show()



#sinter streamlines the monte carlo sampling process (so that dont need to write above code)


#wrap circuit into sinter.Task instances, and give those to sinter.collect - can specify whata data to collect with options
#sinter will then do montecarlo sampling

tasks = [
    sinter.Task(
        circuit=stim.Circuit.generated(
            "repetition_code:memory",
            rounds=d * 3,
            distance=d,
            before_round_data_depolarization=noise,
        ),
        json_metadata={'d': d, 'p': noise},
    )
    for d in [3, 5, 7, 9]
    for noise in [0.05, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5]
]
if __name__ == '__main__':  
    collected_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=4,
        tasks=tasks,
        decoders=['pymatching'],
        max_shots=100_000,
        max_errors=500,
    )


    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_stats,
        x_func=lambda stats: stats.json_metadata['p'],
        group_func=lambda stats: stats.json_metadata['d'],
    )
    ax.set_ylim(1e-4, 1e-0)
    ax.set_xlim(5e-2, 5e-1)
    ax.loglog()
    ax.set_title("Repetition Code Error Rates (Phenomenological Noise)")
    ax.set_xlabel("Phyical Error Rate")
    ax.set_ylabel("Logical Error Rate per Shot")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(120)  # Show it bigger



#can use stim.Circuit.generated to make simple surface code circuits
surface_code_circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_z",
    rounds=9,
    distance=3,
    after_clifford_depolarization=0.001,
    after_reset_flip_probability=0.001,
    before_measure_flip_probability=0.001,
    before_round_data_depolarization=0.001)

#surface codes = 2d grid therefore more complex
surface_code_circuit.without_noise().diagram("timeslice-svg")

#can make a 3d diagram of a circuit
surface_code_circuit.without_noise().diagram("timeline-3d")


#detslice diagram shows how stabilizers change over time
surface_code_circuit.diagram("detslice-svg")
#overlays time slice and detslice diagrams
surface_code_circuit.without_noise().diagram(
    "detslice-with-ops-svg", 
    tick=range(0, 9),
)

import os

surface_code_tasks = [
    sinter.Task(
        circuit = stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=d * 3,
            distance=d,
            after_clifford_depolarization=noise,
            after_reset_flip_probability=noise,
            before_measure_flip_probability=noise,
            before_round_data_depolarization=noise,
        ),
        json_metadata={'d': d, 'r': d * 3, 'p': noise},
    )
    for d in [3, 5, 7]
    for noise in [0.008, 0.009, 0.01, 0.011, 0.012]
]

#Need to add the if __name__ == '__main__':   otherwise basically doing multiprocessing and if dont have then recursively makes more subprocesses
if __name__ == '__main__':   
    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=1,
        tasks=surface_code_tasks,
        decoders=['pymatching'],
        max_shots=1_000,
        max_errors=5_000,
        print_progress=True,
    )

    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_surface_code_stats,
        x_func=lambda stat: stat.json_metadata['p'],
        group_func=lambda stat: stat.json_metadata['d'],
        failure_units_per_shot_func=lambda stat: stat.json_metadata['r'], #r stands for rounds
        #failure_unites_per_shot_func plots per round error rates instead of per shot error rates
    )
    ax.set_ylim(5e-3, 5e-2)
    ax.set_xlim(0.008, 0.012)
    ax.loglog()
    ax.set_title("Surface Code Error Rates per Round under Circuit Noise")
    ax.set_xlabel("Phyical Error Rate")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(120)  # Show it bigger


noise = 1e-3

surface_code_tasks = [
    sinter.Task(
        circuit= stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=d * 3,
            distance= d,
            after_clifford_depolarization=noise,
            after_reset_flip_probability=noise,
            before_measure_flip_probability=noise,
            before_round_data_depolarization=noise,
        ),
        json_metadata={'d':d, 'r': d*3, 'p': noise},
    )
    for d in [3,5,7,9]
]

if __name__ == '__main__': 
    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=os.cpu_count(),
        tasks=surface_code_tasks,
        decoders=['pymatching'],
        max_shots=1_000_000,
        max_errors=100,
        print_progress=True,
    )

    import scipy.stats
    import numpy as np

    #using linear regression to get a line fit of code distance versus log error rate

    # Compute the line fit.
    xs = []
    ys = []
    log_ys = []
    for stats in collected_surface_code_stats:
        d = stats.json_metadata['d']
        if not stats.errors:
            print(f"Didn't see any errors for d={d}")
            continue
        per_shot = stats.errors / stats.shots
        per_round = sinter.shot_error_rate_to_piece_error_rate(per_shot, pieces=stats.json_metadata['r'])
        xs.append(d)
        ys.append(per_round)
        log_ys.append(np.log(per_round))
    fit = scipy.stats.linregress(xs, log_ys)
    print(fit)

    #plotting collected points and line fit, to be able to project the distance needed to get per round error rate at 0.0001%
    fig, ax = plt.subplots(1, 1)
    ax.scatter(xs, ys, label=f"sampled logical error rate at p={noise}")
    ax.plot([0, 25],
            [np.exp(fit.intercept), np.exp(fit.intercept + fit.slope * 25)],
            linestyle='--',
            label='least squares line fit')
    ax.set_ylim(1e-12, 1e-0)
    ax.set_xlim(0, 25)
    ax.semilogy()
    ax.set_title("Projecting distance needed to survive a trillion rounds")
    ax.set_xlabel("Code Distance")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()

"""

circuit = stim.Circuit.generated("surface_code:rotated_memory_x", distance=3, rounds=3, after_clifford_depolarization=0.01, before_measure_flip_probability=0.02, before_round_data_depolarization=0.03, after_reset_flip_probability=0.04)
print(circuit)
