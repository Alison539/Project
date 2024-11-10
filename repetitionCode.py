#bit flip code = detects X errors
# phase-flip = detects error in Z
# format is [n,1,d], where n is the number of qubits, d i the distance = lower bound((n-1)/2)

#shall initially do the repetition code for d = 3
# then I shall code a function which can use parameters to make the repetition code

# plan is that i then use the repetition code to make shor's code
# and then bacon-shor

# M, MR = Z-basis measurements, where MR performs a reset afterwards
# detectors take 2 inputs,
import stim

#bit-flip for d = 3 #where the original data bit is on 1
repetition_bit-flip = stim.Circuit('''
 R 0 1 2
 CX 1 0 1 2
 MR 1
 M 0 2

 DETECTOR(1,0) rec[-3]
 DETECTOR(1,1) rec[-1] rec[-1] rec[-3] 

 OBSERVABLE_INCLUDE rec[-1]
 
 ''')



