import React, { createContext, useState } from "react";
import {sin} from "mathjs"

export const CoordinateSystemContext = createContext();

export const CoordinateSystemProvider = ({ children }) => {
    const [coordSys, setCoordSys] = useState(null);
    const [coordDimension, setCoordDimension] = useState(undefined);

    const coordsGivenCoordSys = (point) => {
        let newX = point.x;
        let newY = point.y;
        if (coordSys === 1) {
            newX = newX + (newY % 2) * 0.5;
            newY = newY * sin(Math.PI / 3);
        }
        return ({x: newX, y: newY});

    }

    return (
        <CoordinateSystemContext.Provider value={{ coordSys, setCoordSys, coordDimension, setCoordDimension, coordsGivenCoordSys }}>
            {children}
        </CoordinateSystemContext.Provider>
    );
}
