import React, { useContext } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { DetailsContext } from "../contexts/DetailsContext";

const SetDetails = () => {
  const { numCycles, setNumCycles,
    singleGateDepolarization, setSingleGateDepolarization,
    twoGateDepolarization, setTwoGateDepolarization,
    measureFlipProbs, setMeasureFlipProbs,
    roundFlipProbs, setRoundFlipProbs,
    resetFlipProbs, setResetFlipProbs } = useContext(DetailsContext)

  return (
    <div className="main">
      <TopBanner title="Set The Details" description="Specify what the final details of your circuit are." />

      <div style = {{width: "60%", marginLeft:"20%"}}>
        <div className="menu-option">
          <h2>Noise: </h2>
          <div className="details-option">
            <p> After single-qubit gate depolarization: </p>
            <input className="details-input" id="singleGateDepolarization" step="0.001" max="1" min="0" value={singleGateDepolarization} type="number" onChange={(e) => { setSingleGateDepolarization(e.target.value) }} />
          </div>
          <div className="details-option">
            <p> After two-qubit gate depolarization: </p>
            <input className="details-input" id="twoGateDepolarization" step="0.001" max="1" min="0" value={twoGateDepolarization} type="number" onChange={(e) => { setTwoGateDepolarization(e.target.value) }} />
          </div>
          <div className="details-option">
            <p> Before measurement flip probability: </p>
            <input className="details-input" id="measureFlipProbs" step="0.001" max="1" min="0" value={measureFlipProbs} type="number" onChange={(e) => { setMeasureFlipProbs(e.target.value) }} />
          </div>
          <div className="details-option">
            <p> Before round data depolarization: </p>
            <input className="details-input" id="roundFlipProbs" step="0.001" max="1" min="0" value={roundFlipProbs} type="number" onChange={(e) => { setRoundFlipProbs(e.target.value) }} />
          </div>
          <div className="details-option">
            <p> After reset flip probability: </p>
            <input className="details-input" id="resetFlipProbs" step="0.001" max="1" min="0" value={resetFlipProbs} type="number" onChange={(e) => { setResetFlipProbs(e.target.value) }} />
            </div>
        </div>

        <div className="menu-option">
          <div className="details-option">
            <p> Number of times rounds are repeated: </p>
            <input className="details-input" id="repeats" max="1000" min="1" value={numCycles} type="number" onChange={(e) => { setNumCycles(e.target.value) }} />
          </div>
        </div>


      </div>

      <NavigationButton label="Previous" destinationPage={"/Rounds"} position={{ bottom: "20px", left: "20px" }} />
      <NavigationButton label="Next" destinationPage={"/Output_code"} position={{ bottom: "20px", right: "20px" }} />
    </div>
  );
};

export default SetDetails; 
