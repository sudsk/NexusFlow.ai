// frontend/src/components/ApiConnectionChecker.jsx
import React, { useState, useEffect } from 'react';
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  CloseButton,
  Box,
} from '@chakra-ui/react';
import apiService from '../services/api';

const ApiConnectionChecker = ({ onConnectionStatusChange }) => {
  const [isConnected, setIsConnected] = useState(true);
  const [showAlert, setShowAlert] = useState(false);

  // Function to check API connection
  const checkConnection = async () => {
    // Test the API connection
    const connected = await testApiConnection();
    
    setIsConnected(connected);
    setShowAlert(!connected);
    
    if (onConnectionStatusChange) {
      onConnectionStatusChange(connected);
    }
  };
  
  // Simple function to test API connection
  const testApiConnection = async () => {
    try {
      // Try to call a lightweight API endpoint
      await apiService.frameworks.getAll();
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  };

  // Check connection on mount and set up periodic checks
  useEffect(() => {
    // Initial check
    checkConnection();
    
    // Set up interval for periodic checks (every 30 seconds)
    const intervalId = setInterval(checkConnection, 30000);
    
    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, []);

  // Only show the alert if there's a connection issue
  if (!showAlert) {
    return null;
  }

  return (
    <Box position="fixed" top="0" width="100%" zIndex="toast">
      <Alert status="error">
        <AlertIcon />
        <AlertTitle mr={2}>API Connection Error</AlertTitle>
        <AlertDescription>
          Unable to connect to the API. Please check your connection or API key.
        </AlertDescription>
        <CloseButton 
          position="absolute" 
          right="8px" 
          top="8px" 
          onClick={() => setShowAlert(false)}
        />
      </Alert>
    </Box>
  );
};

export default ApiConnectionChecker;
