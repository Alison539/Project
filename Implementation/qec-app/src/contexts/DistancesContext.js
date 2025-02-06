import React, { createContext, useContext, useState } from "react";
import { QubitContext } from "./QubitContext";

export const DistancesContext = createContext();

export const DistancesProvider = ({ children }) => {
    const [distances, setDistances] = useState([]);
    const [ratio, setRatio] = useState(3)
    const { qubits } = useContext(QubitContext)

    const initialiseDistance = () => {
        let qubits_involved = []
        for (let index = 0; index < qubits.length; index++) {
            qubits_involved.push(index)
        }
        setDistances([[0, qubits_involved]])
    }

    const resetDistances = () => {
        setDistances([])
    }

    const addDistance = (distance) => {
        for (let i = 0; i < distances.length; i++) {
            if (distances[i][0] === distance) {
                return -1
            }
        }
        setDistances((previousDistances) => [...previousDistances, [distance, []]]);
        return distances.length
    }

    const removeDistance = (distanceid) => {
        setDistances((previousDistances) => previousDistances.filter((distance, index) => index !== distanceid))
    }

    const selectNewQubit = (distanceid, newQubit) => {
        setDistances((previousDistances) => previousDistances.map((distancePair, index) => {
            if (index === distanceid) {
                let newQubitsInvolved = []
                if (distancePair[1].includes(newQubit)) {
                    newQubitsInvolved = distancePair[1].filter((q) => q !== newQubit)
                }
                else {
                    newQubitsInvolved = [...distancePair[1], newQubit]
                }
                return [distancePair[0], newQubitsInvolved]
            }
            else {
                return distancePair
            }
        }))

    }

    return (
        <DistancesContext.Provider value={{ distances, initialiseDistance, resetDistances, addDistance, selectNewQubit, removeDistance, ratio, setRatio }}>
            {children}
        </DistancesContext.Provider>
    );
}
