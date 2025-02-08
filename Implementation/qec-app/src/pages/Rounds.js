import React, { useContext, useState } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { OperationContext } from "../contexts/OperationContext";
import supportMessages from "../resources/supportMessages";
import QubitGraph from "../components/QubitGraph";
import QubitGateButton from "../components/QubitGateButton";

const Rounds = () => {
  const { deleteOperations, replicateQubitOps, setHadamard, setMeasurement, addTwoQubitOp, setLogicalObservable } = useContext(OperationContext);

  const [currentOperation, setCurrentOperation] = useState(0);
  const [timeStep, setTimeStep] = useState(1);
  const [supportMessage, setSupportMessage] = useState("Choose an action to get started")
  const [controlQubit, setControlQubit] = useState(null)
  const [qubitToCopy, setQubitToCopy] = useState(null)

  const onSelectOperation = (operationID) => {
    setQubitToCopy(null)
    setCurrentOperation(operationID);
    if (operationID !== 3) {
      setControlQubit(null)
    }
    setSupportMessage(supportMessages[operationID])
  }

  const onClick = (qubitID) => {
    switch (currentOperation) {
      case 1:
        setHadamard(qubitID, 1)
        break;
      case 2:
        setHadamard(qubitID, 2)
        break;
      case 3:
        if (controlQubit === null) {
          setControlQubit(qubitID)
        }
        else {
          addTwoQubitOp(controlQubit, qubitID, timeStep)
          setControlQubit(null)
        }
        break;
      case 4:
        setMeasurement(qubitID, 1);
        break;
      case 5:
        setMeasurement(qubitID, 2);
        break;
      case 6:
        setMeasurement(qubitID, 3);
        break;
      case 7:
        if (qubitToCopy === null) {
          setQubitToCopy(qubitID);
        }
        else {
          replicateQubitOps(qubitToCopy, qubitID);
        }
        break;
      case 8:
        deleteOperations(qubitID);
        break;
      case 9:
        setLogicalObservable(qubitID);
        break;
      default:
        break;
    }
  }

  const incrementTime = () => {
    if (timeStep < 20) {
      setTimeStep(timeStep + 1);
    }
  }
  const decrementTime = () => {
    if (timeStep > 1) {
      setTimeStep(timeStep - 1);
    }
  }

  return (
    <div className="main">
      <TopBanner title="Per-Round Operations" description="Now add the qubit operations that occur every round." />


      <div style={{ display: "flex", justifyContent: "center", gap: "10px", marginTop: "20px" }}>

        <div style={{ width: "20%" }}>
          <div className="menu-option">
            <p>Add qubit operations</p>
            <ul>
              {[1, 3, 4, 5].map((index) => (
                <li>
                  <QubitGateButton currentOperation={currentOperation} onSelectOperation={onSelectOperation} index={index} />
                </li>
              ))}
            </ul>
          </div>
          <div className="centralised-menu-option">
            <p style={{ marginRight: "5px" }}>Current time step: {timeStep} </p>
            <button className="small-circular-button" onClick={decrementTime}>-</button>
            <button className="small-circular-button" onClick={incrementTime}>+</button>
          </div>
          <div className="centralised-menu-option">
            <button className="option-button" style={{ backgroundColor: currentOperation === 7 ? "#668265" : "#b5c9b4" }} onClick={() => onSelectOperation(7)} >Copy Operations</button>
          </div>
          <div className="centralised-menu-option">
            <button className="option-button" style={{ backgroundColor: currentOperation === 8 ? "#668265" : "#b5c9b4" }} onClick={() => onSelectOperation(8)}>Delete Operations</button>
          </div>
          <div className="centralised-menu-option">
            <button className="option-button" style={{ backgroundColor: currentOperation === 9 ? "#668265" : "#b5c9b4", border: "4px dashed #000000" }} onClick={() => onSelectOperation(9)}>Add Logical Observable</button>
          </div>
        </div>

        <div style={{ width: "60%" }}>
          <div style={{ textAlign: "center", height: "15%" }}>
            {supportMessage}
          </div>
          <div>
            <QubitGraph onClicked={onClick} controlQubit={controlQubit} qubitToCopy={qubitToCopy} />
          </div>
        </div>

      </div>
      <NavigationButton label="Previous" destinationPage={"/Qubit_setup"} position={{ bottom: "20px", left: "20px" }} />
      <NavigationButton label="Next" destinationPage={"/Set_details"} position={{ bottom: "20px", right: "20px" }} />
    </div >
  );
};

export default Rounds; 
