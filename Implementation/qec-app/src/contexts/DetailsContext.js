import React, { createContext, useState } from "react";

export const DetailsContext = createContext();

export const DetailsProvider = ({ children }) => {
    const [numCycles, setNumCycles] = useState(3);
    
    const[singleGateDepolarization, setSingleGateDepolarization] = useState(0);
    const[twoGateDepolarization, setTwoGateDepolarization] = useState(0);
    const[measureFlipProbs, setMeasureFlipProbs] = useState(0)
    const[roundFlipProbs, setRoundFlipProbs] = useState(0)
    const[resetFlipProbs, setResetFlipProbs] = useState(0)
    

    return (
        <DetailsContext.Provider value={{ numCycles, setNumCycles, 
        singleGateDepolarization, setSingleGateDepolarization, 
        twoGateDepolarization, setTwoGateDepolarization, 
        measureFlipProbs, setMeasureFlipProbs, 
        roundFlipProbs, setRoundFlipProbs, 
        resetFlipProbs, setResetFlipProbs }}>
            {children}
        </DetailsContext.Provider>
    );
}
