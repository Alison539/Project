import React, { createContext, useContext, useState } from "react";
import { CoordinateSystemContext } from "./CoordinateSystemContext";

export const QubitContext = createContext();

export class Qubit {
    constructor(coordinates, index) {
        this.location = coordinates;
        this.id = index;
        this.logical_observalble = false;
    }
    qubitFromCopy(qubit, newid) {
        this.location = qubit.getLocation();
        this.id = newid;
        this.logical_observalble = qubit.getLogicalObservable();
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
    setLogicalObservable() {
        this.logical_observalble = !this.logical_observalble;
    }
}

export const QubitProvider = ({ children }) => {
    const {coordsGivenCoordSys} = useContext(CoordinateSystemContext)

    const [qubits, setQubits] = useState([]);
    const [highestX, setHighestX] = useState(0);
    const [highestY, setHighestY] = useState(0);

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
    const findHighest = () => {
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
        setHighestX(maxX)
        setHighestY(maxY)
    }

    return (
        <QubitContext.Provider value={{ qubits, addQubit, removeQubit, resetQubits, setLogicalObservablePerQubit, findHighest, highestX, highestY }}>
            {children}
        </QubitContext.Provider>
    );
}
