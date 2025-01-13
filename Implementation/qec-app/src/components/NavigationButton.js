import React from "react";
import "./styles.css"
import {useNavigate } from "react-router-dom";

const NavigationButton = ({destinationPage, label, position}) => {
  const navigate = useNavigate();

  return (
    <button 
    className="navigation-button"
    style =  {{ 
      position: "fixed",
      right: position.right,
      left: position.left,
      bottom: position.bottom
    }} onClick = {() => navigate(destinationPage)}>{label}</button>
  );
};

export default NavigationButton; 
