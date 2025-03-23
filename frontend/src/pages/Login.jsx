// frontend/src/pages/Login.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  Alert,
  AlertIcon,
  InputGroup,
  InputRightElement,
  Flex,
  Card,
  CardBody,
  FormHelperText,
  useColorModeValue,
  Link,
} from '@chakra-ui/react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiEye, FiEyeOff, FiKey } from 'react-icons/fi';
import apiService from '../services/api';

const Login = () => {
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";
  
  // Define colors for light/dark mode
  const cardBg = useColorModeValue('white', 'gray.700');
  const brandColor = useColorModeValue('brand.500', 'brand.300');
  
  // Check if already authenticated
  useEffect(() => {
    if (apiService.auth.isAuthenticated()) {
      navigate(from, { replace: true });
    }
  }, [from, navigate]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      setError('Please enter your API key');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // Store the API key
      apiService.auth.setApiKey(apiKey);
      
      // Redirect to requested page
      navigate(from, { replace: true });
    } catch (err) {
      setError('Authentication failed. Please check your API key and try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Flex minH="100vh" align="center" justify="center" bg="gray.50">
      <Card bg={cardBg} shadow="lg" p={8} rounded="lg" maxW="md" w="full">
        <CardBody>
          <VStack spacing={6} align="stretch">
            <Box textAlign="center">
              <Heading size="xl" mb={2} color={brandColor}>NexusFlow.ai</Heading>
              <Text color="gray.500">Multi-Framework Agent Orchestration</Text>
            </Box>
            
            {error && (
              <Alert status="error" rounded="md">
                <AlertIcon />
                {error}
              </Alert>
            )}
            
            <form onSubmit={handleSubmit}>
              <VStack spacing={6}>
                <FormControl id="api-key" isRequired>
                  <FormLabel>API Key</FormLabel>
                  <InputGroup>
                    <Input
                      type={showApiKey ? 'text' : 'password'}
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="Enter your API key"
                      autoComplete="off"
                      pr="4.5rem"
                    />
                    <InputRightElement width="4.5rem">
                      <Button h="1.75rem" size="sm" onClick={() => setShowApiKey(!showApiKey)}>
                        {showApiKey ? <FiEyeOff /> : <FiEye />}
                      </Button>
                    </InputRightElement>
                  </InputGroup>
                  <FormHelperText>
                    Enter your NexusFlow API key to access the platform
                  </FormHelperText>
                </FormControl>
                
                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  width="full"
                  isLoading={isLoading}
                  leftIcon={<FiKey />}
                >
                  Sign In with API Key
                </Button>
                
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  Don't have an API key? Contact your administrator for access.
                </Text>
              </VStack>
            </form>
          </VStack>
        </CardBody>
      </Card>
    </Flex>
  );
};

export default Login;
