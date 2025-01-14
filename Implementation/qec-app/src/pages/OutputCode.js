import React from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";

const OutputCode = () => {
  return (
    <div className="main">
      <TopBanner title="Your Code" description="Here is the Stim code for your QEC circuit" />
      <NavigationButton label = "Previous" destinationPage={"/Set_details"} position={{bottom: "20px", left: "20px"}}/>
    </div>
  );
};

export default OutputCode; 
