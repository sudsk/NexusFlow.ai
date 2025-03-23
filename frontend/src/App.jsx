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
  // Check if authenticated
  if (apiService.auth.isAuthenticated()) {
    return children;
  }
  
  // Otherwise, redirect to login
  return <Navigate to="/login" />;
};

function App() {
  const [apiConnected, setApiConnected] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const handleApiConnectionChange = (isConnected) => {
    setApiConnected(isConnected);
  };
  
  const handleToggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
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
              <AppLayout 
                apiConnected={apiConnected} 
                sidebarOpen={sidebarOpen}
                onToggleSidebar={handleToggleSidebar}
              />
            </PrivateRoute>
          } />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

// Main application layout
function AppLayout({ apiConnected, sidebarOpen, onToggleSidebar }) {
  // Define the sidebar width in pixels
  const SIDEBAR_WIDTH = "240px";
  
  return (
    <div style={{ display: 'flex', width: '100%', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar component */}
      <Sidebar 
        isOpen={sidebarOpen} 
        width={SIDEBAR_WIDTH} 
        onClose={onToggleSidebar}
      />
      
      {/* Content area - this will flow naturally beside the sidebar */}
      <div 
        style={{ 
          flex: 1,
          width: `calc(100% - ${sidebarOpen ? SIDEBAR_WIDTH : "0px"})`, 
          marginLeft: sidebarOpen ? SIDEBAR_WIDTH : "0px",
          height: '100vh',
          overflow: 'auto',
          transition: "width 0.3s, margin-left 0.3s" 
        }}
      >
        <Header 
          onToggleSidebar={onToggleSidebar} 
          isSidebarOpen={sidebarOpen} 
        />
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
