#shor [[9,1,3]] code
#this code is based off a circuit diagram - however there are also alternative visual representations
import stim
def generateShorCode(flip_error_prob: float, depolarization_error_prob: float):
    #fixing distance 
    num_qubits = 9
    code = stim.Circuit()

    #Doing the set-up
    for qubit in range(0,num_qubits):
        code.append("R", [qubit])

    #This code is making the phase flip on the 0,3,6 bits
    for qubit in range(3, num_qubits, 3):
        code.append("CX", [0, qubit])

    for qubit in range(0, num_qubits,3):
        code.append("H",[qubit])

    #This code is making the bit flip repetition code on each triplet of bits
    for qubit in range(0, num_qubits, 3):
        code.append("CX", [qubit, qubit+1])
        code.append("CX", [qubit, qubit+2])

    #Adding in an Error 
    code.append("Y_ERROR", [0], 0.5)
    
    #measure if phaseflip wrong
    code.append("MPP",[stim.target_x(0), stim.target_combiner(),
                       stim.target_x(1), stim.target_combiner(),
                       stim.target_x(2), stim.target_combiner(),
                       stim.target_x(3), stim.target_combiner(),
                       stim.target_x(4), stim.target_combiner(),
                       stim.target_x(5)                       ])
    code.append("MPP",[stim.target_x(0), stim.target_combiner(),
                       stim.target_x(1), stim.target_combiner(),
                       stim.target_x(2), stim.target_combiner(),
                       stim.target_x(6), stim.target_combiner(),
                       stim.target_x(7), stim.target_combiner(),
                       stim.target_x(8)                     ])
    
    #measure if bitflips have gone wrong
    code.append("MPP",[stim.target_z(0), stim.target_combiner(),
                       stim.target_z(1)])
    code.append("MPP",[stim.target_z(3), stim.target_combiner(),
                       stim.target_z(4)])
    code.append("MPP",[stim.target_z(6), stim.target_combiner(),
                       stim.target_z(7)])

    code.append("MPP",[stim.target_z(0), stim.target_combiner(),
                       stim.target_z(2)])
    code.append("MPP",[stim.target_z(3), stim.target_combiner(),
                       stim.target_z(5)])
    code.append("MPP",[stim.target_z(6), stim.target_combiner(),
                       stim.target_z(8)])


    for i in range(8, 0,-1):
        code.append("DETECTOR",[stim.target_rec(-i)])
    
    #not sure if should do MPP or Ms?
    """
    #measure the qubits
    for qubit in range(num_qubits -1, -1, -1):
        code.append("M", qubit) #not sure if some of these should be MRs (measure and reset, potentially 0,3,6 should be MRs)

    #detect the phaseflip
    code.append("DETECTOR", [stim.target_rec(-1)])
    code.append("DETECTOR", [stim.target_rec(-1), stim.target_rec(-4), stim.target_rec(-7)])

    #detect the bitflips
    for i in range(1, num_qubits+1, 3):
        code.append("DETECTOR", [stim.target_rec(-i)])
        code.append("DETECTOR", [stim.target_rec(-i), stim.target_rec(-i-1), stim.target_rec(-i-2)])

    code.append("OBSERVABLE_INCLUDE", [stim.target_rec(-1)], 0)
    """
    return code
    
    
shorCode = generateShorCode(0,0)
print(shorCode.diagram())
shors = shorCode.compile_detector_sampler()
print(shors.sample(shots=10))

#Currently, if a singular error has occurred can detect eactly what type of error and on what bits.

