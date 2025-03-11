import networkx as nx
from typing import List
import stim


class UnionFind:
    def __init__(self, initial_clusters):
        self.parent = {}

        for node in initial_clusters:
            self.parent[node] = node

        pass

    def find(self, node):

        # Root
        if self.parent[node] == node:
            return node

        return self.find(self.parent[node])

    def union(self, a, b):
        aRoot = self.find(a)
        bRoot = self.find(b)

        self.parent[aRoot] = bRoot


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
                        self.graph.add_node(("D" + str(index)))
                        self.graph.add_node(("B" + str(index)))
                        self.graph.add_edge(("D" + str(index)), ("B" + str(index)))
                    elif len(target) == 2:
                        index1 = target[0].val + self.relative_detector_index
                        self.graph.add_node(("D" + str(index1)))
                        if target[1].is_logical_observable_id():
                            self.graph.add_node(("B" + str(index1)))
                            self.graph.add_edge(
                                ("D" + str(index1)),
                                ("B" + str(index1)),
                                logical_observable=True,
                            )
                        else:
                            index2 = target[1].val + self.relative_detector_index
                            self.graph.add_node(("D" + str(index2)))
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
        pass


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
    test()
