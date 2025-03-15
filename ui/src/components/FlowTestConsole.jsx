// frontend/src/components/FlowTestConsole.jsx
/* eslint-disable no-unused-vars */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Textarea, Button, Spinner, Text, Progress,
  VStack, HStack, Badge, useToast, Code, Alert, AlertIcon,
  Tabs, TabList, TabPanels, Tab, TabPanel,
  Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon,
  Flex, Icon
} from '@chakra-ui/react';
import { FiPlay, FiCpu, FiTool, FiLink, FiCheck, FiX, FiInfo } from 'react-icons/fi';
import apiService from '../services/api';

const FlowTestConsole = ({ flowId, flowConfig }) => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState(null);
  const [executionId, setExecutionId] = useState(null);
  const [status, setStatus] = useState(null); // 'pending', 'running', 'completed', 'failed'
  const [executionTrace, setExecutionTrace] = useState([]);
  const [currentStepCount, setCurrentStepCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [executionError, setExecutionError] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  const toast = useToast();

  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // Start flow execution
  const testFlow = async () => {
    if (!input.trim()) {
      toast({
        title: 'Input required',
        description: 'Please enter a query to test the flow',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Reset state
    setIsLoading(true);
    setExecutionError(null);
    setOutput(null);
    setExecutionTrace([]);
    setCurrentStepCount(0);
    setStatus('initializing');
    
    try {
      // Use appropriate API endpoint based on if we're testing an existing flow or a draft
      let response;
      if (flowId) {
        // Execute existing flow
        response = await apiService.flows.execute(flowId, { query: input });
      } else {
        // Execute flow configuration directly
        response = await apiService.execute({ flow_config: flowConfig, input: { query: input } });
      }
      
      // Set execution ID for status polling
      if (response.data.execution_id) {
        setExecutionId(response.data.execution_id);
        setStatus('pending');
        
        // Start polling for execution status
        const interval = setInterval(() => checkExecutionStatus(response.data.execution_id), 2000);
        setPollingInterval(interval);
        
        toast({
          title: 'Execution started',
          description: 'Flow execution has been initiated',
          status: 'info',
          duration: 3000,
          isClosable: true,
        });
      } else if (response.data.output) {
        // If the execution was synchronous and already completed
        setStatus('completed');
        setOutput(response.data.output);
        setExecutionTrace(response.data.execution_trace || []);
        setCurrentStepCount(response.data.steps || 0);
      }
    } catch (error) {
      console.error('Error executing flow:', error);
      setExecutionError(error.response?.data?.detail || 'Failed to execute flow');
      setStatus('failed');
      toast({
        title: 'Execution failed',
        description: error.response?.data?.detail || 'Could not start flow execution',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Check execution status
  const checkExecutionStatus = async (execId) => {
    try {
      const response = await apiService.executions.getById(execId);
      const executionData = response.data;
      
      // Update execution status
      setStatus(executionData.status);
      
      // If there's a partial trace, update it
      if (executionData.execution_trace && executionData.execution_trace.length > 0) {
        setExecutionTrace(executionData.execution_trace);
        setCurrentStepCount(executionData.execution_trace.length);
      }
      
      // If execution is complete or failed, stop polling
      if (executionData.status === 'completed' || executionData.status === 'failed') {
        if (pollingInterval) {
          clearInterval(pollingInterval);
          setPollingInterval(null);
        }
        
        // Set output or error
        if (executionData.status === 'completed' && executionData.result) {
          setOutput(executionData.result);
        } else if (executionData.status === 'failed') {
          setExecutionError(executionData.error || 'Execution failed without specific error');
        }
      }
    } catch (error) {
      console.error('Error checking execution status:', error);
      // Don't stop polling on a single error - it might be transient
    }
  };

  // Helper to get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'running': return 'blue';
      case 'pending': return 'orange';
      default: return 'gray';
    }
  };

  // Helper to get step icon
  const getStepIcon = (type) => {
    switch (type) {
      case 'agent_execution': return FiCpu;
      case 'tool_execution': return FiTool;
      case 'delegation': return FiLink;
      case 'start': return FiInfo;
      case 'complete': return FiCheck;
      default: return FiInfo;
    }
  };

  return (
    <Box className="flow-test-console">
      <VStack spacing={4} align="stretch">
        <Text fontSize="md" fontWeight="medium">Enter a query to test your flow:</Text>
        
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your test query here..."
          rows={4}
        />
        
        <Button 
          onClick={testFlow}
          isLoading={isLoading}
          loadingText="Starting execution"
          leftIcon={<FiPlay />}
          colorScheme="blue"
          isDisabled={status === 'pending' || status === 'running'}
        >
          Test Flow
        </Button>
        
        {status && (
          <Flex align="center" justify="space-between">
            <HStack>
              <Text fontWeight="bold">Status:</Text>
              <Badge colorScheme={getStatusColor(status)} px={2} py={1}>
                {status.toUpperCase()}
              </Badge>
            </HStack>
            
            {(status === 'pending' || status === 'running') && (
              <Text fontSize="sm">Step {currentStepCount}</Text>
            )}
          </Flex>
        )}
        
        {(status === 'pending' || status === 'running') && (
          <Box>
            <Progress size="sm" isIndeterminate colorScheme="blue" />
          </Box>
        )}
        
        {executionError && (
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            {executionError}
          </Alert>
        )}
        
        {(executionTrace.length > 0 || output) && (
          <Tabs variant="enclosed" colorScheme="blue" mt={4}>
            <TabList>
              <Tab>Results</Tab>
              <Tab>Execution Trace ({executionTrace.length})</Tab>
            </TabList>
            
            <TabPanels>
              <TabPanel p={4}>
                {output ? (
                  <Box whiteSpace="pre-wrap" p={4} borderWidth="1px" borderRadius="md">
                    {typeof output === 'object' && output.content 
                      ? output.content 
                      : JSON.stringify(output, null, 2)}
                  </Box>
                ) : (
                  <Text color="gray.500">
                    Execution in progress... Results will appear here when complete.
                  </Text>
                )}
              </TabPanel>
              
              <TabPanel p={4}>
                {executionTrace.length > 0 ? (
                  <Accordion allowMultiple defaultIndex={[0]}>
                    {executionTrace.map((step, index) => (
                      <AccordionItem key={index}>
                        <AccordionButton py={2}>
                          <Box flex="1" textAlign="left">
                            <HStack>
                              <Badge colorScheme="blue">Step {step.step || index + 1}</Badge>
                              <Icon as={getStepIcon(step.type)} />
                              <Text fontWeight="medium">{step.type}</Text>
                              {step.agent_name && (
                                <Badge variant="outline" colorScheme="purple">
                                  {step.agent_name}
                                </Badge>
                              )}
                            </HStack>
                          </Box>
                          <AccordionIcon />
                        </AccordionButton>
                        <AccordionPanel pb={4}>
                          <VStack align="stretch" spacing={3}>
                            {step.timestamp && (
                              <Text fontSize="sm" color="gray.500">
                                {new Date(step.timestamp).toLocaleString()}
                              </Text>
                            )}
                            
                            {step.input && (
                              <Box>
                                <Text fontWeight="bold" fontSize="sm">Input:</Text>
                                <Code p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
                                  {typeof step.input === 'object' 
                                    ? JSON.stringify(step.input, null, 2) 
                                    : step.input}
                                </Code>
                              </Box>
                            )}
                            
                            {step.output && (
                              <Box>
                                <Text fontWeight="bold" fontSize="sm">Output:</Text>
                                <Code p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
                                  {typeof step.output === 'object' 
                                    ? (step.output.content || JSON.stringify(step.output, null, 2)) 
                                    : step.output}
                                </Code>
                              </Box>
                            )}
                            
                            {step.decision && (
                              <Box>
                                <Text fontWeight="bold" fontSize="sm">Decision:</Text>
                                <Code p={2} borderRadius="md" display="block">
                                  {typeof step.decision === 'object' 
                                    ? JSON.stringify(step.decision, null, 2) 
                                    : step.decision}
                                </Code>
                              </Box>
                            )}
                          </VStack>
                        </AccordionPanel>
                      </AccordionItem>
                    ))}
                  </Accordion>
                ) : (
                  <Text color="gray.500">Waiting for execution steps...</Text>
                )}
              </TabPanel>
            </TabPanels>
          </Tabs>
        )}
      </VStack>
    </Box>
  );
};

export default FlowTestConsole;
