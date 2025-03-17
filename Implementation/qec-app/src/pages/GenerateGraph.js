import React, { useContext, useState } from "react";
import axios from "axios"
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { DetailsContext } from "../contexts/DetailsContext";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";
import { OperationContext } from "../contexts/OperationContext";
import { DistancesContext } from "../contexts/DistancesContext";
import ConditionalNavigationButton from "../components/ConditionalNavigationButton";
import { useNavigate } from "react-router-dom";
import { GraphContext } from "../contexts/GraphContext";
import noiseName from "../resources/noiseDescriptions";

const GenerateGraph = () => {
    const { numCycles, name, basis } = useContext(DetailsContext)
    const { coordSys } = useContext(CoordinateSystemContext)
    const { qubitOperations, twoQubitOperations } = useContext(OperationContext)
    const { distances, resetDistances, ratio } = useContext(DistancesContext)
    const { noiseModel, changeNoiseModel, noiseRange, setNoiseRangeIndex, step, setStep, decoder, setDecoder } = useContext(GraphContext)

    const [graphURL, setGraphURL] = useState("");
    const navigate = useNavigate()

    const [isLoading, setIsLoading] = useState(false)
    const [threshold, setThreshold] = useState(null)

    const noiseRangeChange = (e, index) => {
        const newProportion = parseFloat(e.target.value)
        if (newProportion < 0 || newProportion > 1) {
            alert("Proportion value has to be between 0 and 1")
        }
        else {
            changeNoiseModel(index, newProportion)
        }

    }

    const noiseBoundChange = (e, index) => {
        setNoiseRangeIndex(parseFloat(e.target.value), index)
    }

    const handleAddDistances = () => {
        if (distances.length === 1) {
            resetDistances()
        }
        navigate("/add_distances");

    }

    const onGenerate = () => {
        let errorOccurred = false;
        noiseModel.forEach((noise) => {
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
                noiseModel: noiseModel,
                ratio: ratio,
                step: step,
                numCycles: numCycles,
                distances: distances,
                basis: basis,
                name: name,
                decoder: decoder,
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
                    setIsLoading(false);
                    console.log(response.data);
                    setGraphURL(response.data.url);
                    setThreshold(response.data.threshold);
                })
                .catch((error) => {
                    setIsLoading(false)
                    alert("Error communicating with the backend:", error)
                })
        }
    }

    return (
        <div className="main">
            <TopBanner title="Generate a Graph" description="Generate a graph of logical error rate against physical error rate for your generate QEC code for a range of noise probabilities." />
            <div style={{ width: "60%", marginLeft: "20%" }}>
                <p className="title-no-space">Noise Model: </p>
                <p className="no-space"> Fraction of the error value. All 1s mean all have the same error value.</p>
                <div className="menu-details-option" style={{ marginTop: '0' }}>
                    {noiseModel.map((noise, index) => (
                        <div style={{ flex_direction: 'column', float: 'left' }}>
                            <p> {noiseName(index)} </p>
                            <input className="details-input" key={index} step="0.001" max="1" min="0" value={noise} type="number" onChange={(e) => { noiseRangeChange(e, index) }} />
                        </div>
                    ))}
                </div>
                <div className="menu-details-option">
                    <p className="no-space"> Range of probability of error to cover: </p>
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
                <div className="menu-details-option">
                    <p> Decoder to use: </p>
                    <div style={{ flex_direction: 'column', float: 'left' }}>
                        <form style={{}}>
                            <div>
                                <input name="basis" type="radio" value="MWPM" id="MWPM" checked={decoder === 0 ? "checked" : null} onClick={() => setDecoder(0)} />
                                <label for="MWPM">Minimum Weight Perfect Matching (using PyMatching) </label>
                            </div>
                            <div>
                                <input name="basis" type="radio" value="UF" id="UF" checked={decoder === 1 ? "checked" : null} onClick={() => setDecoder(1)} />
                                <label for="UF">Union-Find</label>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            <button className="navigation-button" onClick={onGenerate} style={{ marginTop: "10px", marginLeft: "45%" }}>Generate Graph</button>
            {
                isLoading ?
                    (<div className="loading">
                        <h2 style={{ marginLeft: "44%" }}>🌀 Loading...</h2>
                    </div>)
                    :
                    (<div>
                        {graphURL &&
                            <img src={graphURL} alt="Generated Graph" width="60%" style={{ marginLeft: "20%", marginTop: "15px" }} />
                        }
                        {threshold &&
                            <div className="centralised-menu-option">
                                <p>Threshold: {threshold} </p>
                            </div>}
                    </div>)
            }
            <NavigationButton label="Back" destinationPage={"/Output_code"} position={{ bottom: "20px", left: "20px" }} />
            <ConditionalNavigationButton label="Add Different Distances" checkAndNavigate={handleAddDistances} position={{ bottom: "20px", right: "20px" }} />
        </div >
    );
};

export default GenerateGraph; 
