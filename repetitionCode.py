
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
 DETECTOR(1,1) rec[-1] rec[-1] rec[-3] 
 TICK
 
 ''')

# Writing code that generates the above code
def generateRepetitionCode(distance: int, flip_error_prob: float, depolarization_error_prob: float):
    code = stim.Circuit()

    #calculating the total number of qubits
    num_qubits = 2*distance - 1

    for qubit in range(0, num_qubits):
        code.append("R", [qubit])
    
    code.append("TICK")

    #basically the odd qubits with be ..., and the even qubits will be ...
    for qubit in range(0,num_qubits,2):
        code.append("DEPOLARIZE1", qubit, depolarization_error_prob)
    
    for qubit in range(0, num_qubits - 2,2):
        code.append("CX", [qubit, qubit+1])
    
    code.append("TICK")

    for qubit in range(2, num_qubits,2):
        code.append("CX", [qubit, qubit-1])

    code.append("TICK")

    #apply the x error
    for qubit in range(0, num_qubits):
        code.append("X_ERROR", qubit, flip_error_prob)
    

    #measure the qubits
    for qubit in range(1, num_qubits, 2):
        code.append("MR", qubit)
    
    #adding the detectors for odd
    for i in range(-distance, 0):
        code.append("DETECTOR", [stim.target_rec(i)], [((distance + i)*2) + 1, 0])


    for qubit in range(0, num_qubits, 2):
        code.append("M", qubit)

    for i in range((-distance) + 1, 0):
        code.append("DETECTOR", [stim.target_rec(i), stim.target_rec(i-1), stim.target_rec(i-distance)], [(distance + i)*2 + 1, 1])

    code.append("OBSERVABLE_INCLUDE", [stim.target_rec(-1)], 0)

    return code

myCode = generateRepetitionCode(3,0.12,0.03)
print(repr(myCode))

#pre-written function
code = stim.Circuit.generated(
    "repetition_code:memory",
    rounds = 1,
    distance = 3,
    before_measure_flip_probability=0.12,
    before_round_data_depolarization=0.03,
)

print(repr(code))



