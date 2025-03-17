import React, { useContext, useState } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";
import { sin, sqrt, max } from "mathjs"
import { QubitContext } from "../contexts/QubitContext";
import PotentialQubitButton from "../components/PotentialQubitButton";
import { useNavigate } from "react-router-dom";
import ConditionalNavigationButton from "../components/ConditionalNavigationButton";
import { OperationContext } from "../contexts/OperationContext";

function potentialQubitLocations(coordSys, coordDimension) {
  const qubitCoordinates = [];
  let highestX = 0;
  let highestY = 0;
  switch (coordSys) {
    case 1: //Hexagonal Tiling
      for (let x = 0; x < coordDimension; x++) {
        for (let y = 0; y < coordDimension; y++) {
          qubitCoordinates.push({ x: x, y: y })
        }
      }
      highestX = coordDimension - 1;
      highestY = (coordDimension - 1) * sin(Math.PI / 3);
      break;
    case 2: //Tetrakis Tiling
      for (let x = 0; x < coordDimension; x++) {
        for (let y = 0; y < coordDimension; y++) {
          qubitCoordinates.push({ x: x, y: y })
        }
      }
      highestX = coordDimension - 1;
      highestY = coordDimension - 1;
      break;
    case 3: //4-8-8 Tiling
      const rootHalf = sqrt(0.5)
      for (let y = 0; y < coordDimension * 1.5; y++) {
        const newY = y * rootHalf;
        let newX = 0;
        if (y % 3 === 1) {
          newX = -0.5 - rootHalf;
        }
        else if (y % 6 > 2) {
          newX = 1 + rootHalf;
        }
        for (let x = 0; x < coordDimension * 0.7; x++) {
          if (y % 3 === 1) {
            newX += (1 + rootHalf);
          }
          else {
            if (x !== 0 && x % 2 === 0) {
              newX += 1 + (2 * rootHalf);
            }
            newX += (x % 2 * 1)
          }
          qubitCoordinates.push({ x: newX, y: newY })
        }
      }
      highestX = coordDimension * 0.7 * (1 + rootHalf);
      highestY = coordDimension * 1.5 * rootHalf;
      break;
    default:
      break;
  }
  return [qubitCoordinates, highestX, highestY];
}


const QubitSetup = () => {
  const { coordSys, coordDimension, coordsGivenCoordSys } = useContext(CoordinateSystemContext);
  const { qubits, addQubit, removeQubit, findExtremes } = useContext(QubitContext)
  const { instantiate } = useContext(OperationContext)

  const navigate = useNavigate();

  const potentialQubitsInformation = potentialQubitLocations(coordSys, coordDimension);
  const potentialQubits = potentialQubitsInformation[0]
  const highestX = potentialQubitsInformation[1]
  const highestY = potentialQubitsInformation[2]

  const [hoverSelect, setHoverSelect] = useState(false)

  const onPotentialClicked = (parameters) => {
    addQubit(parameters[0], parameters[1]);
  }

  const onHover = (parameters) => {
    if (hoverSelect) {
      addQubit(parameters[0], parameters[1])
    }
  }

  const onSelectedClicked = (qubit) => {
    removeQubit(qubit);
  }

  const scaleCoordinate = (point) => {
    const actualCoords = coordsGivenCoordSys(point)
    return ({
      x: ((actualCoords.x - highestX / 2) * (35 - coordDimension) * 1.5),
      y: ((actualCoords.y - highestY / 2) * (35 - coordDimension) * 1.5),
    })
  }

  const handleHoverSelect = () => {
    setHoverSelect(!hoverSelect)
  }

  const qubitSize = max(30 - (coordDimension), 4)

  const handleNext = () => {
    findExtremes();
    instantiate();
    navigate("/Rounds");
  }

  return (
    <div className="main">
      <TopBanner title="Select the qubits" description="Select which qubits are part of your QEC circuit." />

      <div style={{ position: "relative", width: "70%", height: "60vh", marginLeft: "10%", marginTop: "3%", border: "1px solid black", display: "flex", justifyContent: "center", alignItems: "center", padding: "3%" }}>
        <div style={{ position: "relative", alignSelf: "center" }}>
          {potentialQubits.map((point, index) => (
            <PotentialQubitButton key={index} point={scaleCoordinate(point)} onClickedParameters={[point, index]} onClicked={onPotentialClicked} border={1} qubitSize={qubitSize} zIndex="1" qubitcolor="808080" onHover={onHover} />
          ))}
          {qubits.map((qubit, index) => (
            <PotentialQubitButton key={index} point={scaleCoordinate(qubit.getLocation())} onClickedParameters={qubit} onClicked={onSelectedClicked} border={1} qubitSize={qubitSize} zIndex="2" qubitcolor="E84A5F" />
          ))}
        </div>
        <button className="navigation-button"
          style={{
            position: "absolute",
            left: "0px",
            bottom: "0px",
            backgroundColor: hoverSelect ? "#668265" : "#89a888",
          }}
          onClick={handleHoverSelect} >
          Hover over qubits to select (otherwise click individually)
        </button>
      </div>
      <NavigationButton label="Previous" destinationPage={"/"} position={{ bottom: "20px", left: "20px" }} />
      <ConditionalNavigationButton label="Next" checkAndNavigate={handleNext} position={{ bottom: "20px", right: "20px" }} />
    </div>
  );
};

export default QubitSetup; 
