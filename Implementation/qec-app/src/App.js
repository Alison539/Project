import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SelectCoordinateSystem from "./pages/SelectCoordinateSystem";
import QubitSetup from "./pages/QubitSetup";
import PreroundOperations from "./pages/PreroundOperations";
import Rounds from "./pages/Rounds";
import PostroundOperations from "./pages/PostroundOperations";
import SetDetails from "./pages/SetDetails";
import OutputCode from "./pages/OutputCode";
import { CoordinateSystemProvider } from "./contexts/CoordinateSystemContext";
import { QubitProvider } from "./contexts/QubitContext";

function App() {
  return (
    <CoordinateSystemProvider>
      <QubitProvider>
    <div className="main">
      <Router>
    <Routes>
      <Route path="/" element={<SelectCoordinateSystem />} />
      <Route path="/qubit_setup" element={<QubitSetup />} />
      <Route path="/preround_operations" element={<PreroundOperations />} />
      <Route path="/rounds" element={<Rounds />} />
      <Route path="/postround_operations" element={<PostroundOperations />} />
      <Route path="/set_details" element={<SetDetails />} />
      <Route path="/output_code" element={<OutputCode />} />
    </Routes>
    </Router>

    </div>
    </QubitProvider>
    </CoordinateSystemProvider>
  );
}

export default App;
