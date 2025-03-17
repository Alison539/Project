import networkx as nx
from typing import List
import stim
import numpy as np


class UnionFind:
    def __init__(self, syndromes: List[bool]):
        self.parent = list(range(len(syndromes)))
        self.size = [1 for _ in range(0, len(syndromes))]
        self.parity = [1 if syndrome else 0 for syndrome in syndromes]
        self.vertices_encountered = []
        self.terminated = [False for _ in range(0, len(syndromes))]
        self.isRoot = [True if syndrome else False for syndrome in syndromes]

    def find(self, node):
        if self.parent[node] == node:
            for vertex in self.vertices_encountered:
                self.parent[vertex] = node
            self.vertices_encountered = []
            return node

        self.vertices_encountered.append(node)
        return self.find(self.parent[node])

    def union(self, a: int, b: int) -> bool:
        aRoot = self.find(a)
        bRoot = self.find(b)

        if aRoot == bRoot:
            return False

        aSize = self.size[aRoot]
        bSize = self.size[bRoot]
        totalSize = aSize + bSize
        newParity = (self.parity[aRoot] + self.parity[bRoot]) % 2

        if aSize < bSize:
            newRoot = bRoot
            self.parent[aRoot] = bRoot

            self.isRoot[aRoot] = False
            self.isRoot[bRoot] = True

        else:
            newRoot = aRoot
            self.parent[bRoot] = aRoot

            self.isRoot[bRoot] = False
            self.isRoot[aRoot] = True

        self.size[newRoot] = totalSize
        self.parity[newRoot] = newParity
        self.terminated[newRoot] = self.terminated[aRoot] or self.terminated[bRoot]

        return True

    def terminate(self, u):
        uRoot = self.find(u)
        self.terminated[uRoot] = True


