import React from "react";
import "./styles.css"

const PotentialQubitButton = ({index, point, onClicked, qubitSize, zIndex, qubitcolor}) => {

  return (
    <button
        key={index}
        style={{
        position: "absolute",
        left: `${point.x}px`,
        top: `${point.y}px`,
        zIndex: {zIndex},
        minWidth: `${qubitSize}px`,
        minHeight: `${qubitSize}px `,
        borderRadius: "50%",
        boxSizing: "border-box",
        padding: 0,
        margin: 0,
        backgroundColor: `#${qubitcolor}`,
        }}
        onClick={onClicked}
    />
  );
};

export default PotentialQubitButton; 


