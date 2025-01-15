import React, { useCallback, useContext, useState } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";
import {sin, sqrt,max} from "mathjs"
import { QubitContext } from "../contexts/QubitContext";
import PotentialQubitButton from "../components/PotentialQubitButton";
import { useNavigate } from "react-router-dom";
import ConditionalNavigationButton from "../components/ConditionalNavigationButton";

function potentialQubitLocations(coordSys, coordDimension) {
  const qubitCoordinates = [];
  let highestX = 0;
  let highestY = 0;
  switch(coordSys){
    case 1: //Hexagonal Tiling
      for (let x = 0; x < coordDimension; x++) {
        for (let y = 0; y < coordDimension; y++) {
          let newX = x + (y % 2) * 0.5
          let newY = y * sin(Math.PI / 3)
          qubitCoordinates.push({x: newX,y: newY})
        }     
      }
      highestX = coordDimension - 1;
      highestY = (coordDimension - 1)  * sin(Math.PI / 3);
      break;
    case 2: //Tetrakis Tiling
      for (let x = 0; x < coordDimension; x++) {
        for (let y = 0; y < coordDimension; y++) {
          qubitCoordinates.push({x: x,y: y})
        }     
      }
      highestX = coordDimension - 1;
      highestY = coordDimension - 1;
      break;
    case 3: //4-8-8 Tiling
      const rootHalf = sqrt(0.5)
      for (let y = 0; y < coordDimension*1.5; y++) {
        const newY = y * rootHalf;
        let newX = 0;
        if (y%3 === 1){
          newX = -0.5 - rootHalf;
        }
        else if (y%6 > 2){
            newX = 1 + rootHalf;
          }
        for (let x = 0; x < coordDimension*0.7; x++) {
            if (y%3 === 1){
              newX += (1 + rootHalf);
            }
            else{
              if (x !== 0 && x%2 === 0){
                newX += 1 + (2*rootHalf);
              }
              newX += (x%2 * 1)
            }
            qubitCoordinates.push({x: newX,y: newY})
          }     
      }
      highestX = coordDimension*0.7*(1 + rootHalf);
      highestY = coordDimension * 1.5 * rootHalf;
      break;
    default:
      break;
  }
  return[qubitCoordinates, highestX,highestY];
} 


const QubitSetup = () => {
  const { coordSys, coordDimension} = useContext(CoordinateSystemContext);
  const {qubits, addQubit, removeQubit, setLogicalObservablePerQubit, makeIdsConsecutive} = useContext(QubitContext)

  const navigate = useNavigate();

  const potentialQubitsInformation = potentialQubitLocations(coordSys, coordDimension);
  const potentialQubits = potentialQubitsInformation[0]
  const highestX = potentialQubitsInformation[1]
  const highestY = potentialQubitsInformation[2]

  const [selectingLogicalObservable, setSelectingLogicalObservable] = useState(false)

  const onPotentialClicked = useCallback(parameters => {
    if (!selectingLogicalObservable){
      addQubit(parameters[0],parameters[1]);
    }
  },[addQubit, selectingLogicalObservable])

  const onSelectedClicked = useCallback((qubit) => {
    if (selectingLogicalObservable){
      setLogicalObservablePerQubit(qubit)
    }
    else{
      removeQubit(qubit);
    }
  },[removeQubit, selectingLogicalObservable,setLogicalObservablePerQubit])

  const scaleCoordinate = (point) => {
    return({
      x: ((point.x - highestX/2) * (30 - coordDimension) * 2),
      y: ((point.y - highestY/2) * (30 - coordDimension) * 2),
    })
  }

  const handleLogicalObservable = () => {
    setSelectingLogicalObservable( !selectingLogicalObservable);
  }

  const qubitSize = max(30 - (coordDimension), 4)

  const determineBorderWidth = (qubit) => {
    if (qubit.getLogicalObservable()){
      return (qubitSize/8) + 1;
    }
    else{
      return 0;
    }
  }

  const handleNext = () => {
    makeIdsConsecutive()
    navigate("/Preround_operations");
  }

  

  return (
    <div className = "main">
        <TopBanner title="Select the qubits" description="Select which qubits are part of your QEC circuit." />

        <div  style={{ position: "relative", width: "70%", height: "60vh", marginLeft:"10%", marginTop:"3%", border: "1px solid black", display: "flex", justifyContent: "center", alignItems:"center", padding: "3%" }}>
            <div style={{ position: "relative", alignSelf:"center"}}>
                {potentialQubits.map((point, index) => (
                    <PotentialQubitButton key={index} point={scaleCoordinate(point)} onClickedParameters = {[point,index]} onClicked={ onPotentialClicked} border = {0} qubitSize={qubitSize} zIndex="1" qubitcolor="808080"/> 
                ))}
                {qubits.map((qubit, index) => (
                    <PotentialQubitButton key={index}  point={scaleCoordinate(qubit.getLocation())} onClickedParameters = {qubit} onClicked={ onSelectedClicked} border = {determineBorderWidth(qubit)} qubitSize={qubitSize} zIndex="2" qubitcolor="E84A5F"/> 
                ))}
          </div>
          <button className="navigation-button"
    style =  {{ 
      position: "absolute",
      right: "0px",
      bottom: "0px",
      backgroundColor: selectingLogicalObservable ? "#668265" : "#89a888",
    }}
    onClick={handleLogicalObservable} >
            Select the qubits part of the logical observable
          </button>
        </div>
        <NavigationButton label = "Previous" destinationPage={"/"} position={{bottom: "20px", left: "20px"}}/>
        <ConditionalNavigationButton label = "Next" checkAndNavigate={handleNext} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default QubitSetup; 
