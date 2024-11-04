import stim

pregen = stim.Circuit.generated(
    "repetition_code:memory",
    #how many times the stabilizers are measured
    rounds=25,
    #size fo the error code
    distance=7,
    #depoloarization will occur at each round on each data qubit with this prob
    before_round_data_depolarization=0.04,
    #means an x-error occurs with this probability each measurement operation
    before_measure_flip_probability=0.01)
print(repr(pregen))

#decided to make for same model of error as above

circuit = stim.Circuit("""
    R 0 1 2 3 4 5 6 7 8 9 10 11 12    
    H 0 1 2 3 4 5
    TICK
    CZ 5 6 5 7 5 8 5 12
    TICK
    CZ 4 6 4 7 4 9 4 11
    TICK
    CZ 3 6 3 8 3 9 3 10
    TICK
    CX 2 6 2 7 2 8 2 12
    TICK
    CX 1 6 1 7 1 9 1 11
    TICK
    CX 0 6 0 8 0 9 0 10
    TICK
    H 0 1 2 3 4 5
    TICK
    M 0 1 2 3 4 5
    DETECTOR rec[-1]
    DETECTOR rec[-2]
    DETECTOR rec[-3]
    DETECTOR rec[-4] 
    DETECTOR rec[-5] 
    DETECTOR rec[-6]

    REPEAT 2 {
        R 0 1 2 3 4 5 6 7 8 9 10 11 12    
        H 0 1 2 3 4 5
        TICK
        CZ 5 6 5 7 5 8 5 12
        TICK
        CZ 4 6 4 7 4 9 4 11
        TICK
        CZ 3 6 3 8 3 9 3 10
        TICK
        CX 2 6 2 7 2 8 2 12
        TICK
        CX 1 6 1 7 1 9 1 11
        TICK
        CX 0 6 0 8 0 9 0 10
        TICK
        H 0 1 2 3 4 5
        TICK
        M 0 1 2 3 4 5

            DETECTOR rec[-1] rec[-7] 
            DETECTOR rec[-2] rec[-8] 
            DETECTOR rec[-3] rec[-9] 
            DETECTOR rec[-4] rec[-10] 
            DETECTOR rec[-5] rec[-11] 
            DETECTOR rec[-6] rec[-12]     
        }           
""")

#adding a sampler
sampler = circuit.compile_detector_sampler()
print(sampler.sample(shots=5))