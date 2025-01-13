import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Select_coordinate_system from "./pages/Select_coordinate_system";
import Qubit_setup from "./pages/Qubit_setup";
import Preround_operations from "./pages/Preround_operations";
import Rounds from "./pages/Rounds";
import Postround_operations from "./pages/Postround_operations";
import Set_details from "./pages/Set_details";
import Output_code from "./pages/Output_code";

function App() {

  /*
  const [circuit, setCircuit] = useState("");  // User input
  const [stimCode, setStimCode] = useState("");  // Response from backend

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/convert", { circuit });
      setStimCode(response.data.stim_code);  // Set the Stim code response
    } catch (error) {
      console.error("Error communicating with the backend:", error);
    }
  };

  returm()
  <div style={{ padding: "20px" }}>
      <h1>Quantum Circuit to Stim Code Converter</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={circuit}
          onChange={(e) => setCircuit(e.target.value)}
          placeholder="Draw or describe your quantum circuit"
          rows={5}
          cols={50}
        />
        <br />
        <button type="submit">Convert to Stim Code</button>
      </form>
      {stimCode && (
        <div style={{ marginTop: "20px", border: "1px solid #ccc", padding: "10px" }}>
          <h3>Generated Stim Code:</h3>
          <pre>{stimCode}</pre>
        </div>
      )}
    </div>
  */

  return (
    <div className="main">
      <Router>
    <Routes>
      <Route path="/" element={<Select_coordinate_system />} />
      <Route path="/qubit_setup" element={<Qubit_setup />} />
      <Route path="/preround_operations" element={<Preround_operations />} />
      <Route path="/rounds" element={<Rounds />} />
      <Route path="/postround_operations" element={<Postround_operations />} />
      <Route path="/set_details" element={<Set_details />} />
      <Route path="/output_code" element={<Output_code />} />
    </Routes>
    </Router>

    </div>
  );
}

export default App;
