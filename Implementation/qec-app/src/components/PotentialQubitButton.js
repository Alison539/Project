import React from "react";
import "./styles.css"

const PotentialQubitButton = ({point, onClicked, qubitSize, zIndex, qubitcolor, onClickedParameters, border, onHover}) => {
  return (
    <button
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
        cursor: "pointer",
        borderWidth:  `${border}px `,
        borderColor: "black",
        backgroundColor: `#${qubitcolor}`,
        }}
        onClick={() => onClicked(onClickedParameters)}
        onMouseEnter={() => 
          {if (onHover) {onHover(onClickedParameters)}}}
    />
  );
};

export default PotentialQubitButton; 


