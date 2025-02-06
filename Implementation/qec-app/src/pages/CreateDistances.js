import React, { useContext, useState } from "react";
import TopBanner from "../components/TopBanner";
import { DistancesContext } from "../contexts/DistancesContext";
import ConditionalNavigationButton from "../components/ConditionalNavigationButton";
import { useNavigate } from "react-router-dom";
import QubitGraph from "../components/QubitGraph";

const CreateDistances = () => {
    const { distances, initialiseDistance, addDistance, selectNewQubit, removeDistance, ratio, setRatio } = useContext(DistancesContext)

    const navigate = useNavigate()

    const [selectedDistance, setSelectedDistance] = useState(undefined)
    const [newDistance, setNewDistance] = useState(3)
    const [hoverSelect, setHoverSelect] = useState(false)

    const addNewDistance = () => {
        if (newDistance > 0) {
            const new_distance_id = addDistance(newDistance)
            if (new_distance_id === -1) {
                alert("Please select distinct distance values")
            }
            else {
                setSelectedDistance(new_distance_id)
                setNewDistance(NaN)
            }
        }
        else {
            alert("Please define a distance value greater than zero before adding")
        }
    }

    const handleBack = () => {
        if (ratio <= 0 || ratio > 10000) {
            alert("Please choose a ratio between 0 and 10000");
        }
        else {
            if (distances.length === 0) {
                initialiseDistance()
            }
            navigate("/Generate_graph");
        }
    }

    const deleteDistance = (distance_index) => {
        removeDistance(distance_index)
        setSelectedDistance(undefined)
    }

    const selectDistance = (distance_index) => {
        setSelectedDistance(distance_index)
    }

    const getColour = (index) => {
        return (index === selectedDistance ? "#668265" : "#b5c9b4")
    }

    const onClick = (qubitID) => {
        selectNewQubit(selectedDistance, qubitID)
    }

    const onHover = (qubitID) => {
        if (hoverSelect) {
            selectNewQubit(selectedDistance, qubitID)
        }
    }

    const handleHoverSelect = () => {
        setHoverSelect(!hoverSelect)
    }

    return (
        <div className="main">
            <TopBanner title="Add Distances to Graph" description="Create subsets of qubits which correspond to different distances" />

            <div style={{ display: "flex", justifyContent: "center", gap: "10px", marginTop: "20px" }}>

                <div style={{ width: "20%" }}>

                    <div className="menu-details-option">
                        <p className="no-space"> Number of rounds relative to distance: </p>
                        <input className="details-input" value={ratio} id="round_ratio" type="number" onChange={(e) => { setRatio(parseFloat(e.target.value)) }} />
                    </div>

                    <div className="menu-option">

                        {distances.map((distance, index) => (
                            <div className="details-option">
                                <button className="option-button" onClick={() => selectDistance(index)} style={{ backgroundColor: getColour(index) }}> Distance: {distance[0]} </button>
                                <button className="small-circular-button" onClick={() => deleteDistance(index)}>-</button>
                            </div>
                        ))}
                        <div>
                            <p className="no-space"> New Distance: </p>
                            <div className="details-option">
                                <input className="details-input" id="new_distance" type="number" value={newDistance} onChange={(e) => { setNewDistance(parseInt(e.target.value)) }} />
                                <button className="small-circular-button" onClick={addNewDistance}>Add</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div style={{ width: "60%" }}>
                    <div style={{ textAlign: "center", height: "15%" }}>
                        <p>Add a distance value and then select the subset of qubits involved for that distance value</p>
                    </div>
                    <div>
                        <QubitGraph onClicked={onClick} controlQubit={null} qubitToCopy={null} selected_distance_id={selectedDistance} onHover={onHover} />
                    </div>

                </div>
                <button className="navigation-button"
                    style={{
                        position: "absolute",
                        left: "5%",
                        bottom: "60px",
                        backgroundColor: hoverSelect ? "#668265" : "#89a888",
                    }}
                    onClick={handleHoverSelect} >
                    Hover over qubits to select (o/w click individually)
                </button>
            </div>
            <ConditionalNavigationButton label="Generate Graph" checkAndNavigate={handleBack} position={{ bottom: "20px", left: "20px" }} />
        </div >
    )

};

export default CreateDistances; 