class Decoder_graph:

    def __init__(self, stim_dem):
        self.graph = nx.Graph()
        self.relative_detector_index = 0
        self.relative_coordinate_index = [0, 0, 0, 0]

        self.process_stim_dem(stim_dem)

    def process_stim_dem(self, stim_dem):
        for line in stim_dem:
            if line.type == "error":
                targets = line.target_groups()
                args = line.args_copy()  # TODO: Could add weights
                for target in targets:
                    if len(target) == 1:
                        index = target[0].val + self.relative_detector_index
                        self.graph.add_node(("D" + str(index)), boundary=False)
                        self.graph.add_node(("B" + str(index)), boundary=True)
                        self.graph.add_edge(
                            ("D" + str(index)),
                            ("B" + str(index)),
                            logical_observable=False,
                        )
                    elif len(target) == 2:
                        index1 = target[0].val + self.relative_detector_index
                        self.graph.add_node(("D" + str(index1)), boundary=False)
                        if target[1].is_logical_observable_id():
                            self.graph.add_node(("B" + str(index1)), boundary=True)
                            self.graph.add_edge(
                                ("D" + str(index1)),
                                ("B" + str(index1)),
                                logical_observable=True,
                            )
                        else:
                            index2 = target[1].val + self.relative_detector_index
                            self.graph.add_node(("D" + str(index2)), boundary=False)
                            self.graph.add_edge(
                                ("D" + str(index1)),
                                ("D" + str(index2)),
                                logical_observable=False,
                            )
            elif line.type == "detector":
                targets = line.target_groups()
                args = line.args_copy()
                coords = []
                for i in range(0, len(args)):
                    coords.append(args[i] + self.relative_coordinate_index[i])
                for target in targets:
                    index = target[0].val + self.relative_detector_index
                    nodeid = "D" + str(index)
                    self.graph.add_node(nodeid, coordinates=coords)

            elif line.type == "shift_detectors":
                targets = line.target_groups()
                args = line.args_copy()
                for i in range(0, len(args)):
                    self.relative_coordinate_index[i] += args[i]
                for target in targets:
                    self.relative_detector_index += target[0].val

            elif line.type == "repeat":
                repeat_body = line.body_copy()
                for i in range(0, line.repeat_count):
                    self.process_stim_dem(repeat_body)

        self._generate_edge_dict()

        # final possible line type is that "logical_observable" but that means involved in no errors
        # therefore not needed in decoder graph

    def _generate_edge_dict(self):
        self.get_edge = {}
        for edge in self.graph.edges:
            self.get_edge[edge] = edge
            self.get_edge[(edge[1], edge[0])] = edge

    def _define_syndrome(self, syndromes: List[bool]):
        for node in self.graph.nodes:
            self.graph.nodes[node]["syndrome"] = False
        for i, syndrome in enumerate(syndromes):
            if syndrome:
                node_name = "D" + str(i)
                self.graph.nodes[node_name]["syndrome"] = True

    def syndrome_validation(self, syndromes: List[bool]):
        self.clusters = UnionFind(syndromes=syndromes)
        self._define_syndrome(syndromes=syndromes)
        boundary_lists = [[i] for i in range(0, len(syndromes))]
        odd_root_list = [False for i in range(0, len(syndromes))]
        odd_roots = []

        for i, syndrome in enumerate(syndromes):
            if syndrome:
                odd_root_list[i] = True
                odd_roots.append(i)

        edge_support = {}  # 0 = Unoccupied, 1 = Half-Grown, 2 = Grown
        for edge in self.graph.edges:
            edge_support[edge] = 0

        def grow(root):
            fusion_edges = []
            boundary_list = boundary_lists[root]
            for vertex in boundary_list:
                vertex_name = "D" + str(vertex)
                for neighbour in self.graph.neighbors(vertex_name):
                    edge = self.get_edge[(vertex_name, neighbour)]
                    if edge_support[edge] == 0:
                        edge_support[edge] = 1
                    elif edge_support[edge] == 1:
                        edge_support[edge] = 2
                        fusion_edges.append(edge)
            return fusion_edges

        def fuse_clusters(fusion_edges):
            actual_fusion_edges = []
            for u, v in fusion_edges:
                u_index = int(u[1:])
                v_index = int(v[1:])
                if self.graph.nodes[v]["boundary"]:
                    self.clusters.terminate(u_index)
                u_root = self.clusters.find(u_index)
                v_root = self.clusters.find(v_index)
                distinct_clusters = self.clusters.union(u_index, v_index)
                if distinct_clusters:
                    actual_fusion_edges.append((u_root, v_root))
            return actual_fusion_edges

        def fuse_boundary_lists(actual_fusion_edges):
            for u_root, v_root in actual_fusion_edges:
                new_root = self.clusters.find(u_root)
                if v_root == new_root:
                    boundary_lists[v_root].extend(boundary_lists[u_root])
                else:
                    boundary_lists[u_root].extend(boundary_lists[v_root])
                odd_root_list[u_root] = False
                odd_root_list[v_root] = False
                if not (
                    self.clusters.terminated[new_root]
                    or self.clusters.parity[new_root] == 0
                ):
                    odd_root_list[new_root] = True

        def update_boundary_lists(roots):
            for root in roots:
                for vertex in boundary_lists[root]:
                    vertex_name = "D" + str(vertex)
                    all_edges_explored = True
                    for neighbour in self.graph.neighbors(vertex_name):
                        if edge_support[self.get_edge[(vertex_name, neighbour)]] != 2:
                            all_edges_explored = False
                            break
                    if all_edges_explored:
                        boundary_lists[root].remove(vertex)

        while len(odd_roots) > 0:
            fusion_list = []
            for root in odd_roots:
                fusion_edges = grow(root)
                fusion_list.extend(fusion_edges)
            actual_fusions = fuse_clusters(fusion_list)
            fuse_boundary_lists(actual_fusion_edges=actual_fusions)

            odd_roots = []
            for root, valid in enumerate(odd_root_list):
                if valid:
                    odd_roots.append(root)
            update_boundary_lists(odd_roots)

        for edge, state in edge_support.items():
            self.graph.edges[edge]["erased"] = state == 2

    def erasure_decoder(self) -> bool:

        def generate_seed():
            seed = []
            for j, isRoot in enumerate(self.clusters.isRoot):
                if isRoot:
                    seed.append(j)
            return seed

        def make_spanning_tree(seeds):
            for edge in self.graph.edges:
                self.graph.edges[edge]["tree"] = False

            visited = {}
            seed_list = []
            for node in self.graph.nodes:
                visited[node] = False
            for seed in seeds:
                seed_name = "D" + str(seed)
                visited[seed_name] = True
                seed_list.append(seed_name)

            borders = []
            boundary_borders = []

            self.edges_in_tree = 0

            stack = []
            for seed in seed_list:
                num_connections = 0
                for neighbour in self.graph.neighbors(seed):
                    edge = self.get_edge[(seed, neighbour)]
                    if self.graph.edges[edge]["erased"]:
                        if not visited[neighbour]:
                            self.graph.edges[edge]["tree"] = True
                            self.edges_in_tree += 1
                            visited[neighbour] = True
                            stack.append(neighbour)
                            num_connections += 1
                        self.graph.edges[edge]["erased"] = False
                if num_connections == 1:
                    borders.append(seed)

            while len(stack) > 0:
                vertex = stack.pop(0)
                is_border = True
                for neighbour in self.graph.neighbors(vertex):
                    edge = self.get_edge[(vertex, neighbour)]
                    if self.graph.edges[edge]["erased"]:
                        if not visited[neighbour]:
                            self.graph.edges[edge]["tree"] = True
                            self.edges_in_tree += 1
                            visited[neighbour] = True
                            stack.append(neighbour)
                            is_border = False
                        self.graph.edges[edge]["erased"] = False
                if is_border:
                    if self.graph.nodes[vertex]["boundary"]:
                        boundary_borders.append(vertex)
                    else:
                        borders.append(vertex)
            return borders, boundary_borders

        def leaf_edges(borders, remove_from_tree, know_boundary):
            leaf_edges = []
            for border in borders:
                for neighbour in self.graph.neighbors(border):
                    edge = self.get_edge[(border, neighbour)]
                    if self.graph.edges[edge]["tree"]:
                        leaf_edges.append((edge, border, neighbour))
                        if remove_from_tree:
                            self.graph.edges[edge]["tree"] = False
                            self.edges_in_tree -= 1
                        if know_boundary:
                            break
            return leaf_edges

        def peel(pendant, neighbour):
            if self.graph.nodes[pendant]["syndrome"]:
                self.graph.nodes[pendant]["syndrome"] = False
                in_syndrome = self.graph.nodes[neighbour]["syndrome"]
                self.graph.nodes[neighbour]["syndrome"] = not in_syndrome
                return True
            else:
                return False

        def process_leaf(leaf_edge, pendant, neighbour):
            is_error = peel(pendant, neighbour)
            if is_error:
                self.all_errors.append(leaf_edge)

            new_leaf_edges = leaf_edges([neighbour], False, False)
            if len(new_leaf_edges) == 1:
                self.edges_stack.append(new_leaf_edges[0])
                self.graph.edges[new_leaf_edges[0][0]]["tree"] = False
                self.edges_in_tree -= 1

        seeds = generate_seed()
        borders, boundary_borders = make_spanning_tree(seeds)
        self.all_errors = []
        self.edges_stack = leaf_edges(borders, True, True)
        while len(self.edges_stack) > 0:
            leaf_edge, pendant, neighbour = self.edges_stack.pop(0)
            process_leaf(leaf_edge, pendant, neighbour)

        current_boundary = 0
        while self.edges_in_tree > 0:
            self.edges_stack = leaf_edges(
                [boundary_borders[current_boundary]], True, True
            )
            while len(self.edges_stack) > 0:
                leaf_edge, pendant, neighbour = self.edges_stack.pop(0)
                process_leaf(leaf_edge, pendant, neighbour)
            current_boundary += 1

    def logical_observable_impact(self) -> bool:
        logical_observable_error = False
        for edge in self.all_errors:
            if self.graph.edges[edge]["logical_observable"]:
                logical_observable_error = not logical_observable_error
        return logical_observable_error

    def decode_batch(self, syndromess: List[List[bool]]) -> List[bool]:
        predictions = []
        for syndromes in syndromess:
            self.syndrome_validation(syndromes=syndromes)
            self.erasure_decoder()
            prediction = self.logical_observable_impact()
            predictions.append(prediction)
        return predictions


