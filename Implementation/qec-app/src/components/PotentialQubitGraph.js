import React from "react";
import PotentialQubitButton from "./PotentialQubitButton";
import {max} from "mathjs";

const PotentialQubitGraph = ({ points, dimension, highestX,highestY }) => {
   
    const onClicked = (point) => {
        
    }

    const scaledPoints = points.map((point) => ({
        x: ((point.x - highestX/2) * (30 - dimension) * 2),
        y: ((point.y - highestY/2) * (30 - dimension) * 2),
    }))

  return (
    <div  style={{ position: "relative", width: "70%", height: "60vh", marginLeft:"10%", marginTop:"3%", border: "1px solid black", display: "flex", justifyContent: "center", alignItems:"center", padding: "3%" }}>
        <div style={{ position: "relative", alignSelf:"center"}}>
            {scaledPoints.map((point, index) => (
                <PotentialQubitButton key={index} index={index} point={point} onClicked={ onClicked(point)} qubitSize={ max(30 - (dimension), 4)} zIndex="1" qubitcolor="808080"/> 
            ))}
      </div>
    </div>
  );
};

export default PotentialQubitGraph;