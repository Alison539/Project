import React from "react";
import "./styles.css"

const OperationQubitButton = ({point, onClicked, qubitSize, amSelected, qubit}) => {
    function getColour(hadamard){
        
        switch (hadamard){
            case 0:
                return (amSelected ? "d9cfb1" : "fff5d5");
            case 1:
                return (amSelected ? "6aa768" : "91e48e");
            case 2:
                return (amSelected ? "915be7" : "af8ee4");
            default:
                return "000000";
        }
    }
  
    function getBorder(measurement){
        switch (measurement){
            case 0:
                return (1)
            case 1:
                return ((qubitSize/8) + 1)
            default:
                return (1)
        }
    }
    return (
    <button
        key = {qubit.getid()}
        style={{
        position: "absolute",
        left: `${point.x}px`,
        top: `${point.y}px`,
        zIndex: 2,
        minWidth: `${qubitSize}px`,
        minHeight: `${qubitSize}px `,
        borderRadius: "50%",
        boxSizing: "border-box",
        padding: 0,
        margin: 0,
        cursor: "pointer",
        borderWidth:  `${getBorder(qubit.getMeasurement())}px `,
        borderColor: "black",
        backgroundColor: `#${getColour(qubit.getHadamard())}`,
        }}
        onClick={() => onClicked(qubit.getid())}
    />
  );
};

export default OperationQubitButton; 