def test():
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=1,
        distance=5,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = Decoder_graph(detector_error_model)
    print(matcher.graph.nodes)
    print(matcher.graph.edges)


def test_decoder_graph():
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=1,
        distance=5,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = Decoder_graph(detector_error_model)

    nodes = ["D0", "B0", "D1", "D4", "D5", "D2", "D6", "D3", "D7", "B3", "B4", "B7"]
    edges = [
        ("D0", "B0"),
        ("D0", "D1"),
        ("D0", "D4"),
        ("D0", "D5"),
        ("D1", "D2"),
        ("D1", "D5"),
        ("D1", "D6"),
        ("D4", "B4"),
        ("D4", "D5"),
        ("D5", "D6"),
        ("D2", "D3"),
        ("D2", "D6"),
        ("D2", "D7"),
        ("D6", "D7"),
        ("D3", "D7"),
        ("D3", "B3"),
        ("D7", "B7"),
    ]
    assert list(matcher.graph.nodes) == nodes
    assert list(matcher.graph.edges) == edges


def test_syndrome_validation():
    syndrome = [1, 0, 1, 0, 0, 0, 1, 0]
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=1,
        distance=5,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = Decoder_graph(detector_error_model)

    matcher.syndrome_validation(syndromes=syndrome)

    erasures = [matcher.graph.edges[edge]["erased"] for edge in matcher.graph.edges]

    correct_erasures = [
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        False,
        False,
        False,
        False,
        False,
    ]
    assert erasures == correct_erasures


