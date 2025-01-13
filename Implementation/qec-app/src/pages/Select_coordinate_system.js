import React from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";

const Select_coordinate_system = () => {
  return (
    <div className = "main">
        <TopBanner title="Select the Co-ordinate System" description="Choose the underlying coordinate grid. This determines the location of the qubits you can select to be part of your circuit." />
        <NavigationButton label = "Next" destinationPage={"./Qubit_setup"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default Select_coordinate_system; 
