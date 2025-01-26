from flask import Blueprint, jsonify, request, send_file, make_response
from contextlib import redirect_stdout
from .generate_stim import generate_stim
from .qec_graph import generate_qec_graph
import os

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
    try:
        circuit = generate_stim(coord_sys=coord_sys, qubit_operations=qubit_operations, two_qubit_operations=two_qubit_operations,noise=noise,num_cycles=num_cycles,name=name,basis=basis)
        with open('new_circuit.txt', 'w') as f:
            with redirect_stdout(f):
                print(circuit)
        with open('new_circuit.txt', 'r') as f:
            toReturn = f.read()
    except:
        toReturn = "An error occurred"
    
    return jsonify({"stimcode": (toReturn) })

@api_blueprint.route('/generate_graph', methods=['POST'])
def generate_graph():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid or missing data"}), 400
    
    coord_sys = data.get('coordSys')
    qubit_operations = data.get('qubitOperations',[])
    two_qubit_operations = data.get("twoQubitOperations",[])
    noiseRange = data.get("noiseRange",[])
    step = data.get("step")
    num_cycles = data.get("numCycles")
    basis = data.get("basis")
    name = data.get("name")

    generate_qec_graph(coord_sys, qubit_operations, two_qubit_operations, noiseRange, step, num_cycles, basis, name)
    return{"url": "http://localhost:5000/api/get-graph"}
    

@api_blueprint.route('/get-graph', methods=['GET'])
def get_graph():

    filepath = os.path.join(os.getcwd(), "graph.png")
    print(filepath)
    response = make_response(send_file(filepath, mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
    return send_file(filepath, mimetype='image/png', cache_timeout=0)
