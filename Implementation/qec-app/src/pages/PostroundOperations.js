import React from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";

const PostroundOperations = () => {
  return (
    <div className = "main">
        <TopBanner title="After Round Operations" description="Now add the qubit operations that occur once the rounds are complete." />
        <NavigationButton label = "Previous" destinationPage={"/Rounds"} position={{bottom: "20px", left: "20px"}}/>
        <NavigationButton label = "Next" destinationPage={"/Set_details"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default PostroundOperations; 
