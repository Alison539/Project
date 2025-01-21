import React, { useContext, useEffect, useRef } from "react";
import OperationQubitButton from "./OperationQubitButton";
import {max} from "mathjs"
import { QubitContext } from "../contexts/QubitContext";
import { OperationContext } from "../contexts/OperationContext";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";

function drawCNOT(canvasRef, times, controlPoint, targetPoint) {

}

function calculateStartAndEnd(startQubit, endQubit) {

}

const QubitGraph = ({onClicked, controlQubit, qubitToCopy}) => {
  const {coordsGivenCoordSys} = useContext(CoordinateSystemContext)
  const {qubitOperations, twoQubitOperations} = useContext(OperationContext)
  const {highestX, highestY} = useContext(QubitContext);

  const canvasRef = useRef(null);
  const coordDimension = max(highestX + 1,highestY + 1)
  const qubitSize = max(30 - (coordDimension), 4)

  const canvasWidth = ((highestX*1.5) * (30 - coordDimension) * 2) + qubitSize*2;
  const canvasHeight = ((highestY) * (30 - coordDimension) * 2) + qubitSize*2;

  const scaleCoordinate = (point) => {
    const actualCoords = coordsGivenCoordSys(point)
    return({
      x: ((actualCoords.x + highestX/2) * (30 - coordDimension) * 2),
      y: ((actualCoords.y ) * (30 - coordDimension) * 2),
    })
  }
  

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const scaleCoordinate = (point) => {
      const actualCoords = coordsGivenCoordSys(point)
      return({
        x: ((actualCoords.x + (highestX/2)) * (30 - coordDimension) * 2) + qubitSize/2,
        y: ((actualCoords.y) * (30 - coordDimension) * 2) + qubitSize/2,
      })
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    twoQubitOperations.forEach((targets, cindex) => {
      targets.forEach((timesteps, tindex) => {
        if(timesteps.length > 0){
          const startPoint = scaleCoordinate(qubitOperations[cindex].getLocation())
          const endPoint = scaleCoordinate(qubitOperations[tindex].getLocation())
          if (startPoint && endPoint) {
            ctx.beginPath();
            ctx.moveTo(startPoint.x, startPoint.y);
            ctx.lineTo(endPoint.x, endPoint.y);
            ctx.lineWidth = "10px"; 
            ctx.stroke();
          }
        }
      })
    } );
  }, [qubitOperations, twoQubitOperations, coordDimension, highestX, highestY, qubitSize, coordsGivenCoordSys]);

  return (
    <div style={{ position: "relative"}}>
      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          zIndex: 0,
          width: `${canvasWidth}px`,
          height:`${canvasHeight}px`,
        }}
      />
      <div style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
        }}>
      {qubitOperations.map((qubit, index ) => (
        < OperationQubitButton key = {index} point={scaleCoordinate(qubit.getLocation())} onClicked = {onClicked} qubit = {qubit} amSelected = {qubit.getid() === qubitToCopy || qubit.getid() === controlQubit} qubitSize = {qubitSize} />
      ))}
      </div>
    </div>
  );
};

export default QubitGraph;