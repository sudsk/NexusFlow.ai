// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FlowEditor from './pages/FlowEditor';
import ExecutionViewer from './pages/ExecutionViewer';
import ExecutionsPage from './pages/ExecutionsPage';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ApiConnectionChecker from './components/ApiConnectionChecker';
import Login from './pages/Login';

// Import pages
import FlowList from './pages/FlowList';
import ToolManagement from './pages/ToolManagement';
import DeploymentList from './pages/DeploymentList';
import Settings from './pages/Settings';
import apiService from './services/api';

// Define theme
const theme = extendTheme({
  colors: {
    brand: {
      50: '#e0f2ff',
      100: '#b9deff',
      200: '#90caff',
      300: '#64b5ff',
      400: '#3aa0ff',
      500: '#1a91ff', // Primary brand color
      600: '#0077e6',
      700: '#005bb3',
      800: '#003f80',
      900: '#00254d',
    },
  },
  fonts: {
    heading: '"Inter", sans-serif',
    body: '"Inter", sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
      },
    },
  },
});

// Private route component to handle authentication
const PrivateRoute = ({ children }) => {
  // If using mock API or authenticated, render children
  if (apiService.mock.isEnabled() || apiService.auth.isAuthenticated()) {
    return children;
  }
  
  // Otherwise, redirect to login
  return <Navigate to="/login" />;
};

function App() {
  const [apiConnected, setApiConnected] = useState(null);
  
  const handleApiConnectionChange = (isConnected) => {
    setApiConnected(isConnected);
  };
  
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <ApiConnectionChecker onConnectionStatusChange={handleApiConnectionChange} />
        
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Private routes */}
          <Route path="/*" element={
            <PrivateRoute>
              <AppLayout apiConnected={apiConnected} />
            </PrivateRoute>
          } />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

// Main application layout
function AppLayout({ apiConnected }) {
  return (
    <div className="app-container" style={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      <div className="content-container" style={{ flex: 1, overflow: 'auto' }}>
        <Header />
        <div style={{ padding: '20px' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/flows" element={<FlowList />} />
            <Route path="/flows/new" element={<FlowEditor />} />
            <Route path="/flows/:flowId" element={<FlowEditor />} />
            <Route path="/tools" element={<ToolManagement />} />
            <Route path="/deployments" element={<DeploymentList />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/executions" element={<ExecutionsPage />} />
            <Route path="/executions/:executionId" element={<ExecutionViewer />} />
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default App;
