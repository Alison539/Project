import stim, numpy as np


#using steane 5 that found online
#Project into Steane's five qubit code, up to sign:
#These are the qubits used to represent the logical qubit
# 01234
# ZXXZ_
# XXZ_Z
# XZ_ZX
# Z_ZXX

#The MPP gates, give you +1 or -1 eigenvalues of those (which can be used to figure out where the error ocurred)

#basically did the generators
#v.impo detector just gets the result of the last measurement that occurred
original_circuit_1 = ("""

MPP Z0*X1*X2*Z3
MPP X0*X1*Z2*Z4
MPP X0*Z1*Z3*X4
MPP Z0*Z2*X3*X4
   
""")

original_circuit_2 = ("""
REPEAT 1{
    MPP Z0*X1*X2*Z3
    MPP X0*X1*Z2*Z4
    MPP X0*Z1*Z3*X4
    MPP Z0*Z2*X3*X4

    DETECTOR rec[-4] rec[-8] 
    DETECTOR rec[-3] rec[-7] 
    DETECTOR rec[-2] rec[-6] 
    DETECTOR rec[-1] rec[-5] 
                           
}
                          """)

noErrors = stim.Circuit(original_circuit_1 + original_circuit_2)
# Z stabilizers were already satisfied by starting in |0000000>
sampler = noErrors.compile_detector_sampler()
#This returns all false (which means that eigenvalues all +1 therefore identity no changes)
print(sampler.sample(shots=1))
print(np.sum(sampler.sample(shots=1)))

#the purpose of steane 5 is that can detect (and the correct afterwards) any singular XYZ errors that occur on the data qubits
#testing my steane code
xError = stim.Circuit(original_circuit_1 + "X_ERROR(1) 4 \n" + original_circuit_2)
sampler = xError.compile_detector_sampler()
#Sampler should return [  False True False False] //the True is where Z4 appears in the generator (since X4 anticommutes with Z4) and it does
print(sampler.sample(shots=1))

yError = stim.Circuit(original_circuit_1 + "Y_ERROR(1) 2 \n" + original_circuit_2)
sampler = yError.compile_detector_sampler()
#Sampler should return [ True True False True ]
print(sampler.sample(shots=1))