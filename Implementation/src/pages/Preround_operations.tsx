import React from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";

const Preround_operations = () => {
  return (
    <div className = "main">
        <TopBanner title="Before Round Operations" description="These operations added are only done at the very start." />
        <NavigationButton label = "Previous" destinationPage={"./Qubit_setup"} position={{bottom: "20px", left: "20px"}}/>
        <NavigationButton label = "Next" destinationPage={"./Rounds"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default Preround_operations; 
