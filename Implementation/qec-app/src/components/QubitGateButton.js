import React from "react";

const labels = [
    "H",
    "H_YZ",
    "CNOT",
    "MR",
    "MRX",
    "MRY"
]

function getColor(index, currentOperation) {
    switch (index) {
        case 1:
            return (currentOperation === 1 ? "#6aa768" : "#91e48e")
        case 2:
            return (currentOperation === 2 ? "#915be7" : "#af8ee4")
        default:
            return (currentOperation === index ? "#668265" : "#b5c9b4")
    }
}

function getBorder(index) {
    switch (index) {
        case 4:
            return ("4px solid #64310d")
        case 5:
            return ("4px solid #0b522a")
        case 6:
            return ("4px solid #350f4a")
        default:
            return
    }
}

const QubitGateButton = ({ currentOperation, onSelectOperation, index }) => {
    return (
        <button
            className="option-button"
            style={{
                backgroundColor: getColor(index, currentOperation),
                border: getBorder(index)
            }}
            onClick={() => onSelectOperation(index)}>
            {labels[index - 1]}
        </button>
    )
}

export default QubitGateButton;