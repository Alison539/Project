import React, { createContext, useState } from "react";

export const StimCodeContext = createContext();

export const StimCodeProvider = ({ children }) => {
    const [stimCode, setStimCode] = useState("undefined");

    return (
        <StimCodeContext.Provider value={{stimCode, setStimCode }}>
            {children}
        </StimCodeContext.Provider>
    );
}
