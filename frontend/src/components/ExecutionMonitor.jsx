import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Badge, 
  Heading, 
  Progress, 
  Card, 
  CardBody,
  Button,
  Spinner,
  useToast,
  Code,
  Tag,
  Alert,
  AlertIcon,
  IconButton,
  Collapse,
  SimpleGrid
} from '@chakra-ui/react';
import { FiClock, FiCheckCircle, FiAlertCircle, FiRotateCw, FiChevronDown, FiChevronUp, FiX } from 'react-icons/fi';
import apiService from '../services/api';

const ExecutionMonitor = ({ executionId, onComplete }) => {
  const [execution, setExecution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [lastStepSeen, setLastStepSeen] = useState(0);
  const [newSteps, setNewSteps] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  const toast = useToast();
  const wsRef = useRef(null);
  const pollingRef = useRef(null);
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Status badge component with appropriate colors
  const StatusBadge = ({ status }) => {
    let color = 'gray';
    
    switch (status) {
      case 'completed':
        color = 'green';
        break;
      case 'failed':
        color = 'red';
        break;
      case 'running':
        color = 'blue';
        break;
      case 'pending':
        color = 'yellow';
        break;
      case 'cancelled':
        color = 'orange';
        break;
      default:
        color = 'gray';
    }
    
    return <Badge colorScheme={color}>{status}</Badge>;
  };
  
  // Calculate execution progress
  const calculateProgress = (execution) => {
    if (!execution) return 0;
    
    // If completed, return 100%
    if (execution.status === 'completed' || execution.status === 'failed' || execution.status === 'cancelled') {
      return 100;
    }
    
    // If pending, return 10%
    if (execution.status === 'pending') {
      return 10;
    }
    
    // Estimate based on steps
    if (execution.execution_trace && execution.execution_trace.length > 0) {
      // Assuming average execution is about 10 steps
      const estimatedProgress = Math.min(90, Math.round((execution.execution_trace.length / 10) * 100));
      return estimatedProgress;
    }
    
    // Default to 20% if running but no steps yet
    return 20;
  };
  
  // Fetch execution status
  const fetchExecutionStatus = async () => {
    try {
      setRefreshing(true);
      const response = await apiService.executions.getById(executionId);
      
      // Update execution data
      setExecution(response.data);
      
      // Check for new steps
      if (response.data.execution_trace) {
        const currentSteps = response.data.execution_trace.length;
        if (currentSteps > lastStepSeen) {
          const newStepsList = response.data.execution_trace.slice(lastStepSeen);
          setNewSteps(newStepsList);
          setLastStepSeen(currentSteps);
        }
      }
      
      // If execution is complete, notify parent component
      if (
        response.data.status === 'completed' || 
        response.data.status === 'failed' || 
        response.data.status === 'cancelled'
      ) {
        if (onComplete) {
          onComplete(response.data);
        }
        
        // Clear polling interval
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        
        // Close WebSocket if connected
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.close();
          setWsConnected(false);
        }
      }
      
      setError(null);
    } catch (err) {
      setError(`Error fetching execution status: ${err.message || 'Unknown error'}`);
      toast({
        title: 'Error fetching status',
        description: err.message || 'Could not fetch execution status',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  };
  
  // Connect to WebSocket for real-time updates
  const connectWebSocket = () => {
    // Skip if in mock mode - use polling instead
    if (apiService.mock.isEnabled()) {
      return;
    }
    
    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    // Create WebSocket connection
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/executions/ws/${executionId}`;
    wsRef.current = new WebSocket(wsUrl);
    
    // WebSocket event handlers
    wsRef.current.onopen = () => {
      setWsConnected(true);
      toast({
        title: 'Real-time updates enabled',
        description: 'Connected to execution stream',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    };
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Update execution status
        if (data.status) {
          setExecution(prev => ({
            ...prev,
            status: data.status,
            result: data.result || prev?.result,
            error: data.error || prev?.error
          }));
        }
        
        // Process new steps
        if (data.new_steps && data.new_steps.length > 0) {
          setNewSteps(data.new_steps);
          
          // Update execution trace
          setExecution(prev => {
            if (!prev) return prev;
            
            const updatedTrace = [
              ...(prev.execution_trace || []),
              ...data.new_steps
            ];
            
            return {
              ...prev,
              execution_trace: updatedTrace
            };
          });
          
          // Update last step seen
          setLastStepSeen(prev => prev + data.new_steps.length);
        }
        
        // Handle completion
        if (data.complete && onComplete) {
          onComplete(execution);
        }
      } catch (err) {
        console.error('Error processing WebSocket message:', err);
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
      
      // Fall back to polling
      startPolling();
      
      toast({
        title: 'WebSocket connection failed',
        description: 'Falling back to polling for updates',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
    };
    
    wsRef.current.onclose = () => {
      setWsConnected(false);
      
      // If execution is still in progress, fall back to polling
      if (
        execution?.status !== 'completed' && 
        execution?.status !== 'failed' && 
        execution?.status !== 'cancelled'
      ) {
        startPolling();
      }
    };
  };
  
  // Start polling for updates
  const startPolling = () => {
    // Clear existing polling interval
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    
    // Set up new polling interval
    pollingRef.current = setInterval(fetchExecutionStatus, 3000);
  };
  
  // Cancel execution
  const handleCancel = async () => {
    try {
      await apiService.executions.cancel(executionId);
      
      toast({
        title: 'Execution cancelled',
        description: 'The execution has been cancelled',
        status: 'info',
        duration: 3000,
        isClosable: true,
      });
      
      // Refresh status
      fetchExecutionStatus();
    } catch (err) {
      toast({
        title: 'Error cancelling execution',
        description: err.message || 'Could not cancel execution',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  // Effect for initial data fetch and websocket connection
  useEffect(() => {
    // Fetch initial status
    fetchExecutionStatus();
    
    // Connect to WebSocket for real-time updates
    connectWebSocket();
    
    // Fall back to polling if WebSocket fails or for mock mode
    if (apiService.mock.isEnabled()) {
      startPolling();
    }
    
    // Cleanup function
    return () => {
      // Clear polling interval
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
      
      // Close WebSocket connection
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [executionId]); // Re-run if executionId changes
  
  // Show notification for new steps
  useEffect(() => {
    if (newSteps.length > 0) {
      // Clear new steps after 5 seconds
      const timer = setTimeout(() => {
        setNewSteps([]);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [newSteps]);
  
  // Loading state
  if (loading && !execution) {
    return (
      <Card variant="outline" mb={4}>
        <CardBody>
          <VStack spacing={4}>
            <Spinner size="xl" />
            <Text>Loading execution details...</Text>
          </VStack>
        </CardBody>
      </Card>
    );
  }
  
  // Error state
  if (error && !execution) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        <Text>{error}</Text>
      </Alert>
    );
  }
  
  // No execution data
  if (!execution) {
    return (
      <Alert status="warning" borderRadius="md">
        <AlertIcon />
        <Text>No execution data available</Text>
      </Alert>
    );
  }
  
  // Calculate progress
  const progress = calculateProgress(execution);
  
  // Determine if execution is in progress
  const isInProgress = execution.status === 'running' || execution.status === 'pending';
  
  return (
    <Card variant="outline" mb={4}>
      <CardBody>
        <VStack spacing={4} align="stretch">
          {/* Header with status */}
          <HStack justify="space-between">
            <HStack>
              <Heading size="md">Execution #{executionId.substring(0, 8)}</Heading>
              <StatusBadge status={execution.status} />
            </HStack>
            
            {/* Actions */}
            <HStack>
              {/* Real-time indicator */}
              {wsConnected && (
                <Tag colorScheme="green" size="sm">Live Updates</Tag>
              )}
              
              {/* Refresh button */}
              <IconButton
                icon={<FiRotateCw />}
                size="sm"
                isLoading={refreshing}
                onClick={fetchExecutionStatus}
                aria-label="Refresh"
              />
              
              {/* Cancel button */}
              {isInProgress && (
                <Button
                  size="sm"
                  colorScheme="red"
                  leftIcon={<FiX />}
                  onClick={handleCancel}
                >
                  Cancel
                </Button>
              )}
              
              {/* Toggle details */}
              <IconButton
                icon={showDetails ? <FiChevronUp /> : <FiChevronDown />}
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                aria-label={showDetails ? "Hide details" : "Show details"}
              />
            </HStack>
          </HStack>
          
          {/* Progress bar */}
          <Box>
            <Progress 
              value={progress} 
              size="sm" 
              colorScheme={
                execution.status === 'completed' ? 'green' :
                execution.status === 'failed' ? 'red' :
                execution.status === 'cancelled' ? 'orange' : 'blue'
              }
              isAnimated={isInProgress}
              hasStripe={isInProgress}
            />
          </Box>
          
          {/* Basic info */}
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
            <HStack>
              <FiClock />
              <Text>Started: {formatTimestamp(execution.started_at)}</Text>
            </HStack>
            
            {execution.completed_at && (
              <HStack>
                {execution.status === 'completed' ? <FiCheckCircle /> : <FiAlertCircle />}
                <Text>Completed: {formatTimestamp(execution.completed_at)}</Text>
              </HStack>
            )}
            
            {execution.steps > 0 && (
              <Text>Steps: {execution.steps}</Text>
            )}
          </SimpleGrid>
          
          {/* New steps notification */}
          {newSteps.length > 0 && (
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Text>{newSteps.length} new {newSteps.length === 1 ? 'step' : 'steps'} received</Text>
            </Alert>
          )}
          
          {/* Detailed information - collapsible */}
          <Collapse in={showDetails} animateOpacity>
            <VStack spacing={4} align="stretch" mt={2}>
              {/* Flow information */}
              <Box>
                <Text fontWeight="bold">Flow:</Text>
                <Text>{execution.flow_name || execution.flow_id}</Text>
              </Box>
              
              {/* Input */}
              <Box>
                <Text fontWeight="bold">Input:</Text>
                <Code p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
                  {JSON.stringify(execution.input, null, 2)}
                </Code>
              </Box>
              
              {/* Output or Error */}
              {(execution.result || execution.error) && (
                <Box>
                  <Text fontWeight="bold">{execution.error ? 'Error:' : 'Result:'}</Text>
                  {execution.error ? (
                    <Text color="red.500">{execution.error}</Text>
                  ) : execution.result?.output?.content ? (
                    <Text>{execution.result.output.content}</Text>
                  ) : (
                    <Code p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
                      {JSON.stringify(execution.result, null, 2)}
                    </Code>
                  )}
                </Box>
              )}
              
              {/* Last few steps */}
              {execution.execution_trace && execution.execution_trace.length > 0 && (
                <Box>
                  <Text fontWeight="bold">Recent Steps:</Text>
                  <VStack spacing={2} align="stretch">
                    {execution.execution_trace.slice(-3).map((step, index) => (
                      <Card key={index} size="sm" variant="outline">
                        <CardBody>
                          <HStack justify="space-between">
                            <Text fontWeight="bold">Step {step.step}: {step.type}</Text>
                            <Text fontSize="sm">{formatTimestamp(step.timestamp)}</Text>
                          </HStack>
                          {step.agent_name && (
                            <Text>Agent: {step.agent_name}</Text>
                          )}
                          {step.output?.content && (
                            <Text noOfLines={2}>{step.output.content}</Text>
                          )}
                        </CardBody>
                      </Card>
                    ))}
                  </VStack>
                </Box>
              )}
            </VStack>
          </Collapse>
          
          {/* View full details link */}
          {execution.status === 'completed' || execution.status === 'failed' ? (
            <Button 
              colorScheme="blue" 
              variant="link" 
              size="sm" 
              onClick={() => { 
                if (onComplete) onComplete(execution);
              }}
            >
              View Full Results
            </Button>
          ) : null}
        </VStack>
      </CardBody>
    </Card>
  );
};

export default ExecutionMonitor;
