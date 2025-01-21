import React, { useContext, useState } from "react";
import NavigationButton from "../components/NavigationButton";
import TopBanner from "../components/TopBanner";
import { OperationContext } from "../contexts/OperationContext";
import supportMessages from "../resources/supportMessages";
import QubitGraph from "../components/QubitGraph";

const Rounds = () => {
  const { deleteOperations, replicateQubitOps, setHadamard, setMeasurement, addTwoQubitOp } = useContext(OperationContext);

  const [currentOperation, setCurrentOperation] = useState(0);
  const [timeStep, setTimeStep] = useState(1);
  const [supportMessage, setSupportMessage] = useState("Choose an action to get started")
  const [controlQubit, setControlQubit] = useState(null)
  const [qubitToCopy, setQubitToCopy] = useState(null)

  const onSelectOperation = (operationID) => {
    setQubitToCopy(null)
    setCurrentOperation(operationID);
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
        if (qubitToCopy === null) {
          setQubitToCopy(qubitID);
        }
        else {
          replicateQubitOps(qubitToCopy, qubitID);
        }
        break;
      case 6:
        deleteOperations(qubitID);
        break;
      default:
        break;
    }
  }

  const incrementTime = () => {
    onSelectOperation(0)
    if (timeStep < 20) {
      setTimeStep(timeStep + 1);
    }
  }
  const decrementTime = () => {
    onSelectOperation(0)
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
              <li><button className="option-button" style={{ backgroundColor: currentOperation === 1 ? "#6aa768" : "#91e48e" }} onClick={() => onSelectOperation(1)}>H</button></li>
              <li><button className="option-button" style={{ backgroundColor: currentOperation === 2 ? "#915be7" : "#af8ee4" }} onClick={() => onSelectOperation(2)}> H_YZ</button></li>
              <li><button className="option-button" style={{ backgroundColor: currentOperation === 3 ? "#668265" : "#b5c9b4" }} onClick={() => onSelectOperation(3)}>CNOT</button></li>
              <li><button className="option-button" style={{ backgroundColor: currentOperation === 4 ? "#668265" : "#b5c9b4", borderWidth: "4px" }} onClick={() => onSelectOperation(4)}>MR</button></li>
            </ul>
          </div>
          <div className="centralised-menu-option">
            <p style={{ marginRight: "5px" }}>Current time step: {timeStep} </p>
            <button className="small-circular-button" onClick={decrementTime}>-</button>
            <button className="small-circular-button" onClick={incrementTime}>+</button>
          </div>
          <div className="centralised-menu-option">
            <button className="option-button" style={{ backgroundColor: currentOperation === 5 ? "#668265" : "#b5c9b4" }} onClick={() => onSelectOperation(5)} >Copy Operations</button>
          </div>
          <div className="centralised-menu-option">
            <button className="option-button" style={{ backgroundColor: currentOperation === 6 ? "#668265" : "#b5c9b4" }} onClick={() => onSelectOperation(6)}>Delete Operations</button>
          </div>
        </div>

        <div style={{width: "60%" }}>
          <div style={{ textAlign: "center", height: "15%" }}>
            {supportMessage}
          </div>
          <div>
            <QubitGraph onClicked={onClick} controlQubit={controlQubit} qubitToCopy = {qubitToCopy}/>
          </div>
        </div>

      </div>
      <NavigationButton label="Previous" destinationPage={"/Qubit_setup"} position={{ bottom: "20px", left: "20px" }} />
      <NavigationButton label="Next" destinationPage={"/Set_details"} position={{ bottom: "20px", right: "20px" }} />
    </div >
  );
};

export default Rounds; 