def test_erasure_decoder():

    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=1,
        distance=5,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = Decoder_graph(detector_error_model)

    syndrome = [1, 0, 1, 0, 0, 0, 1, 0]
    matcher.syndrome_validation(syndromes=syndrome)
    matcher.erasure_decoder()
    expected_errors = [("D2", "D6"), ("D0", "B0")]
    assert matcher.all_errors == expected_errors


def test_erasure_decoder2():
    circuit = circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        rounds=1,
        distance=3,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = Decoder_graph(detector_error_model)

    syndrome = [0, 0, 0, 1, 0, 0, 0, 0]
    matcher.syndrome_validation(syndromes=syndrome)
    matcher.erasure_decoder()
    expected_errors = [("D3", "B3")]
    assert matcher.all_errors == expected_errors

    syndrome = [1, 0, 0, 0, 1, 1, 0, 0]
    matcher.syndrome_validation(syndromes=syndrome)
    matcher.erasure_decoder()
    expected_errors = [("D0", "D4"), ("D5", "B5")]
    assert matcher.all_errors == expected_errors

    syndrome = [0, 0, 1, 0, 0, 0, 0, 1]
    matcher.syndrome_validation(syndromes=syndrome)
    matcher.erasure_decoder()
    expected_errors = [
        [("D2", "B2"), ("D7", "B7")],
        [("D2", "D3"), ("D3", "D7")],
        [("D2", "D6"), ("D6", "D7")],
    ]
    assert matcher.all_errors in expected_errors


def testing_overall(num_shots):
    circuit = circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        rounds=1,
        distance=3,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )

    sampler = circuit.compile_detector_sampler()
    detection_events, observable_flips = sampler.sample(
        num_shots, separate_observables=True
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    print(detector_error_model)
    matcher = Decoder_graph(detector_error_model)

    num_errors = 0
    for i, syndromes in enumerate(detection_events):
        matcher.syndrome_validation(syndromes=syndromes)
        matcher.erasure_decoder()
        prediction = matcher.logical_observable_impact()
        actual = observable_flips[i][0]
        prediction = prediction
        if actual != prediction:
            num_errors += 1
    return num_errors


def count_logical_errors(circuit: stim.Circuit, num_shots: int) -> int:

    sampler = circuit.compile_detector_sampler()
    detection_events, observable_flips = sampler.sample(
        num_shots, separate_observables=True
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    print(detector_error_model)
    matcher = Decoder_graph(detector_error_model)
    predictions = matcher.decode_batch(detection_events)

    num_errors = 0
    for shot in range(num_shots):
        actual_for_shot = observable_flips[shot]
        predicted_for_shot = predictions[shot]
        if actual_for_shot[0] != predicted_for_shot:
            num_errors += 1
    return num_errors


if __name__ == "__main__":
    # test_decoder_graph()
    # test_syndrome_validation()
    # test_erasure_decoder()
    # test_erasure_decoder2()
    print(testing_overall(1000))
    """
    circuit = circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        rounds=1,
        distance=3,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )
    print(count_logical_errors(circuit, 1000))

    black = False
    black = not black
    print(black)"
    """
