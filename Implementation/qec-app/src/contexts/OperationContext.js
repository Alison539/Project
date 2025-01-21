import React, { createContext, useContext, useState } from "react";
import { QubitContext } from "./QubitContext";
import { CoordinateSystemContext } from "./CoordinateSystemContext";

export const OperationContext = createContext();

class QubitOperation {
    constructor(coordinates, index) {
        this.location = coordinates;
        this.id = index;
        this.hadamard = 0;
        this.measurement = 0;
    }
    getid() {
        return (this.id);
    }
    getLocation() {
        return (this.location);
    }
    getHadamard() {
        return (this.hadamard);
    }
    getMeasurement() {
        return (this.measurement);
    }
    setHadamard(hadamard, qubit) {
        this.measurement = qubit.measurement;
        this.hadamard = hadamard;
    }
    setMeasurement(measurement, qubit) {
        this.hadamard = qubit.hadamard;
        this.measurement = measurement;
    }
    copyHadamardMeasurement(qubit) {
        this.hadamard = qubit.hadamard;
        this.measurement = qubit.measurement;
    }
}

export const OperationProvider = ({ children }) => {
    const { qubits } = useContext(QubitContext)
    const { coordSys } = useContext(CoordinateSystemContext)

    const [qubitOperations, setQubitOperations] = useState([]);
    const [twoQubitOperations, setTwoQubitOperations] = useState([]);
    const [length, setLength] = useState(0);
    const [coordsToIndeces, setCoordsToIndeces] = useState(undefined);

    function makeCoordsStrings(coords){
        return (`${coords.x}_${coords.y}`);
    }

    const instantiate = () => {
        const qlength = qubits.length
        setLength(qlength);
        setCoordsToIndeces(() => {
            const newCoordsToIndeces = new Map();
            for (let i = 0; i < qlength; i++) {
                newCoordsToIndeces.set(makeCoordsStrings(qubits[i].getLocation()), i);
            }
            return newCoordsToIndeces;
        })
        setQubitOperations(qubits.map((qubit, index) => {
            const newQop = new QubitOperation(qubit.location, index);
            return newQop;
        }))
        const newTwoQubitOperations = new Array(qlength);
        for (let i = 0; i < qlength; i++) {
            newTwoQubitOperations[i] = new Array(qlength);
            for (let j = 0; j < qlength; j++) {
                newTwoQubitOperations[i][j] = []
            }
        }
        setTwoQubitOperations(newTwoQubitOperations);
    }

    const deleteOperations = (qubitOpID) => {
        const qubitOp = qubitOperations[qubitOpID]
        setQubitOperations((previousQubits) => {
            const updatedQubits = previousQubits.map((q, index) => {
                if (index === qubitOpID) {
                    const newQuOp = new QubitOperation(qubitOp.getLocation(), qubitOpID)
                    return newQuOp;
                }
                else { return q };
            });
            return updatedQubits;
        });
        setTwoQubitOperations((previousTwoQubitOps) => {
            const updatedQubitOps = previousTwoQubitOps.map((controls, index) => {
                if (index === qubitOpID) {
                    const newControls = new Array(length);
                    for (let j = 0; j < length; j++) {
                        newControls[j] = []
                    }
                    return newControls;
                }
                else {
                    return (controls.map((destination, index) => {
                        if (index === qubitOpID) { return []; }
                        else { return destination }
                    }))
                };
            });
            return updatedQubitOps;
        })
    }

    function getRelativeNeighbour(oldFocusID, oldNeighbourID, newFocusID) {
        const oldFocus = qubitOperations[oldFocusID].getLocation()
        const oldNeighbour = qubitOperations[oldNeighbourID].getLocation()
        const newFocus = qubitOperations[newFocusID].getLocation()
        let newX = newFocus.x + (oldNeighbour.x - oldFocus.x)
        let newY = newFocus.y + (oldNeighbour.y - oldFocus.y)
        if (coordSys == 1 && (newFocus.y % 2) !== (oldFocus.y % 2)){
            if ((oldNeighbour.y - oldFocus.y) !== 0){
                if (oldFocus.y % 2 == 0){
                    newX += 1
                }
                else{
                    newX -= 1
                }
            }
        }
        const newLocation = { x: newX, y: newY }
        return coordsToIndeces.get(makeCoordsStrings(newLocation))
    }

    const replicateQubitOps = (qubitToCopyID, qubitToPasteID) => {
        const copy = qubitOperations[qubitToCopyID];
        const original = qubitOperations[qubitToPasteID];
        setQubitOperations((previousQubits) => {
            const updatedQubits = previousQubits.map((q, index) => {
                if (index === qubitToPasteID) {
                    const newQuOp = new QubitOperation(original.getLocation(), qubitToPasteID)
                    newQuOp.copyHadamardMeasurement(copy)
                    return newQuOp;
                }
                else { return q };
            });
            return updatedQubits;
        });
        const newTwoQubitOperations = new Array(length);
        for (let i = 0; i < length; i++) {
            newTwoQubitOperations[i] = new Array(length);
            for (let j = 0; j < length; j++) {
                newTwoQubitOperations[i][j] = [...twoQubitOperations[i][j]]
            }
        }
        for (let i = 0; i < length; i++) {
            const relativeNeighbour = getRelativeNeighbour(qubitToCopyID, i, qubitToPasteID)
            if (relativeNeighbour !== undefined) {
                newTwoQubitOperations[qubitToPasteID][relativeNeighbour] = [...twoQubitOperations[qubitToCopyID][i]]
                newTwoQubitOperations[relativeNeighbour][qubitToPasteID] = [...twoQubitOperations[i][qubitToCopyID]]
            }
        }
        setTwoQubitOperations(newTwoQubitOperations);
    }

    const setHadamard = (qubitOpID, hadamardValue) => {
        const qubitOp = qubitOperations[qubitOpID];
        setQubitOperations((previousQubits) => {
            const updatedQubits = previousQubits.map((q, index) => {
                if (index === qubitOpID) {
                    const newQuOp = new QubitOperation(qubitOp.getLocation(), qubitOpID)
                    newQuOp.setHadamard(hadamardValue, qubitOp)
                    return newQuOp;
                }
                else { return q };
            });
            return updatedQubits;
        });
    }

    const setMeasurement = (qubitOpID, measurement) => {
        const qubitOp = qubitOperations[qubitOpID];
        setQubitOperations((previousQubits) => {
            const updatedQubits = previousQubits.map((q, index) => {
                if (index === qubitOpID) {
                    const newQuOp = new QubitOperation(qubitOp.getLocation(), qubitOpID)
                    newQuOp.setMeasurement(measurement, qubitOp)
                    return newQuOp;
                }
                else { return q };
            });
            return updatedQubits;
        });
    }

    const addTwoQubitOp = (controlID, targetID, timestep) => {
        const newTwoQubitOperations = new Array(length);
        for (let i = 0; i < length; i++) {
            newTwoQubitOperations[i] = new Array(length);
            for (let j = 0; j < length; j++) {
                newTwoQubitOperations[i][j] = [...twoQubitOperations[i][j]]
            }
        }
        const oldList = twoQubitOperations[controlID][targetID]
        newTwoQubitOperations[controlID][targetID] = [...oldList, timestep]

        setTwoQubitOperations(newTwoQubitOperations)
    }

    return (
        <OperationContext.Provider value={{ qubitOperations, twoQubitOperations, instantiate, deleteOperations, replicateQubitOps, setHadamard, setMeasurement, addTwoQubitOp }}>
            {children}
        </OperationContext.Provider>
    );
}
