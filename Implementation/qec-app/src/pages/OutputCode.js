import React, { useContext } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { StimCodeContext } from "../contexts/StimCodeContext";

const OutputCode = () => {
  const {stimCode} = useContext(StimCodeContext);

  return (
    <div className="main">
      <TopBanner title="Your Code" description="Here is the Stim code for your QEC circuit" />
      <p>
        {stimCode}
      </p>
      <NavigationButton label = "Previous" destinationPage={"/Set_details"} position={{bottom: "20px", left: "20px"}}/>
    </div>
  );
};

export default OutputCode; 
