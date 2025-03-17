from .union_find import Decoder_graph
import stim


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

    nodes = ['D0', 'B0', 'D1', 'D4', 'D5', 'D2', 'D6', 'D3', 'D7', 'B3', 'B4', 'B7']
    edges = [('D0', 'B0'), ('D0', 'D1'), ('D0', 'D4'), ('D0', 'D5'), ('D1', 'D2'), ('D1', 'D5'), ('D1', 'D6'), ('D4', 'B4'), ('D4', 'D5'), ('D5', 'D6'), ('D2', 'D3'), ('D2', 'D6'), ('D2', 'D7'), ('D6', 'D7'), ('D3', 'D7'), ('D3', 'B3'), ('D7', 'B7')]

    assert matcher.graph.nodes == nodes
    assert matcher.graph.edges == edges

def test_