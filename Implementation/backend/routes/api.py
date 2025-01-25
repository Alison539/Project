from flask import Blueprint, jsonify, request
from contextlib import redirect_stdout
from .generate_stim import generate_stim

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/qec_data', methods=['POST'])
def qec_data():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid or missing data"}), 400
    
    coord_sys = data.get('coordSys')
    qubit_operations = data.get('qubitOperations',[])
    two_qubit_operations = data.get("twoQubitOperations",[])
    noise = data.get("noise",[])
    num_cycles = data.get("numCycles")
    basis = data.get("basis")
    name = data.get("name")

    toReturn = ""
    with open('new_circuit.txt', 'w') as f:
        circuit = generate_stim(coord_sys=coord_sys, qubit_operations=qubit_operations, two_qubit_operations=two_qubit_operations,noise=noise,num_cycles=num_cycles,name=name,basis=basis)
        with redirect_stdout(f):
            print(circuit)
    with open('new_circuit.txt', 'r') as f:
        toReturn = f.read()
    
    return jsonify({"stimcode": (toReturn) })