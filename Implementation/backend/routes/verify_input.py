from typing import List, Dict


def validate_dict(data: dict, required_fields: list) -> bool:
    return all(field in data and (data[field] is not None) for field in required_fields)


def verify_coord_sys(coord_sys: int):
    return isinstance(coord_sys, int) and coord_sys in {1, 2}


def verify_noise(noises: List[float]):
    if not (isinstance(noises, list) and len(noises) == 5):
        return False
    return all(
        (isinstance(noise, float) or isinstance(noise, int)) and 0 <= noise <= 1
        for noise in noises
    )


def verify_num_cycles(num_cycles: int):
    return isinstance(num_cycles, int) and 1 <= num_cycles <= 10000


def verify_ratio(ratio: float):
    return (isinstance(ratio, int) or isinstance(ratio, float)) and 1 <= ratio <= 10000


def verify_name(name: str):
    return isinstance(name, str)


def verify_basis(basis: int):
    return isinstance(basis, int) and basis in {0, 1, 2}


def verify_noise_range(noiseRange: List[float]):
    if not (isinstance(noiseRange, list) and len(noiseRange) == 2):
        return False
    if not all(
        (isinstance(noise, float) or isinstance(noise, int)) and 0 <= noise <= 1
        for noise in noiseRange
    ):
        return False
    return noiseRange[0] <= noiseRange[1]


def verify_step(step: float):
    return isinstance(step, float) and 0 < step < 1


def verify_qubits(
    qubit_operations: List[Dict], two_qubit_operations: List[List[List[int]]]
):
    if not isinstance(qubit_operations, list):
        return False
    num_qubits = len(qubit_operations)
    if num_qubits == 0:
        return False
    for qubit in qubit_operations:
        if not isinstance(qubit, dict):
            return False
        if not validate_dict(
            qubit, ["location", "logical_observable", "hadamard", "measurement", "id"]
        ):
            return False
        try:
            measurement = qubit.get("measurement")
            if not (isinstance(measurement, int) and measurement in {0, 1, 2, 3}):
                return False
            hadamard = qubit.get("hadamard")
            if not (isinstance(hadamard, int) and hadamard in {0, 1, 2}):
                return False
            logical_observable = qubit.get("logical_observable")
            if not isinstance(logical_observable, bool):
                return False
            if logical_observable and measurement != 0:
                return False
            location_dict = qubit.get("location")
            if not isinstance(location_dict, dict):
                return False
            if not validate_dict(location_dict, ["x", "y"]):
                return False
            x = location_dict.get("x")
            if not isinstance(x, int):
                return False
            y = location_dict.get("y")
            if not isinstance(y, int):
                return False
        except KeyError:
            return False

    if not (
        isinstance(two_qubit_operations, list)
        and len(two_qubit_operations) == num_qubits
    ):
        return False
    for targets in two_qubit_operations:
        if not (isinstance(targets, list) and len(targets) == num_qubits):
            return False
        for timesteps in targets:
            if not (
                isinstance(timesteps, list) and len(timesteps) == len(set(timesteps))
            ):
                return False
            for time in timesteps:
                if not (isinstance(time, int) and 1 <= time <= 20):
                    return False

    return True


def verify_distances(distances: List[List], qubit_operations: List[Dict]):
    num_qubits = len(qubit_operations)
    if not isinstance(distances, list):
        return False
    for distance in distances:
        if not isinstance(distance, list):
            return False
        if not (isinstance(distance[0], int) and distance[0] >= 0):
            return False
        if not isinstance(distance[1], list):
            return False

        for qubit_involved in distance[1]:
            if not (
                isinstance(qubit_involved, int) and 0 <= qubit_involved < num_qubits
            ):
                return False

        if len(set(distance[1])) != len(distance[1]):
            return False
    return True
