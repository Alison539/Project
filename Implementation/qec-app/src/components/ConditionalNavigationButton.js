import React from "react";
import "./styles.css"

const ConditionalNavigationButton = ({checkAndNavigate, label, position}) => {
  return (
    <button 
    className="navigation-button"
    style =  {{ 
      position: "fixed",
      right: position.right,
      left: position.left,
      bottom: position.bottom
    }} onClick = {checkAndNavigate}>{label}</button>
  );
};

export default ConditionalNavigationButton; 
