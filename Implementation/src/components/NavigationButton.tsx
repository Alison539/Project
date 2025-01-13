import React from "react";
import "./styles.css"
import { To, useNavigate } from "react-router-dom";

interface NavigationButtonProps {
  destinationPage: To;
  label: string;
  position: {bottom: string; right?: string; left?:string};
}

const NavigationButton = ({destinationPage, label, position}: NavigationButtonProps) => {
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
