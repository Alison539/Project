import React, { useEffect, useRef } from "react";
import PotentialQubitButton from "./PotentialQubitButton";

function drawCNOT(canvasRef, times, controlPoint, targetPoint) {

}

function calculateStartAndEnd(startQubit, endQubit) {

}

const QubitGraph = ({ points, connections, dimension, lineColour }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const onClicked = (point) => {
        
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    connections.forEach(([startIndex, endIndex]) => {
      const startPoint = points[startIndex];
      const endPoint = points[endIndex];
      if (startPoint && endPoint) {
        ctx.beginPath();
        ctx.moveTo(startPoint.x, startPoint.y);
        ctx.lineTo(endPoint.x, endPoint.y);
        ctx.strokeStyle = {lineColour};
        ctx.lineWidth = max(5 - ({dimension}/2), 2); 
        ctx.stroke();
      }
    });
  }, [points, connections]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <canvas
        ref={canvasRef}
        width={window.innerWidth}
        height={window.innerHeight}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          zIndex: 0,
        }}
      />
      {points.map((point, index) => (
        PotentialQubitButton(index = index,point = point,onClicked = onClicked(point),size = max(8 - ({dimension}/2), 4))
      ))}
    </div>
  );
};

export default QubitGraph;