import networkx as nx
import re
import stim
from enum import Enum


class Line_Type(Enum):
    BLANK = 1
    BLOCK_START = 2
    BLOCK_END = 3
    INSTRUCTION = 4


class Ins_Type(Enum):
    DETECTOR = 1
    LOGICAL_OBSERVABLE = 2
    SHIFT_DETECTORS = 3
    ERROR = 4


class Decoder_graph:

    def __init__(self, stim_dem):
        self.graph = nx.Graph()
        repeat_stack = []
        ins_in_repeat = []
        in_repeat = False
        index = 0
        relative_detector_index = 0
        relative_coordinate_index = [0, 0, 0, 0]

        for index, line in enumerate(stim_dem):
            print(line)
            # print(line[0])
            print(type(line))
            print(line.type)

            category, arg = self.identify_line_type(str(line))
            if category == Line_Type.BLOCK_START:
                repeat_stack.append((index, arg))

            elif category == Line_Type.BLOCK_END:
                jump_back, iterations = repeat_stack.pop()
                if iterations > 0:
                    index = jump_back
                    repeat_stack.append((jump_back, iterations - 1))

            elif category == Line_Type.INSTRUCTION:
                name, tags, parens_ags, targets = self.identify_ins_type(arg)

                if name == Ins_Type.DETECTOR:
                    for relative_target in re.findall(r"D(\d+)", targets):
                        nodeID = "D" + str(
                            int(relative_target) + relative_detector_index
                        )
                        self.graph.add_node(nodeID)
                        if parens_ags:
                            coords = parens_ags.split(", ")
                            absolute_coords = [
                                float(coord) + relative_coordinate_index[i]
                                for i, coord in enumerate(coords)
                            ]
                            self.graph[nodeID]["coordinates"] = absolute_coords

                elif name == Ins_Type.SHIFT_DETECTORS:
                    if parens_ags:
                        coords = parens_ags.split(", ")
                        for i in range(0, coords.len()):
                            relative_coordinate_index[i] += float(coords[i])

                    offset_increment = int(targets.strip())
                    relative_detector_index += offset_increment

                elif name == Ins_Type.ERROR:
                    targets = targets.split("^")
                    for target in targets:
                        target = target.split(" ")

                        if target.len() == 1:
                            index = target[1:] + relative_detector_index
                            self.graph.add_node(("D" + str(index)))
                            self.graph.add_node(("B" + str(index)))
                            self.graph.add_edge(("D" + str(index)), ("B" + str(index)))

                        else:
                            index1 = target[0][1:] + relative_detector_index
                            self.graph.add_node(("D" + str(index1)))
                            if target[1][0] == "L":
                                self.graph.add_node(("B" + str(index1)))
                                self.graph.add_edge(
                                    ("D" + str(index1)),
                                    ("B" + str(index1)),
                                    logical_observable=True,
                                )
                            else:
                                index2 = target[1][1:] + relative_detector_index
                                self.graph.add_node(("D" + str(index2)))
                                self.graph.add_edge(
                                    ("D" + str(index1)), ("D" + str(index2))
                                )

            index += 1

    def identify_line_type(line):
        # 	<LINE> ::= <INDENT> (<INSTRUCTION> | <BLOCK_START> | <BLOCK_END>)? <COMMENT>? '\n'

        comment_loc = re.search("#", ins)
        if comment_loc:
            ins = ins[: comment_loc.start()]

        ins = re.sub(r"[\n\t]+", "", str(line))

        if ins == "":
            return Line_Type.BLANK, None

        block_start = re.search("{", ins)
        if block_start:
            ins = ins.split()
            if ins.len() != 3 or not re.match("repeat", ins[0]):
                raise Exception("Badly formed Block-Start")
            return Line_Type.BLOCK_START, int(ins[1])

        block_end = re.search("}", ins)
        if block_end:
            return Line_Type.BLOCK_END, None

        return Line_Type.INSTRUCTION, ins

    def identify_ins_type(ins):
        #   <INSTRUCTION> ::= <NAME> <TAG>? <PARENS_ARGUMENTS>? <TARGETS>
        if re.match("detector", ins):
            name = Ins_Type.DETECTOR
        elif re.match("logical_observable", ins):
            name = Ins_Type.LOGICAL_OBSERVABLE
        elif re.match("shift_detectors", ins):
            name = Ins_Type.SHIFT_DETECTORS
        elif re.match("error", ins):
            name = Ins_Type.ERROR
        else:
            raise Exception("Badly formed Instruction")

        tags = re.search(r"\[(.*?)\]", ins)
        parens_ags = re.search(r"\((.*?)\)", ins)

        end_parens = re.search(")", ins)
        end_square = re.search("]", ins)
        end_name = re.search(r"\s", ins)
        if end_parens:
            targets = ins[end_parens.end() :]
        elif end_square:
            targets = ins[end_square.end() :]
        else:
            targets = ins[end_name.end() :]

        return name, tags, parens_ags, targets


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
    print(matcher.graph)


def test2():
    dem = [
        " error(0.01911873511075362) D0 D1 # Commenting \n",
        "  error(0.02492213333333331) D0 D8 \n",
    ]
    matcher = Decoder_graph(dem)


if __name__ == "__main__":
    test()
