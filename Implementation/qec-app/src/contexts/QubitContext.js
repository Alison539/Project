import React, { createContext, useContext, useState } from "react";
import { CoordinateSystemContext } from "./CoordinateSystemContext";

export const QubitContext = createContext();

export class Qubit {
    constructor(coordinates, index) {
        this.location = coordinates;
        this.id = index;
    }
    qubitFromCopy(qubit, newid) {
        this.location = qubit.getLocation();
        this.id = newid;
    }
    getid() {
        return (this.id);
    }
    getLocation() {
        return (this.location);
    }
}

export const QubitProvider = ({ children }) => {
    const {coordsGivenCoordSys} = useContext(CoordinateSystemContext)

    const [qubits, setQubits] = useState([]);
    const [highest, setHighest] = useState([0,0]);
    
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
    const findExtremes = () => {
        let maxX = 0;
        let maxY = 0;
        qubits.forEach((q) => {
            let coords = coordsGivenCoordSys(q.getLocation())
            if (coords.x > maxX) {
                maxX = coords.x
            }
            if (coords.y > maxY) {
                maxY = coords.y
            }
        })
        setHighest([maxX, maxY])
    }

    return (
        <QubitContext.Provider value={{ qubits, addQubit, removeQubit, resetQubits, findExtremes, highest }}>
            {children}
        </QubitContext.Provider>
    );
}
