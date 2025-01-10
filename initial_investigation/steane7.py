import stim, numpy as np

#Steane 7 qubit code (aka [7,1,3])

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
#print(repr(pregen))

#decided to make for same model of error as above

#0-5 = the 6 generators

#Initial working = made using the picture of the error correcting circuit from Mermin's Chap 5
#however realised that basically have now made the generators, but don't understand what to do with the generators
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


#using steane 7 that found online
#Project into Steane's seven qubit code, up to sign:
#These are the qubits used to represent the logical qubit
# 0123456
# ___ZZZZ
# _ZZ__ZZ
# Z_Z_Z_Z
# ___XXXX
# _XX__XX
# X_X_X_X

#The MPP gates, give you +1 or -1 eigenvalues of those (which can be used to figure out where the error ocurred)

#basically did the generators
#v.impo detector just gets the result of the last measurement that occurred
original_circuit_1 = ("""
MPP Z3*Z4*Z5*Z7
MPP Z1*Z2*Z5*Z6
MPP Z0*Z2*Z4*Z6
MPP X3*X4*X5*X6
MPP X1*X2*X5*X6
MPP X0*X2*X4*X6
""")

original_circuit_2 = ("""
REPEAT 1{
    MPP Z3*Z4*Z5*Z6
    MPP Z1*Z2*Z5*Z6
    MPP Z0*Z2*Z4*Z6
    MPP X3*X4*X5*X6
    MPP X1*X2*X5*X6
    MPP X0*X2*X4*X6

    DETECTOR rec[-6] rec[-12] 
    DETECTOR rec[-5] rec[-11] 
    DETECTOR rec[-4] rec[-10] 
    DETECTOR rec[-3] rec[-9] 
    DETECTOR rec[-2] rec[-8] 
    DETECTOR rec[-1] rec[-7] 
                           
}
                          """)

noErrors = stim.Circuit(original_circuit_1 + original_circuit_2)
# Z stabilizers were already satisfied by starting in |0000000>
sampler = noErrors.compile_detector_sampler()
#This returns all false (which means that eigenvalues all +1 therefore identity no changes)
print(sampler.sample(shots=1))
print(np.sum(sampler.sample(shots=1)))

#the purpose of steane 7 is that can detect (and the correct afterwards) any singular XYZ errors that occur on the data qubits
#testing my steane code
xError = stim.Circuit(original_circuit_1 + "X_ERROR(1) 4 \n" + original_circuit_2)
sampler = xError.compile_detector_sampler()
#Sampler should return [ True False  True False False False] //the True is where Z4 appears in the generator (since X4 anticommutes with Z4) and it does
print(sampler.sample(shots=1))

yError = stim.Circuit(original_circuit_1 + "Y_ERROR(1) 2 \n" + original_circuit_2)
sampler = yError.compile_detector_sampler()
#Sampler should return [False True True False True True]
print(sampler.sample(shots=1))