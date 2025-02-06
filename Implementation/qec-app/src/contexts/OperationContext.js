import React, { createContext, useContext, useState } from "react";
import { QubitContext } from "./QubitContext";
import { CoordinateSystemContext } from "./CoordinateSystemContext";
import { DistancesContext } from "./DistancesContext";

export const OperationContext = createContext();

class QubitOperation {
    constructor(qubit, index) {
        this.location = qubit.getLocation();
        this.id = (index !== undefined) ? index : qubit.getid();
        this.logical_observable = false;
        this.hadamard = 0;
        this.measurement = 0;
    }
    getid() {
        return (this.id);
    }
    getLocation() {
        return (this.location);
    }
    getLogicalObservable() {
        return (this.logical_observable)
    }
    getHadamard() {
        return (this.hadamard);
    }
    getMeasurement() {
        return (this.measurement);
    }
    setLogicalObservable(qubit) {
        this.logical_observable = !qubit.logical_observable;
        this.measurement = 0;
    }
    setHadamard(hadamard) {
        this.hadamard = hadamard;
    }
    setMeasurement(measurement) {
        this.logical_observable = false;
        this.measurement = measurement;
    }
    copyHadamardMeasurement(qubit) {
        this.logical_observable = qubit.logical_observable;
        this.hadamard = qubit.hadamard;
        this.measurement = qubit.measurement;
    }
}

export const OperationProvider = ({ children }) => {
    const { qubits } = useContext(QubitContext)
    const { coordSys } = useContext(CoordinateSystemContext)
    const { initialiseDistance } = useContext(DistancesContext)

    const [qubitOperations, setQubitOperations] = useState([]);
    const [twoQubitOperations, setTwoQubitOperations] = useState([]);
    const [length, setLength] = useState(0);
    const [coordsToIndeces, setCoordsToIndeces] = useState(undefined);

    function makeCoordsStrings(coords) {
        return (`${coords.x}_${coords.y}`);
    }

    const instantiate = () => {
        initialiseDistance();
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
            const newQop = new QubitOperation(qubit, index);
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
                    const newQuOp = new QubitOperation(qubitOp)
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
        if (coordSys === 1 && (newFocus.y % 2) !== (oldFocus.y % 2)) {
            if ((oldNeighbour.y - oldFocus.y) !== 0) {
                if (oldFocus.y % 2 === 0) {
                    newX += 1
                }
                else {
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
                    const newQuOp = new QubitOperation(original)
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
                    const newQuOp = new QubitOperation(qubitOp)
                    newQuOp.copyHadamardMeasurement(qubitOp)
                    newQuOp.setHadamard(hadamardValue)
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
                    const newQuOp = new QubitOperation(qubitOp)
                    newQuOp.copyHadamardMeasurement(qubitOp)
                    newQuOp.setMeasurement(measurement)
                    return newQuOp;
                }
                else { return q };
            });
            return updatedQubits;
        });
    }
    const setLogicalObservable = (qubitOpID) => {
        const qubitOp = qubitOperations[qubitOpID];
        setQubitOperations((previousQubits) => {
            const updatedQubits = previousQubits.map((q, index) => {
                if (index === qubitOpID) {
                    const newQuOp = new QubitOperation(qubitOp)
                    newQuOp.copyHadamardMeasurement(qubitOp)
                    newQuOp.setLogicalObservable(qubitOp)
                    return newQuOp;
                }
                else { return q };
            });
            return updatedQubits;
        });
    }

    const addTwoQubitOp = (controlID, targetID, timestep) => {
        if (controlID !== targetID) {
            const newTwoQubitOperations = new Array(length);
            for (let i = 0; i < length; i++) {
                newTwoQubitOperations[i] = new Array(length);
                for (let j = 0; j < length; j++) {
                    newTwoQubitOperations[i][j] = [...twoQubitOperations[i][j]]
                }
            }
            const oldList = twoQubitOperations[controlID][targetID]
            newTwoQubitOperations[controlID][targetID] = [...new Set([...oldList, timestep])]

            setTwoQubitOperations(newTwoQubitOperations)
        }
    }

    return (
        <OperationContext.Provider value={{ qubitOperations, twoQubitOperations, instantiate, deleteOperations, replicateQubitOps, setHadamard, setMeasurement, addTwoQubitOp, setLogicalObservable }}>
            {children}
        </OperationContext.Provider>
    );
}
