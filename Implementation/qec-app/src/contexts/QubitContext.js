import React, { createContext, useContext, useState } from "react";
import { CoordinateSystemContext } from "./CoordinateSystemContext";

export const QubitContext = createContext();

export class Qubit {
    constructor(coordinates, index) {
        this.location = coordinates;
        this.id = index;
        this.class = null;
        this.logical_observalble = false;
        this.label = "";
    }
    qubitFromCopy(qubit, newid) {
        this.location = qubit.getLocation();
        this.id = newid;
        this.class = qubit.getClass();
        this.logical_observalble = qubit.getLogicalObservable();
        this.label = qubit.getLabel();
    }
    getid() {
        return (this.id);
    }
    getLocation() {
        return (this.location);
    }
    getLogicalObservable() {
        return (this.logical_observalble);
    }
    getClass() {
        return (this.class);
    }
    getLabel() {
        return (this.label);
    }
    setClass(classId) {
        this.class = classId;
    }
    setLogicalObservable() {
        this.logical_observalble = !this.logical_observalble;
    }
    setLabel(label) {
        this.label = label;
    }
}

export const QubitProvider = ({ children }) => {
    const {coordsGivenCoordSys} = useContext(CoordinateSystemContext)

    const [qubits, setQubits] = useState([]);
    const [highestX, setHighestX] = useState(0);
    const [highestY, setHighestY] = useState(0);

    function updateHighest(coords) {
        const actualCoords = coordsGivenCoordSys(coords)
        if (actualCoords.x > highestX) {
            setHighestX(coords.x)
        }
        if (actualCoords.y > highestY) {
            setHighestY(coords.y)
        }
    }

    const addQubit = (coordinates, index) => {
        const newQubit = new Qubit(coordinates, index);
        setQubits((previousQubits) => [...previousQubits, newQubit]);
    }
    const removeQubit = (qubit) => {
        const qid = qubit.getid()
        setQubits(qubits.filter((q) => q.getid() !== qid));
    }
    const resetQubits = () => {
        setQubits([]);
    }
    const setLogicalObservablePerQubit = (qubit) => {
        const qid = qubit.getid()
        setQubits((previousQubits) => {
            const updatedQubits = previousQubits.map((q) => {
                if (q.getid() === qid) {
                    const newQ = new Qubit(qubit.getLocation(), qid)
                    newQ.setLogicalObservable()
                    return newQ;
                }
                else {
                    return q;
                }
            });
            return updatedQubits;
        })
    }
    const makeIdsConsecutive = () => {
        setQubits((previousQubits) => {
            const updatedQubits = previousQubits.map((q, newid) => {
                updateHighest(q.getLocation())
                const newQ = new Qubit(q.getLocation(), newid);
                newQ.qubitFromCopy(q, newid);
                return newQ;
            }
            );
            return updatedQubits;
        })

    }

    return (
        <QubitContext.Provider value={{ qubits, addQubit, removeQubit, resetQubits, setLogicalObservablePerQubit, makeIdsConsecutive, highestX, highestY }}>
            {children}
        </QubitContext.Provider>
    );
}
