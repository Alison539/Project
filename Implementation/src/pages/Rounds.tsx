import React from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";

const Rounds = () => {
  return (
    <div className = "main">
        <TopBanner title="Per-Round Operations" description="Now add the qubit operations that occur every round." />
        <NavigationButton label = "Previous" destinationPage={"./Preround_operations"} position={{bottom: "20px", left: "20px"}}/>
        <NavigationButton label = "Next" destinationPage={"./Postround_operations"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default Rounds; 
