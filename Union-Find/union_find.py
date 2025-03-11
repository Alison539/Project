import networkx as nx
from typing import List
import stim
import re


class UnionFind:
    def __init__(self, syndromes: List[bool]):
        self.parent = list(range(len(syndromes)))
        self.size = [1 for _ in range(0, len(syndromes))]
        self.parity = [1 if syndrome else 0 for syndrome in syndromes]
        self.vertices_encountered = []
        self.terminated = [False for _ in range(0, len(syndromes))]

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

        else:
            newRoot = aRoot
            self.parent[bRoot] = aRoot

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
                        self.graph.add_node(("B" + str(index)), boundary=False)
                        self.graph.add_edge(("D" + str(index)), ("B" + str(index)))
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
                                ("D" + str(index1)), ("D" + str(index2))
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

            # final possible line type is that "logical_observable" but that means involved in no errors
            # therefore not needed in decoder graph

    def syndrome_validation(self, syndromes: List[bool]):
        clusters = UnionFind(syndromes=syndromes)
        boundary_lists = {}
        odd_root_list = []
        new_odd_root_list = set()

        for i, syndrome in enumerate(syndromes):
            if syndrome:
                boundary_lists[i] = [i]
                odd_root_list.append(i)

        edge_support = {}  # 0 = Unoccupied, 1 = Half-Grown, 2 = Grown
        get_edge = {}
        for edge in self.graph.edges:
            edge_support[edge] = 0

            get_edge[edge] = edge
            get_edge[(edge[1], edge[0])] = edge

        def grow(root):
            fusion_edges = []
            boundary_list = boundary_lists[root]
            for vertex in boundary_list:
                vertex_name = "D" + str(vertex)
                for neighbour in self.graph.neighbors(vertex_name):
                    edge = get_edge[(vertex_name, neighbour)]
                    if edge_support[edge] == 0:
                        edge_support[edge] = 1
                    if edge_support[edge] == 1:
                        edge_support[edge] = 2
                        fusion_edges.append(edge)
            return fusion_edges

        def fuse_clusters(fusion_edges):
            actual_fusion_edges = []
            for u, v in fusion_edges:
                if self.graph[v]["boundary"]:
                    clusters.terminate(u)
                u_index = int(u[1:])
                v_index = int(v[1:])
                u_root = clusters.find(u)
                v_root = clusters.find(v)
                distinct_clusters = clusters.union(u_index, v_index)
                if distinct_clusters:
                    actual_fusion_edges.append((u_root, v_root))
            return actual_fusion_edges

        def fuse_boundary_lists(actual_fusion_edges):
            for u_root, v_root in actual_fusion_edges:
                new_root = clusters.find(u_root)
                if v_root == new_root:
                    boundary_lists[v_root].extend(boundary_lists[u_root])
                else:
                    boundary_lists[u_root].extend(boundary_lists[v_root])
                if not (
                    clusters.terminated[new_root] or clusters.parity[new_root] == 0
                ):
                    new_odd_root_list.add(new_root)
                else:
                    new_odd_root_list.remove(new_root)

        def update_boundary_lists(roots):
            for root in roots:
                for vertex in boundary_lists[root]:
                    vertex_name = "D" + str(vertex)
                    for neighbour in self.graph.neighbors(vertex_name):
                        if edge_support[get_edge[(vertex_name, neighbour)]] == 2:
                            boundary_lists[root].remove(neighbour)

        while len(odd_root_list) > 0:
            fusion_list = []
            for root in odd_root_list:
                fusion_edges = grow(root)
                fusion_list.extend(fusion_edges)
            actual_fusions = fuse_clusters(fusion_list)
            fuse_boundary_lists(actual_fusion_edges=actual_fusions)

            odd_root_list = list(new_odd_root_list)
            update_boundary_lists(odd_root_list)

        for edge, state in edge_support.items():
            self.graph[edge]["erased"] = state == 2


def test():
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=40,
        distance=2,
        after_clifford_depolarization=0.01,
        after_reset_flip_probability=0.01,
        before_measure_flip_probability=0.01,
        before_round_data_depolarization=0.01,
    )
    detector_error_model = circuit.detector_error_model(decompose_errors=True)
    matcher = Decoder_graph(detector_error_model)
    print(matcher.graph.nodes.data())
    print(matcher.graph.edges.data())


if __name__ == "__main__":
    edges = [(1, 2), (2, 3)]
    for u, v in edges:
        print(u)
