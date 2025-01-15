import React, { useContext } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";
import {sin, sqrt} from "mathjs"
import PotentialQubitGraph from "../components/PotentialQubitGraph";

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
  return([qubitCoordinates, highestX,highestY]);
} 


const QubitSetup = () => {
  const { coordSys, coordDimension} = useContext(CoordinateSystemContext);

  const potentialQubitInformation = potentialQubitLocations(coordSys, coordDimension);

  return (
    <div className = "main">
        <TopBanner title="Select the qubits" description="Select which qubits are part of your QEC circuit." />
        <PotentialQubitGraph points={potentialQubitInformation[0]} dimension={coordDimension} highestX={potentialQubitInformation[1]} highestY={potentialQubitInformation[2]}/>
        <NavigationButton label = "Previous" destinationPage={"/"} position={{bottom: "20px", left: "20px"}}/>
        <NavigationButton label = "Next" destinationPage={"/Preround_operations"} position={{bottom: "20px", right: "20px"}}/>
    </div>
  );
};

export default QubitSetup; 
