import React, { createContext, useState } from "react";

export const GraphContext = createContext();

export const GraphProvider = ({ children }) => {

    const [noiseModel, setNoiseModel] = useState([1, 1, 1, 1, 1])
    const [noiseRange, setNoiseRange] = useState([0.01, 0.02]);
    const [step, setStep] = useState(0.002);

    const changeNoiseModel = (listIndex, newValue) => {
        setNoiseModel((previousNoiseModel) => {
            let newModel = [...previousNoiseModel];
            newModel[listIndex] = newValue;
            return newModel;
        })
    }
    const setNoiseRangeIndex = (newNoiseBound, index) => {
        let newNoiseRange = [...noiseRange];
        newNoiseRange[index] = newNoiseBound;
        setNoiseRange(newNoiseRange)
    }


    return (
        <GraphContext.Provider value={{ noiseModel, changeNoiseModel, noiseRange, setNoiseRangeIndex, step, setStep }}>
            {children}
        </GraphContext.Provider>
    );

}

