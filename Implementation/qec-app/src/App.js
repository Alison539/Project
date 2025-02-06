import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SelectCoordinateSystem from "./pages/SelectCoordinateSystem";
import QubitSetup from "./pages/QubitSetup";
import Rounds from "./pages/Rounds";
import SetDetails from "./pages/SetDetails";
import OutputCode from "./pages/OutputCode";
import GenerateGraph from "./pages/GenerateGraph";
import { CoordinateSystemProvider } from "./contexts/CoordinateSystemContext";
import { QubitProvider } from "./contexts/QubitContext";
import { OperationProvider } from "./contexts/OperationContext";
import { DetailsProvider } from "./contexts/DetailsContext";
import { StimCodeProvider } from "./contexts/StimCodeContext";
import { DistancesProvider } from "./contexts/DistancesContext";
import CreateDistances from "./pages/CreateDistances";

function App() {
  return (
    <CoordinateSystemProvider>
      <QubitProvider>
        <DistancesProvider>
          <OperationProvider>
            <DetailsProvider>
              <StimCodeProvider>
                <div className="main">
                  <Router>
                    <Routes>
                      <Route path="/" element={<SelectCoordinateSystem />} />
                      <Route path="/qubit_setup" element={<QubitSetup />} />
                      <Route path="/rounds" element={<Rounds />} />
                      <Route path="/set_details" element={<SetDetails />} />
                      <Route path="/output_code" element={<OutputCode />} />
                      <Route path="/generate_graph" element={<GenerateGraph />} />
                      <Route path="/add_distances" element={<CreateDistances />} />
                    </Routes>
                  </Router>
                </div>
              </StimCodeProvider>
            </DetailsProvider>
          </OperationProvider>
        </DistancesProvider>
      </QubitProvider>
    </CoordinateSystemProvider>
  );
}

export default App;
