import React from 'react';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FlowEditor from './pages/FlowEditor';
import ExecutionViewer from './pages/ExecutionViewer';
import Header from './components/Header';
import Sidebar from './components/Sidebar';

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

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <div className="app-container" style={{ display: 'flex', height: '100vh' }}>
          <Sidebar />
          <div className="content-container" style={{ flex: 1, overflow: 'auto' }}>
            <Header />
            <div style={{ padding: '20px' }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/flows/new" element={<FlowEditor />} />
                <Route path="/flows/:flowId" element={<FlowEditor />} />
                <Route path="/executions/:executionId" element={<ExecutionViewer />} />
              </Routes>
            </div>
          </div>
        </div>
      </Router>
    </ChakraProvider>
  );
}

export default App;
