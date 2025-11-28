import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';


import ProfessorDashboard from './pages/ProfessorDashboard';


function App() {
  return (
    <Router>
      {/* Top navigation bar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4" style={{ background: 'linear-gradient(90deg, #0b69ff 0%, #4f8fdc 100%)' }}>
        <div className="container">
          <Link className="navbar-brand" to="/">Lobster Notes</Link>
          <div className="collapse navbar-collapse">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <Link className="nav-link" to="/professor">Professor Dashboard</Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* 
      Page content routes 
      */}
      <Routes>
        //remove once other pages are incorporated, make home default / path
        <Route path="/" element={<ProfessorDashboard />} />
        
        <Route path="/professor" element={<ProfessorDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;