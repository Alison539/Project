import React from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";

const SetDetails = () => {
  return (
    <div className = "main">
        <TopBanner title="Set The Details" description="Specify what the final details of your circuit are." />
        <NavigationButton label = "Previous" destinationPage={"/Postround_operations"} position={{bottom: "20px", left: "20px"}}/>
        <NavigationButton label = "Next" destinationPage={"/Output_code"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default SetDetails; 
