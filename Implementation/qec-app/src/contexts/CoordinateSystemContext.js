import React, { createContext, useState} from "react";

export const CoordinateSystemContext = createContext();

export const CoordinateSystemProvider = ({ children }) => {
    const [coordSys, setCoordSys] = useState(null);
    const [coordDimension, setCoordDimension] = useState(undefined);

    return(
        <CoordinateSystemContext.Provider value={{coordSys, setCoordSys, coordDimension, setCoordDimension}}>
            {children}
        </CoordinateSystemContext.Provider>
    );
}
