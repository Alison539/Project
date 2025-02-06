import React, { useContext } from "react";
import "./styles.css"
import { DistancesContext } from "../contexts/DistancesContext";

const OperationQubitButton = ({ point, onClicked, qubitSize, amSelected, qubit, selected_distance_id, onHover }) => {
    const { distances } = useContext(DistancesContext)

    const getOpacity = () => {
        if (selected_distance_id !== undefined) {
            const id = qubit.getid()
            if (distances[selected_distance_id][1].includes(id)) {
                return 1
            }
            else {
                return 0.33
            }
        }
        else {
            return 1
        }
    }



    function getColour(hadamard) {

        switch (hadamard) {
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

    function getBorder() {
        const measurement = qubit.getMeasurement();
        const logical_observable = qubit.getLogicalObservable();
        const width = (qubitSize / 8) + 1
        switch (measurement) {
            case 1:
                return (`${width}px solid #64310d`)
            case 2:
                return (`${width}px solid #0b522a`)
            case 3:
                return (`${width}px solid #350f4a`)
            default:
                if (logical_observable) {
                    return (`${width}px dashed #000000`)
                }
                return
        }
    }
    return (
        <button
            key={qubit.getid()}
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
                border: getBorder(),
                backgroundColor: `#${getColour(qubit.getHadamard())}`,
                opacity: getOpacity(),
            }}
            onClick={() => onClicked(qubit.getid())}
            onMouseEnter={() => { if (onHover) { onHover(qubit.getid()) } }}

        />
    );
};

export default OperationQubitButton;


