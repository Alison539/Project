import React, { useContext } from "react";
import axios from "axios"
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { DetailsContext } from "../contexts/DetailsContext";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";
import { OperationContext } from "../contexts/OperationContext";
import { StimCodeContext } from "../contexts/StimCodeContext";
import { useNavigate } from "react-router-dom";
import ConditionalNavigationButton from "../components/ConditionalNavigationButton";

function noiseName(index) {
  switch (index) {
    case 0:
      return ("After single-qubit gate depolarization:");
    case 1:
      return ("After two-qubit gate depolarization:");
    case 2:
      return ("Before measurement flip probability:");
    case 3:
      return ("Before round data depolarization:");
    case 4:
      return ("After reset flip probability:")
    default:
      break;
  }
}

const SetDetails = () => {
  const { numCycles, setNumCycles, noises, setNoiseIndex } = useContext(DetailsContext)
  const { coordSys } = useContext(CoordinateSystemContext)
  const { qubitOperations, twoQubitOperations } = useContext(OperationContext)
  const { setStimCode } = useContext(StimCodeContext)

  const navigate = useNavigate()

  const handleNoiseChange = (e, index) => {
    setNoiseIndex(parseFloat(e.target.value), index);
  }

  const handleNext = () => {
    let errorOccurred = false;
    noises.forEach((noise) => {
      if (noise < 0 || noise > 1) {
        if (!errorOccurred) {
          alert("Please make noise values between 0 and 1");
          errorOccurred = true;
        }
      }
    })
    if (!errorOccurred && (numCycles < 1 || numCycles > 1000)) {
      alert("Please choose a number of repetitions between 1 and 1000");
      errorOccurred = true;
    }
    if (!errorOccurred) {

      const payload = {
        coordSys: coordSys,
        qubitOperations: qubitOperations,
        twoQubitOperations: twoQubitOperations,
        noise: noises,
        numCycles: numCycles,
      };

      axios({
        url: "http://127.0.0.1:5000/api/qec_data",
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        data: JSON.stringify(payload),
      })
        .then((response) => {
          console.log(response.data)
          setStimCode(response.data.stimcode);
          navigate("/Output_code");
        })
        .catch((err) => { console.error("Error communicating with the backend:", err) })
    }
  }

  return (
    <div className="main">
      <TopBanner title="Set The Details" description="Specify what the final details of your circuit are." />

      <div style={{ width: "60%", marginLeft: "20%" }}>
        <div className="menu-option">
          <h2>Noise: </h2>
          {noises.map((noise, index) => (
            <div className="details-option">
              <p> {noiseName(index)} </p>
              <input className="details-input" key={index} step="0.001" max="1" min="0" value={noise} type="number" onChange={(e) => { handleNoiseChange(e, index) }} />
            </div>
          ))}
        </div>
        <div className="menu-option">
          <div className="details-option">
            <p> Number of times rounds are repeated: </p>
            <input className="details-input" id="repeats" max="1000" min="1" value={numCycles} type="number" onChange={(e) => { setNumCycles(parseInt(e.target.value)) }} />
          </div>
        </div>
      </div>

      <NavigationButton label="Previous" destinationPage={"/Rounds"} position={{ bottom: "20px", left: "20px" }} />
      <ConditionalNavigationButton label="Generate Stim Code" checkAndNavigate={handleNext} position={{ bottom: "20px", right: "20px" }} />
    </div>
  );
};

export default SetDetails; 
