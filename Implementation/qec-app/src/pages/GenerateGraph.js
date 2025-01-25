import React, { useContext, useState } from "react";
import axios from "axios"
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { DetailsContext } from "../contexts/DetailsContext";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";
import { OperationContext } from "../contexts/OperationContext";

const GenerateGraph = () => {
    const { numCycles, name, basis } = useContext(DetailsContext)
    const { coordSys } = useContext(CoordinateSystemContext)
    const { qubitOperations, twoQubitOperations } = useContext(OperationContext)
    
    const [graph, setGraph] = useState(undefined)
    const [noiseRange, setNoiseRange] = useState([0.01,0.1]);
    const [step, setStep] = useState(0.01);

    const setNoiseRangeIndex = (newNoiseBound, index) => {
        let newNoiseRange = [...noiseRange];
        newNoiseRange[index] = newNoiseBound;
        setNoiseRange(newNoiseRange)
    }

    const [isLoading, setIsLoading] = useState(false)

    const noiseBoundChange = (e, index) => {
        setNoiseRangeIndex(parseFloat(e.target.value), index)
    }

    const handleNext = () => {
        let errorOccurred = false;
        noiseRange.forEach((noise) => {
            if (noise < 0 || noise > 1) {
                if (!errorOccurred) {
                    alert("Please make noise bounds between 0 and 1");
                    errorOccurred = true;
                }
            }
        })
        if (errorOccurred) { return }
        if (noiseRange[0] > noiseRange[1]) {
            alert("Please ensure higher bound greater than lower bound");
            return;
        }
        else if (step < 0 || step > 1) {
            alert("Please make step between 0 and 1");
            return;
        }
        else if ((noiseRange[1] - noiseRange[0]) / step > 50) {
            alert("Step too small. Please ensure maximum 50 possible noise values.");
            return;
        }
        else {
            setIsLoading(true)
            const payload = {
                coordSys: coordSys,
                qubitOperations: qubitOperations,
                twoQubitOperations: twoQubitOperations,
                noiseRange: noiseRange,
                step: step,
                numCycles: numCycles,
                basis: basis,
                name: name,
            };
            axios({
                url: "http://127.0.0.1:5000/api/generate_graph",
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                data: JSON.stringify(payload),
            })
                .then((response) => {
                    setIsLoading(false)
                    console.log(response.data)
                    setGraph(response.data.graph);
                })
                .catch((err) => {
                    setIsLoading(false)
                    console.error("Error communicating with the backend:", err)
                })
        }
    }

    return (
        <div className="main">
            <TopBanner title="Generate a Graph" description="Generate a graph of logical error rate against physical error rate for your generate QEC code for a range of noise probabilities. PyMatching, a Minimum Weight Perfect Matching decoder, is used directly when generating the results. " />
            <div style={{ width: "60%", marginLeft: "20%" }}>
                <div className="menu-details-option">
                    <p>Noise Model:</p>
                    <p>Currently the probability of error shall be the same for all types of noise. </p>
                </div>
                <div className="menu-details-option">
                    <p className="no-space"> Range of probability of error to cover (inclusive): </p>
                    <div style={{ display: "flex" }}>
                        <input className="details-input" id="errorProbsLower" step="0.001" max="1" min="0" value={noiseRange[0]} type="number" onChange={(e) => { noiseBoundChange(e, 0) }} />
                        <p className="no-space" style={{ marginLeft: "5px", marginRight: "5px" }}> - </p>
                        <input className="details-input" id="errorProbsHigher" step="0.001" max="1" min="0" value={noiseRange[1]} type="number" onChange={(e) => { noiseBoundChange(e, 1) }} />

                    </div>
                </div>
                <div className="menu-details-option">
                    <p className="no-space"> Step between error probabilities: </p>
                    <input className="details-input" id="step" step="0.001" max="1" min="0" value={step} type="number" onChange={(e) => { setStep(parseFloat(e.target.value)) }} />
                </div>
            </div>
            <button className="navigation-button" onClick={handleNext} style={{ marginTop: "10px", marginLeft: "45%" }}>Generate Graph</button>
            {isLoading ?
                (<div className="loading">
                    <h2 style={{ marginLeft: "44%" }}>🌀 Loading...</h2>
                </div>)
                :
                (<div>
                    {graph ?
                        (<p> Graph being shown</p>)
                        : (<div></div>)
                    }
                </div>)

            }
            <NavigationButton label="Back" destinationPage={"/Output_code"} position={{ bottom: "20px", left: "20px" }} />
        </div>
    );
};

export default GenerateGraph; 
