import React, { useContext } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { StimCodeContext } from "../contexts/StimCodeContext";

const OutputCode = () => {
  const { stimCode } = useContext(StimCodeContext);

  const copyCode = () => {
    navigator.clipboard.writeText(stimCode)
  }

  return (
    <div className="main">
      <TopBanner title="Your Code" description="Here is the Stim code for your QEC circuit" />
      <div className="code_container">
        <pre>
          {stimCode}
        </pre>
      </div>
      <button className="navigation-button" style={{ marginLeft: "45%"}} onClick={copyCode}>Copy Code</button>
      <NavigationButton label="Previous" destinationPage={"/Set_details"} position={{ bottom: "20px", left: "20px" }} />
    </div>
  );
};

export default OutputCode; 
