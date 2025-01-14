import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Select_coordinate_system from "./pages/Select_coordinate_system";
import Qubit_setup from "./pages/Qubit_setup";
import Preround_operations from "./pages/Preround_operations";
import Rounds from "./pages/Rounds";
import Postround_operations from "./pages/Postround_operations";
import Set_details from "./pages/Set_details";
import Output_code from "./pages/Output_code";
import { CoordinateSystemProvider } from "./contexts/CoordinateSystemContext";

function App() {
  return (
    <CoordinateSystemProvider>
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
    </CoordinateSystemProvider>
  );
}

export default App;
