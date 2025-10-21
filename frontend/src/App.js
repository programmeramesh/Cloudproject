import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Dashboard from './pages/Dashboard';
import Metrics from './pages/Metrics';
import Predictions from './pages/Predictions';
import Resources from './pages/Resources';
import Login from './pages/Login';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  const handleLogin = (token) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Toaster position="top-right" />
        
        {!isAuthenticated ? (
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        ) : (
          <div className="flex h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
              <Header onLogout={handleLogout} />
              <main className="flex-1 overflow-x-hidden overflow-y-auto p-8 bg-transparent">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/metrics" element={<Metrics />} />
                  <Route path="/predictions" element={<Predictions />} />
                  <Route path="/resources" element={<Resources />} />
                  <Route path="*" element={<Navigate to="/" />} />
                </Routes>
              </main>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
