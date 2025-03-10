import React, { createContext, useState } from "react";

export const DetailsContext = createContext();

export const DetailsProvider = ({ children }) => {
    const [numCycles, setNumCycles] = useState(3);
    const [noises, setNoises] = useState([0,0,0,0,0])
    const [name, setName] = useState("");
    const [basis, setBasis] = useState(0)

    const setNoiseIndex = (newNoise, index) => {
        let newNoises = [...noises];
        newNoises[index] = newNoise;
        setNoises(newNoises)
    }
    
    return (
        <DetailsContext.Provider value={{ numCycles, setNumCycles, noises, setNoiseIndex, name, setName, basis, setBasis}}>
            {children}
        </DetailsContext.Provider>
    );
}
