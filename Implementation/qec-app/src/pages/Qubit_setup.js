import React, { useContext } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";

const Qubit_setup = () => {
  const { coordSys, coordDimension} = useContext(CoordinateSystemContext);

  return (
    <div className = "main">
        <TopBanner title="Select the qubits" description="Select which qubits are part of your QEC circuit." />
        <p>Coordinate System: {coordSys}</p>
        <p>Dimension: {coordDimension}</p>
        <NavigationButton label = "Previous" destinationPage={"/"} position={{bottom: "20px", left: "20px"}}/>
        <NavigationButton label = "Next" destinationPage={"/Preround_operations"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default Qubit_setup; 
