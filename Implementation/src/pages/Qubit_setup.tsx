import React from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";

const Qubit_setup = () => {
  return (
    <div className = "main">
        <TopBanner title="Select the qubits" description="Select which qubits are part of your QEC circuit." />
        <NavigationButton label = "Previous" destinationPage={"./Select_coordinate_system"} position={{bottom: "20px", left: "20px"}}/>
        <NavigationButton label = "Next" destinationPage={"./Preround_operations"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default Qubit_setup; 
