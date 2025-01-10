
# bit flip code = detects X errors
# phase-flip = detects error in Z
# format is [n,1,d], where n is the number of qubits, d i the distance = lower bound((n-1)/2)

#shall initially do the repetition code for d = 3
# then I shall code a function which can use parameters to make the repetition code

# plan is that i then use the repetition code to make shor's code
# and then bacon-shor

# M, MR = Z-basis measurements, where MR performs a reset afterwards
# detectors take 2 inputs,
import stim
import pymatching, numpy as np, matplotlib.pyplot as plt

#bit-flip for d = 2 #where the original data bit is on 1
repetition_bitflip = stim.Circuit('''
 R 0 1 2
 TICK
 DEPOLARIZE1(0.03) 0 2                             
 CX 0 1
 TICK                            
 CX 2 1 
 TICK                                
 X_ERROR(0.12) 0 1 2
 MR 1
 M 0 2

 DETECTOR(1,0) rec[-3]
 OBSERVABLE_INCLUDE(1) rec[-1]
 DETECTOR(1,1) rec[-1] rec[-2] rec[-3] 
 TICK
 
 ''')

repetition_phaseflip = stim.Circuit('''
 R 0 1 2
 TICK
 DEPOLARIZE1(0.03) 0 2                             
 CX 0 1
 TICK                            
 CX 2 1 
 TICK  
 H 0 1 2                              
 Z_ERROR(0.12) 0 1 2
 MXR 1
 MX 0 2

 DETECTOR(1,0) rec[-3]
 OBSERVABLE_INCLUDE(1) rec[-1]
 DETECTOR(1,1) rec[-1] rec[-2] rec[-3] 
 TICK
 
 ''')

print(repetition_phaseflip.diagram())


# Writing code that generates the above code
def generateRepetitionCode(distance: int, flip_error_prob: float, depolarization_error_prob: float):
    code = stim.Circuit()

    #calculating the total number of qubits
    num_qubits = 2*distance - 1

    for qubit in range(0, num_qubits):
        code.append_operation("R", [qubit])
    
    code.append_operation("TICK")

    #basically the odd qubits with be ..., and the even qubits will be ...
    for qubit in range(0,num_qubits,2):
        code.append_operation("DEPOLARIZE1", qubit, depolarization_error_prob)
    
    for qubit in range(0, num_qubits - 2,2):
        code.append_operation("CX", [qubit, qubit+1])
    
    code.append_operation("TICK")

    for qubit in range(2, num_qubits,2):
        code.append_operation("CX", [qubit, qubit-1])

    code.append_operation("TICK")

    #apply the x error
    for qubit in range(0, num_qubits):
        code.append_operation("X_ERROR", qubit, flip_error_prob)
    

    #measure the qubits
    for qubit in range(1, num_qubits, 2):
        code.append_operation("MR", qubit)
    
    #adding the detectors for odd
    for i in range((-distance) + 1, 0):
        code.append_operation("DETECTOR", [stim.target_rec(i)], [((distance - 1 + i)*2) + 1, 0])


    for qubit in range(0, num_qubits, 2):
        code.append_operation("M", qubit)

    for i in range((-distance) + 1, 0):
        code.append_operation("DETECTOR", [stim.target_rec(i), stim.target_rec(i-1), stim.target_rec(i-distance)], [(distance - 1 + i)*2 + 1, 1])

    code.append_operation("OBSERVABLE_INCLUDE", [stim.target_rec(-1)], 0)
    code.append_operation("TICK")
    return code

myCode = generateRepetitionCode(3,0.12,0.03)
print(repr(myCode))
#In order to make the graphs also need to make a detector model
DEM = myCode.detector_error_model(decompose_errors=True)
print(repr(DEM))

#Detector error model provides error model that will be used in decoder

#Decoders take in error models and syndromes, and return prediction
decoder = pymatching.Matching.from_detector_error_model(DEM)

#Need a decoder sampler - this simulates out code circuit being run based on error model
#Sampler outputs: num. of detection events, num. of times detectores flagged an error, num. of time logical observable flipped

detector_sampler = myCode.compile_detector_sampler()
detection_events, observable_flips = detector_sampler.sample(
    1, separate_observables=True
)

predictions = decoder.decode_batch(detection_events)

#output of decoder is then compared to output of observables, want to agree
logical_errors = (
    sum(
        bool(pred) != obs_flip #when disagree
        for pred, obs_flip  #for each guess
        in zip(predictions,observable_flips)
    )
)

#aim of code is not comparing different decoders on our error code

#will then then experiment how performs with different levels of noise
MAX_NOISE_ALLOWED = 3/4
noise_levels = np.linspace(0, MAX_NOISE_ALLOWED, 20)

#function for testing that we will call at different noise levels
def benchmark_decoder(depolarisation_error_prob: float = 0, flip_error_prob: float = 0, num_shots: int = 10000):
    circuit = generateRepetitionCode(2, flip_error_prob, depolarisation_error_prob)
    DEM = circuit.detector_error_model(decompose_errors=True)
    decoder = pymatching.Matching.from_detector_error_model(DEM)  # create a decoder
    detector_sampler = circuit.compile_detector_sampler()
    detection_events, observable_flips = detector_sampler.sample(num_shots, separate_observables=True) # generate samples
    predictions = decoder.decode_batch(detection_events) #use decoder on samples
    logical_errors = (
        sum(
            bool(pred) != obs_flip #when disagree
            for pred, obs_flip  #for each guess
            in zip(predictions,observable_flips)
        )
    )
    percentage_failure = (logical_errors[0] / num_shots ) *100
    return percentage_failure

testing_depolarisation = [
    benchmark_decoder(depolarisation_error_prob=p) for p in noise_levels
]
testing_flipping = [
    benchmark_decoder(flip_error_prob=p) for p in noise_levels
]

plt.plot(noise_levels,testing_depolarisation, label='Depolarisation')
plt.plot(noise_levels,testing_flipping,label='Flip')
plt.title("Performance of standard decoder with quantum repetition code")
plt.xlabel("Noise level")
plt.ylabel("Percentage of failed decodings")
plt.ylim(0,100)
plt.axhline(y=50, color='black', linestyle = '--')
plt.legend()
plt.show()

#pre-written function
code = stim.Circuit.generated(
    "repetition_code:memory",
    rounds = 1,
    distance = 3,
    before_measure_flip_probability=0.12,
    before_round_data_depolarization=0.03,
)
DEM = code.detector_error_model(decompose_errors=True)

print(repr(DEM))


