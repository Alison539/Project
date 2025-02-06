from flask import Blueprint, jsonify, request, send_file, make_response
from contextlib import redirect_stdout
from .generate_stim import generate_stim
from .qec_graph_mult import generate_qec_graph_mult
from .verify_input import (
    validate_dict,
    verify_noise_range,
    verify_basis,
    verify_coord_sys,
    verify_name,
    verify_noise,
    verify_num_cycles,
    verify_qubits,
    verify_step,
    verify_ratio,
    verify_distances,
)
import os

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/qec_data", methods=["POST"])
def qec_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing data"}), 400

    if not validate_dict(
        data,
        [
            "coordSys",
            "qubitOperations",
            "twoQubitOperations",
            "noise",
            "numCycles",
            "basis",
            "name",
        ],
    ):
        return jsonify({"error": "Invalid or missing data"}), 400
    coord_sys = data.get("coordSys")
    if not verify_coord_sys(coord_sys):
        return jsonify({"error": "Invalid coordinate system"}), 400
    qubit_operations = data.get("qubitOperations", [])
    two_qubit_operations = data.get("twoQubitOperations", [])
    if not verify_qubits(qubit_operations, two_qubit_operations):
        return jsonify({"error": "Invalid qubit operation data"}), 400

    noise = data.get("noise", [])
    if not verify_noise(noise):
        return jsonify({"error": "Invalid noise values"}), 400

    num_cycles = data.get("numCycles")
    if not verify_num_cycles(num_cycles):
        return jsonify({"error": "Invalid number of cycles"}), 400
    basis = data.get("basis")
    if not verify_basis(basis):
        return jsonify({"error": "Invalid basis"}), 400
    name = data.get("name")
    if not verify_name(name):
        return jsonify({"error": "Invalid name"}), 400
    toReturn = ""
    # try:
    circuit = generate_stim(
        coord_sys=coord_sys,
        qubit_operations=qubit_operations,
        two_qubit_operations=two_qubit_operations,
        noise=noise,
        num_cycles=num_cycles,
        name=name,
        basis=basis,
    )
    with open("new_circuit.txt", "w") as f:
        with redirect_stdout(f):
            print(circuit)
    with open("new_circuit.txt", "r") as f:
        toReturn = f.read()
    # except:
    #    return jsonify({"error": "Error occurred when generating Stim Code"}), 400

    return jsonify({"stimcode": (toReturn)})


@api_blueprint.route("/generate_graph", methods=["POST"])
def generate_graph():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid or missing data"}), 400
    if not validate_dict(
        data,
        [
            "coordSys",
            "qubitOperations",
            "twoQubitOperations",
            "noiseRange",
            "step",
            "numCycles",
            "ratio",
            "basis",
            "name",
            "distances",
        ],
    ):
        return jsonify({"error": "Invalid or missing data"}), 400

    coord_sys = data.get("coordSys")
    if not verify_coord_sys(coord_sys):
        return jsonify({"error": "Invalid coordinate system"}), 400

    qubit_operations = data.get("qubitOperations", [])
    two_qubit_operations = data.get("twoQubitOperations", [])
    if not verify_qubits(qubit_operations, two_qubit_operations):
        return jsonify({"error": "Invalid qubit operation data"}), 400

    noiseRange = data.get("noiseRange", [])
    if not verify_noise_range(noiseRange):
        return jsonify({"error": "Invalid noise range"}), 400

    step = data.get("step")
    if not verify_step(step):
        return jsonify({"error": "Invalid step"}), 400

    num_cycles = data.get("numCycles")
    if not verify_num_cycles(num_cycles):
        return jsonify({"error": "Invalid number of cycles"}), 400

    basis = data.get("basis")
    if not verify_basis(basis):
        return jsonify({"error": "Invalid basis"}), 400

    name = data.get("name")
    if not verify_name(name):
        return jsonify({"error": "Invalid name"}), 400

    distances = data.get("distances")
    if not verify_distances(distances, qubit_operations):
        return jsonify({"error": "Invalid distance sets"}), 400

    ratio = data.get("ratio")
    if not verify_ratio(ratio):
        return jsonify({"error": "Invalid ratio"}), 400

    generate_qec_graph_mult(
        coord_sys=coord_sys,
        qubit_operations=qubit_operations,
        two_qubit_operations=two_qubit_operations,
        noiseRange=noiseRange,
        step=step,
        num_cycles=num_cycles,
        ratio=ratio,
        distances=distances,
        name=name,
        basis=basis,
    )
    return {"url": "http://localhost:5000/api/get-graph"}


@api_blueprint.route("/get-graph", methods=["GET"])
def get_graph():
    filepath = os.path.join(os.getcwd(), "graph.png")
    response = make_response(send_file(filepath, mimetype="image/png"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
