import React, { useContext, useState } from "react";
import ConditionalNavigationButton from "../components/ConditionalNavigationButton";
import {useNavigate } from "react-router-dom";
import TopBanner from "../components/TopBanner";
import "../components/styles.css"
import hexagonal_tiling from "../resources/honeycomb-tiling.png";
import tetrakis_tiling from "../resources/tetrakis-tiling.png";
import octagon_square_tiling from "../resources/honeycomb-tiling.png";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";
import { QubitContext } from "../contexts/QubitContext";

function getCoordinateSystemDetails(index){
    switch(index) {
        case 1:
            return(<div>
                <img src = {hexagonal_tiling} width = "150px" alt = "Hexagonal Tiling"/>
                <p> Hexagonal Tiling</p>
            </div>);                        
        case 2:
            return(<div>
                <img src = {tetrakis_tiling} width = "150px" alt = "Tetrakis Tiling" />
                <p> Tetrakis Tiling</p>
            </div>);
        case 3:
            return(<div>
                <img src = {octagon_square_tiling} width = "150px" alt = "4-8-8 Tiling" />
                <p> 4-8-8 Tiling</p>
            </div>)
        default:
          return(<div></div>)
}}


const SelectCoordinateSystem = () => { 
  const {coordSys, setCoordSys, coordDimension, setCoordDimension} = useContext(CoordinateSystemContext)
  const {resetQubits} = useContext(QubitContext)
  const [selected, setSelected] = useState(coordSys);
  const [dimension, setDimension] = useState(coordDimension)
  const navigate = useNavigate();

  const handleNext = () => {
    const num = parseInt(dimension, 10);
    if (num >= 3 && num <= 25 && selected != null) {
        setCoordDimension(num);
        setCoordSys(selected)
        resetQubits()
        navigate("./Qubit_setup");
    }
    else {
        if (selected == null) {
            alert("Please select a coordinate system")
        }
        else{
            alert("Please choose a number between 3 and 25")
        }
    }
  }


  const handleDimensionInputChange = (e) => {
    setDimension(e.target.value);
  }

  const handleSelection = (index) => {
    setSelected(index)
  }

  return (
    <div className = "main">
        <TopBanner title="Select the Co-ordinate System" description="Choose the underlying coordinate grid. This determines the location of the qubits you can select to be part of your circuit." />
    <div style = {{display: "flex", justifyContent: "center", gap: "10px", marginTop: "20px"}}>
        {[1,2,3].map((index) => (
            <button
            key = {index}
            onClick = {() => handleSelection(index)}
            style = {{
              padding: "10px 20px",
              backgroundColor: selected === index ? "#668265" : "#89a888",
              color: "#2a363b",
              border: "1px solid #ccc",
              borderRadius: "5px",
              width: "300px",
              cursor: "pointer",
              height: "300px",
              fontSize: "20px"
            }}
            >
               {getCoordinateSystemDetails(index)}
            </button>
        ))}
    </div>
    <div style = {{display: "flex", justifyContent: "center", gap: "10px", marginTop: "20px"}}>
        <p> Dimension (between 3 and 25): </p>
        <input id="dimension" max = "25" min="3" value = {dimension} type="number" onChange={handleDimensionInputChange} />
    </div>
    <ConditionalNavigationButton label = "Next" checkAndNavigate={handleNext} position={{bottom: "20px", right: "20px"}}/>
        
    </div>
  );
}

    


export default SelectCoordinateSystem; 
