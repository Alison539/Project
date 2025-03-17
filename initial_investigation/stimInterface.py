"""
The aim is to learn about the interface between stim and pymatching
"""

"""
This was copied from stimSetup
"""
# decoders consume detector error model format
# some decoders need a weighted graph, use glue code to convert stim.DetectorErrorModel into a graph expected by a decoder
# pymatching is a package i can use instead of writing glue code
import pymatching
import stim
import numpy as np

# will sample a circuit using stim
# will decode the circuit using pymatching + count when gets answer right


def count_logical_errors(circuit: stim.Circuit, num_shots: int) -> int:
    # print(circuit)
    # Sample the circuit.

    # want to sample detection events (symptoms) and observable flips
    # create a sampler with circuit.compile_detector_sampler()
    # call sampler.sample(shots, separate_observables=True)
    # the argument means that retruned = a tuple, first = detection event data (to give to decoder), second = flip data decoder should predict
    sampler = circuit.compile_detector_sampler()
    # This is basically a regular stim circuit

    detection_events, observable_flips = sampler.sample(
        num_shots, separate_observables=True
    )
    # print(detection_events)
    # print(observable_flips)

    # Configure a decoder using the circuit.
    # extract decoder info with stim.Circuit.detector_error_model(...)
    # create decoder pymatching.Matching.from_detector_error_model

    detector_error_model = circuit.detector_error_model(decompose_errors=False)
    # print(detector_error_model)
    # with open("detector_error_model2.txt", "w") as file:
    #    detector_error_model.to_file(file)
    matcher = pymatching.Matching.from_detector_error_model(detector_error_model)

    # Run the decoder.
    # get predicted observable flips matching.predict
    predictions = matcher.decode_batch(detection_events)

    # Count the mistakes.
    # compare predictions with actual observable flip data (call this a logical error)
    num_errors = 0
    for shot in range(num_shots):
        actual_for_shot = observable_flips[shot]
        predicted_for_shot = predictions[shot]
        if not np.array_equal(actual_for_shot, predicted_for_shot):
            num_errors += 1
    return num_errors


testing_circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_z",
    rounds=40,
    distance=2,
)

testing_circuit_repetition = stim.Circuit.generated(
    "surface_code:rotated_memory_z",
    rounds=1,
    distance=3,
    after_clifford_depolarization=0.01,
    after_reset_flip_probability=0.01,
    before_measure_flip_probability=0.01,
    before_round_data_depolarization=0.01,
)

print(count_logical_errors(testing_circuit_repetition, 100000))
