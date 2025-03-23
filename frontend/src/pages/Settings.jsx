// frontend/src/pages/Settings.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  FormControl,
  FormLabel,
  FormHelperText,
  Input,
  InputGroup,
  InputRightElement,
  Select,
  Switch,
  Button,
  Divider,
  Text,
  Card,
  CardHeader,
  CardBody,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Alert,
  AlertIcon,
  Badge,
  HStack,
  Code,
  useToast,
  useColorModeValue,
  useColorMode,
} from '@chakra-ui/react';
import { FiSave, FiEye, FiEyeOff, FiKey } from 'react-icons/fi';
import apiService from '../services/api';

const Settings = () => {
  const toast = useToast();
  const { colorMode, toggleColorMode } = useColorMode();
  
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [settings, setSettings] = useState({
    defaultFramework: 'langgraph',
    enableStreamingExecutions: true,
    enableVisualizations: true,
    theme: colorMode,
    logLevel: 'info',
    autoRefreshDashboard: true,
    refreshInterval: 30,
  });
  const [isSaving, setIsSaving] = useState(false);
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Load saved settings and API key on mount
  useEffect(() => {
    // Load saved settings from localStorage
    const savedSettings = localStorage.getItem('nexusflow_settings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings(prevSettings => ({
          ...prevSettings,
          ...parsedSettings
        }));
      } catch (error) {
        console.error('Error parsing saved settings:', error);
      }
    }
    
    // Load saved API key (masked)
    const savedApiKey = localStorage.getItem('nexusflow_api_key');
    if (savedApiKey) {
      // Mask the API key for display
      setApiKey('•'.repeat(16));
    }
  }, []);

  // Handle settings save
  const handleSaveSettings = async () => {
    setIsSaving(true);
    
    try {
      // Update theme if changed
      if (settings.theme !== colorMode) {
        toggleColorMode();
      }
      
      // Save settings to localStorage
      localStorage.setItem('nexusflow_settings', JSON.stringify(settings));
      
      toast({
        title: 'Settings saved',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: 'Error saving settings',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Handle API key changes
  const handleApiKeyChange = (e) => {
    setApiKey(e.target.value);
  };

  // Save new API key
  const handleSaveApiKey = () => {
    if (apiKey && apiKey !== '•'.repeat(16)) {
      apiService.auth.setApiKey(apiKey);
      
      toast({
        title: 'API key updated',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Mask the API key after saving
      setApiKey('•'.repeat(16));
    }
  };

  // Handle form field changes
  const handleSettingChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>Settings</Heading>
      
      <Tabs variant="enclosed" colorScheme="blue">
        <TabList>
          <Tab>General</Tab>
          <Tab>API Configuration</Tab>
          <Tab>Flow Execution</Tab>
          <Tab>About</Tab>
        </TabList>
        
        <TabPanels>
          {/* General Settings Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Heading size="md">General Settings</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  <FormControl>
                    <FormLabel>Default Framework</FormLabel>
                    <Select
                      value={settings.defaultFramework}
                      onChange={(e) => handleSettingChange('defaultFramework', e.target.value)}
                    >
                      <option value="langgraph">LangGraph</option>
                      <option value="crewai">CrewAI</option>
                      <option value="autogen">AutoGen</option>
                      <option value="dspy">DSPy</option>
                    </Select>
                    <FormHelperText>
                      The default framework to use when creating new flows
                    </FormHelperText>
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Theme</FormLabel>
                    <Select
                      value={settings.theme}
                      onChange={(e) => handleSettingChange('theme', e.target.value)}
                      ml={2}
                      w="120px"
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                    </Select>
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Enable Visualizations</FormLabel>
                    <Switch
                      isChecked={settings.enableVisualizations}
                      onChange={(e) => handleSettingChange('enableVisualizations', e.target.checked)}
                    />
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Auto-refresh Dashboard</FormLabel>
                    <Switch
                      isChecked={settings.autoRefreshDashboard}
                      onChange={(e) => handleSettingChange('autoRefreshDashboard', e.target.checked)}
                    />
                  </FormControl>
                  
                  <Button
                    leftIcon={<FiSave />}
                    colorScheme="blue"
                    onClick={handleSaveSettings}
                    isLoading={isSaving}
                    alignSelf="flex-start"
                  >
                    Save Settings
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>
          
          {/* API Configuration Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={6}>
              <CardHeader>
                <Heading size="md">API Configuration</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  <FormControl>
                    <FormLabel>API Key</FormLabel>
                    <InputGroup>
                      <Input
                        type={showApiKey ? 'text' : 'password'}
                        value={apiKey}
                        onChange={handleApiKeyChange}
                        placeholder="Enter your API key"
                      />
                      <InputRightElement width="4.5rem">
                        <Button
                          h="1.75rem"
                          size="sm"
                          onClick={() => setShowApiKey(!showApiKey)}
                        >
                          {showApiKey ? <FiEyeOff /> : <FiEye />}
                        </Button>
                      </InputRightElement>
                    </InputGroup>
                    <FormHelperText>
                      Your API key for accessing NexusFlow.ai services
                    </FormHelperText>
                  </FormControl>
                  
                  <Button
                    leftIcon={<FiKey />}
                    colorScheme="blue"
                    onClick={handleSaveApiKey}
                    alignSelf="flex-start"
                  >
                    Update API Key
                  </Button>
                </VStack>
              </CardBody>
            </Card>
            
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Heading size="md">API Endpoints</Heading>
              </CardHeader>
              <CardBody>
                <Text mb={4}>
                  Current API URL: <Code>{process.env.REACT_APP_API_URL || '/api'}</Code>
                </Text>
                
                <Alert status="warning" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <Text fontWeight="bold">Development Mode</Text>
                    <Text fontSize="sm">
                      Changes to API endpoints require restarting the application with updated environment variables.
                    </Text>
                  </Box>
                </Alert>
              </CardBody>
            </Card>
          </TabPanel>
          
          {/* Flow Execution Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Heading size="md">Flow Execution Settings</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  <FormControl display="flex" alignItems="center">
                    <FormLabel mb="0">Enable Streaming Executions</FormLabel>
                    <Switch
                      isChecked={settings.enableStreamingExecutions}
                      onChange={(e) => handleSettingChange('enableStreamingExecutions', e.target.checked)}
                    />
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Log Level</FormLabel>
                    <Select
                      value={settings.logLevel}
                      onChange={(e) => handleSettingChange('logLevel', e.target.value)}
                    >
                      <option value="debug">Debug</option>
                      <option value="info">Info</option>
                      <option value="warning">Warning</option>
                      <option value="error">Error</option>
                    </Select>
                    <FormHelperText>
                      Controls the verbosity of logs in the console
                    </FormHelperText>
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Default Execution Timeout (seconds)</FormLabel>
                    <Input
                      type="number"
                      value={settings.defaultTimeout || 60}
                      onChange={(e) => handleSettingChange('defaultTimeout', parseInt(e.target.value))}
                      min={10}
                      max={300}
                    />
                    <FormHelperText>
                      Default timeout for flow executions (10-300 seconds)
                    </FormHelperText>
                  </FormControl>
                  
                  <Button
                    leftIcon={<FiSave />}
                    colorScheme="blue"
                    onClick={handleSaveSettings}
                    isLoading={isSaving}
                    alignSelf="flex-start"
                  >
                    Save Settings
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>
          
          {/* About Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Heading size="md">About NexusFlow.ai</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <HStack>
                    <Text fontWeight="bold">Version:</Text>
                    <Text>0.1.0 (Alpha)</Text>
                    <Badge colorScheme="purple">Developer Preview</Badge>
                  </HStack>
                  
                  <Text>
                    NexusFlow.ai is a multi-framework agent orchestration platform that makes it easy to
                    build, test, and deploy AI agent workflows using frameworks like LangGraph, CrewAI, and more.
                  </Text>
                  
                  <Divider />
                  
                  <Heading size="sm">Supported Frameworks</Heading>
                  <HStack spacing={2} flexWrap="wrap">
                    <Badge colorScheme="blue" p={1}>LangGraph</Badge>
                    <Badge colorScheme="purple" p={1}>CrewAI</Badge>
                    <Badge colorScheme="green" p={1}>AutoGen</Badge>
                    <Badge colorScheme="orange" p={1}>DSPy</Badge>
                  </HStack>
                  
                  <Divider />
                  
                  <Alert status="info" borderRadius="md">
                    <AlertIcon />
                    <Text fontSize="sm">
                      This application follows the NexusFlow.ai architecture where flows are the central 
                      entity with configurable agents, tools, and deployment options.
                    </Text>
                  </Alert>
                </VStack>
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default Settings;
