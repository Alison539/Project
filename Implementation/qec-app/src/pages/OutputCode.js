import React, { useContext } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { StimCodeContext } from "../contexts/StimCodeContext";
import { useNavigate } from "react-router-dom";

const OutputCode = () => {
  const { stimCode } = useContext(StimCodeContext);
  const navigate = useNavigate();

  const copyCode = () => {
    navigator.clipboard.writeText(stimCode)
  }

  const onGenerateGraph = () => {
    navigate("/Generate_graph");
  }

  return (
    <div className="main">
      <TopBanner title="Your Code" description="Here is the Stim code for your QEC circuit" />
      <div className="code_container">
        <pre>
          {stimCode}
        </pre>
      </div>
      <div style={{display:"flex"}}>
        <button className="navigation-button" style={{ marginLeft: "25%"}} onClick={copyCode}>Copy Code</button>
        <button className="navigation-button" style={{ marginLeft: "30%"}} onClick={onGenerateGraph}>Generate Graph</button>
      </div>
      <NavigationButton label="Previous" destinationPage={"/Set_details"} position={{ bottom: "20px", left: "20px" }} />
    </div>
  );
};

export default OutputCode; 
