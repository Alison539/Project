import React, { useContext, useEffect, useRef } from "react";
import OperationQubitButton from "./OperationQubitButton";
import { max, sqrt } from "mathjs"
import { QubitContext } from "../contexts/QubitContext";
import { OperationContext } from "../contexts/OperationContext";
import { CoordinateSystemContext } from "../contexts/CoordinateSystemContext";

const QubitGraph = ({ onClicked, controlQubit, qubitToCopy }) => {
  const { coordsGivenCoordSys } = useContext(CoordinateSystemContext)
  const { qubitOperations, twoQubitOperations } = useContext(OperationContext)
  const { highest} = useContext(QubitContext);

  const canvasRef = useRef(null);
  const coordDimension = max(highest[0] + 1, highest[1] + 1)
  const qubitSize = max(30 - (coordDimension), 4)

  const canvasWidth = ((highest[0] * 1.5) * (30 - highest[0]) * 2) + qubitSize * 2;
  const canvasHeight = ((highest[1]) * (30 - highest[1]) * 2) + qubitSize * 2;

  const scaleCoordinate = (point) => {
    const actualCoords = coordsGivenCoordSys(point)
    return ({
      x: ((actualCoords.x + highest[0] / 9) * (30 - highest[0]) * 2),
      y: ((actualCoords.y) * (30 - highest[1]) * 2),
    })
  }


  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    function calculateStartAndEnd(startpoint, endpoint) {
      function scaleLineCoords(point) {
        const actualCoords = coordsGivenCoordSys(point)
        return ({
          x: ((actualCoords.x + (highest[0] / 9)) * (30 - highest[0]) * 2) + qubitSize / 2,
          y: ((actualCoords.y) * (30 - highest[1]) * 2) + qubitSize / 2,
        })
      }

      const separation = qubitSize/40;
      const proportionalLength = 0.6;
      const control = scaleLineCoords(startpoint);
      const target = scaleLineCoords(endpoint);

      const dx = target.x - control.x
      const dy = target.y - control.y

      const length = sqrt(((target.x - control.x)**2) + ((target.y - control.y)**2))

      const udx = dx / length
      const udy =  dy / length

      const controlPoint = {
        x: control.x + (udy * separation) + (dx*((1-proportionalLength)/2)),
        y: control.y - (udx * separation) + (dy*((1-proportionalLength)/2)),
      }
      const targetPoint = {
        x: controlPoint.x + (dx * proportionalLength),
        y: controlPoint.y + (dy * proportionalLength)
      }

      return ([controlPoint, targetPoint])
    }

    function drawCNOTTarget(x, y, radius, angle) {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);

      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, 2 * Math.PI);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(0, - radius);
      ctx.lineTo(0, + radius);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(- radius, 0);
      ctx.lineTo(+ radius, 0);
      ctx.stroke();

      ctx.restore();
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    twoQubitOperations.forEach((targets, cindex) => {
      targets.forEach((timesteps, tindex) => {
        if (timesteps.length > 0) {
          const points = calculateStartAndEnd(qubitOperations[cindex].getLocation(), qubitOperations[tindex].getLocation())
          const startPoint = points[0]
          const endPoint = points[1]
          if (startPoint && endPoint) {
            ctx.beginPath();
            ctx.moveTo(startPoint.x, startPoint.y);
            ctx.lineTo(endPoint.x, endPoint.y);
            ctx.lineWidth = "10px";
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(startPoint.x, startPoint.y, qubitSize / 8, 0, 2 * Math.PI);
            ctx.fillStyle = "black";
            ctx.fill();

            const lineAngle = Math.atan2(endPoint.y - startPoint.y, endPoint.x - startPoint.x)

            drawCNOTTarget(endPoint.x, endPoint.y, qubitSize / 4, lineAngle)

            const midpointX = (endPoint.x + startPoint.x) / 2
            const midpointY = (endPoint.y + startPoint.y) / 2

            ctx.save();
            ctx.translate(midpointX, midpointY);
            ctx.rotate(lineAngle);

            ctx.font = `${14 - timesteps.length}px Arial`;
            ctx.textAlign = 'center';

            ctx.fillText(timesteps, 0, -3)
            ctx.restore();
          }
        }
      })
    });
  }, [qubitOperations, twoQubitOperations, highest, qubitSize, coordsGivenCoordSys]);

  return (
    <div style={{ position: "relative" }}>
      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          zIndex: 0,
        }}
      />
      <div style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
      }}>
        {qubitOperations.map((qubit, index) => (
          < OperationQubitButton key={index} point={scaleCoordinate(qubit.getLocation())} onClicked={onClicked} qubit={qubit} amSelected={qubit.getid() === qubitToCopy || qubit.getid() === controlQubit} qubitSize={qubitSize} />
        ))}
      </div>
    </div>
  );
};

export default QubitGraph;