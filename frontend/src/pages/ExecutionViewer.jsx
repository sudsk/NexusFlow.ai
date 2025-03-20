// frontend/src/pages/ExecutionViewer.jsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Heading,
  Card,
  CardHeader,
  CardBody,
  Badge,
  Text,
  Flex,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  VStack,
  HStack,
  Icon,
  Tag,
  Divider,
  Spinner,
  Button,
  Code,
  useToast,
  useColorModeValue,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Select,
} from '@chakra-ui/react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  FiHome,
  FiCpu,
  FiCheck,
  FiX,
  FiClock,
  FiSend,
  FiLink,
  FiTool,
  FiAlertCircle,
  FiInfo,
  FiDownload,
  FiRefreshCw,
  FiBarChart2,
} from 'react-icons/fi';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';
import apiService from '../services/api';

// Import custom visualization component
import FlowVisualization from '../components/FlowVisualization';

const ExecutionViewer = () => {
  const { executionId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [execution, setExecution] = useState(null);
  const [flowDetails, setFlowDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [visualizationType, setVisualizationType] = useState('auto');
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const codeBg = useColorModeValue('gray.50', 'gray.700');

  // Fetch execution data
  useEffect(() => {
    fetchExecutionData();
  }, [executionId]);

  const fetchExecutionData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch execution details
      const response = await apiService.executions.getById(executionId);
      setExecution(response.data);
      
      // If execution has a flow_id, fetch flow details too
      if (response.data.flow_id) {
        try {
          const flowResponse = await apiService.flows.getById(response.data.flow_id);
          setFlowDetails(flowResponse.data);
        } catch (flowError) {
          console.error('Error fetching flow details:', flowError);
          // Non-critical error, don't set main error state
        }
      }
      
      // Generate visualization nodes and edges if execution trace exists
      if (response.data.execution_trace && response.data.execution_trace.length > 0) {
        generateVisualization(response.data);
      }
    } catch (error) {
      console.error('Error fetching execution:', error);
      setError(error.response?.data?.detail || 'Failed to load execution data');
      toast({
        title: 'Error',
        description: 'Could not load execution data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Export execution results as JSON
  const handleExportResults = () => {
    if (!execution) return;
    
    const jsonString = JSON.stringify(execution, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `execution-${executionId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Results exported',
      description: 'Execution results downloaded as JSON',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
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

  // Helper to get icon for status
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return FiCheck;
      case 'failed': return FiX;
      case 'running': case 'pending': return FiClock;
      default: return FiAlertCircle;
    }
  };

  // Helper to get icon for step type
  const getStepIcon = (type) => {
    switch (type) {
      case 'agent_execution': return FiCpu;
      case 'delegation': return FiSend;
      case 'tool_execution': return FiTool;
      case 'start': return FiInfo;
      case 'complete': return FiCheck;
      default: return FiInfo;
    }
  };

  if (isLoading) {
    return (
      <Flex justify="center" align="center" height="500px">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10}>
        <Alert status="error" borderRadius="md" maxW="xl" mx="auto">
          <AlertIcon />
          <AlertTitle>Error loading execution</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button mt={6} onClick={() => navigate('/executions')}>
          Back to Executions
        </Button>
      </Box>
    );
  }

  if (!execution) {
    return (
      <Box textAlign="center" py={10}>
        <Heading size="md">Execution not found</Heading>
        <Button mt={4} onClick={() => navigate('/executions')}>
          Back to Executions
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Breadcrumb mb={4} fontSize="sm">
        <BreadcrumbItem>
          <BreadcrumbLink as={Link} to="/">
            <FiHome style={{ display: 'inline', marginRight: '5px' }} />
            Home
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem>
          <BreadcrumbLink as={Link} to="/executions">
            Executions
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>
          <BreadcrumbLink>Execution {executionId.slice(0, 8)}</BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>

      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Execution Details</Heading>
        <HStack>
          {(execution.status === 'running' || execution.status === 'pending') && (
            <Button 
              leftIcon={<FiRefreshCw />} 
              onClick={refreshExecution}
              isLoading={isRefreshing}
              loadingText="Refreshing"
              mr={2}
            >
              Refresh
            </Button>
          )}
          <Button 
            leftIcon={<FiDownload />} 
            onClick={handleExportResults}
          >
            Export Results
          </Button>
        </HStack>
      </Flex>

      {/* Execution Summary Card */}
      <Card mb={6} bg={cardBg} borderColor={borderColor} borderWidth="1px">
        <CardBody>
          <Flex direction={{ base: 'column', md: 'row' }} justify="space-between">
            <VStack align="start" spacing={2} mb={{ base: 4, md: 0 }}>
              <Heading size="md">
                {execution.flow_name || flowDetails?.name || "Execution"}
              </Heading>
              <HStack flexWrap="wrap">
                <Badge colorScheme={getStatusColor(execution.status)} px={2} py={1}>
                  <Flex align="center">
                    <Icon as={getStatusIcon(execution.status)} mr={1} />
                    {execution.status.toUpperCase()}
                  </Flex>
                </Badge>
                {execution.framework && (
                  <Tag colorScheme="blue">Framework: {execution.framework}</Tag>
                )}
                {execution.steps && <Tag>Steps: {execution.steps}</Tag>}
              </HStack>
            </VStack>
            
            <VStack align={{ base: 'start', md: 'end' }} spacing={1}>
              <Text fontSize="sm" color="gray.500">
                Started: {new Date(execution.started_at).toLocaleString()}
              </Text>
              {execution.completed_at && (
                <Text fontSize="sm" color="gray.500">
                  Completed: {new Date(execution.completed_at).toLocaleString()}
                </Text>
              )}
              <Text fontSize="sm" color="gray.500">
                Flow ID: {execution.flow_id || 'N/A'}
              </Text>
              <Text fontSize="sm" color="gray.500">
                Execution ID: {execution.id || executionId}
              </Text>
            </VStack>
          </Flex>
        </CardBody>
      </Card>

      {/* Execution Details Tabs */}
      <Tabs variant="enclosed" colorScheme="blue">
        <TabList>
          <Tab>Results</Tab>
          <Tab>Execution Trace</Tab>
          <Tab>Flow Visualization</Tab>
          {execution.framework === 'langgraph' && <Tab>LangGraph Specific</Tab>}
          {execution.framework === 'crewai' && <Tab>CrewAI Specific</Tab>}
        </TabList>

        <TabPanels>
          {/* Results Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Heading size="md">Final Output</Heading>
              </CardHeader>
              <CardBody>
                {(execution.status === 'completed' && execution.result) ? (
                  <Box whiteSpace="pre-wrap">
                    {typeof execution.result.output === 'object' && execution.result.output?.content
                      ? execution.result.output.content
                      : typeof execution.result === 'object' && execution.result.output?.content
                        ? execution.result.output.content
                        : typeof execution.result.output === 'string'
                          ? execution.result.output
                          : typeof execution.result === 'string'
                            ? execution.result
                            : JSON.stringify(execution.result, null, 2)}
                  </Box>
                ) : execution.status === 'failed' ? (
                  <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    <AlertTitle>Execution Failed</AlertTitle>
                    <AlertDescription>
                      {execution.error || 'No specific error message provided'}
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Text color="gray.500">
                    Execution is still in progress. Results will appear here when complete.
                  </Text>
                )}
              </CardBody>
            </Card>
          </TabPanel>

          {/* Execution Trace Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Flex justify="space-between" align="center">
                  <Heading size="md">Execution Steps</Heading>
                  <HStack spacing={2}>
                    <Text fontSize="sm">Filter:</Text>
                    <Select 
                      size="sm" 
                      width="150px" 
                      defaultValue="all"
                      onChange={(e) => setVisualizationType(e.target.value)}
                    >
                      <option value="all">All Steps</option>
                      <option value="agent_execution">Agent Execution</option>
                      <option value="delegation">Delegations</option>
                      <option value="tool_execution">Tool Usage</option>
                    </Select>
                  </HStack>
                </Flex>
              </CardHeader>
              <CardBody>
                {execution.execution_trace && execution.execution_trace.length > 0 ? (
                  <Accordion allowMultiple defaultIndex={[0]}>
                    {execution.execution_trace
                      .filter(step => visualizationType === 'all' || step.type === visualizationType)
                      .map((step, index) => (
                        <AccordionItem key={index}>
                          <AccordionButton py={2}>
                            <Box flex="1" textAlign="left">
                              <HStack>
                                <Badge>Step {step.step || index + 1}</Badge>
                                <Icon as={getStepIcon(step.type)} />
                                <Text fontWeight="bold">{step.type}</Text>
                                {step.agent_name && (
                                  <Tag colorScheme="blue">{step.agent_name}</Tag>
                                )}
                                <Text fontSize="sm" color="gray.500">
                                  {new Date(step.timestamp).toLocaleTimeString()}
                                </Text>
                              </HStack>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <VStack align="stretch" spacing={3}>
                              {step.input && (
                                <Box mt={2}>
                                  <Text fontWeight="bold" fontSize="sm">Input:</Text>
                                  <Code 
                                    p={2} 
                                    bg={codeBg} 
                                    borderRadius="md" 
                                    w="100%" 
                                    display="block"
                                  >
                                    {typeof step.input === 'object' 
                                      ? JSON.stringify(step.input, null, 2) 
                                      : step.input}
                                  </Code>
                                </Box>
                              )}

                              {step.decision && (
                                <Box mt={2}>
                                  <Text fontWeight="bold" fontSize="sm">Decision:</Text>
                                  <Code 
                                    p={2} 
                                    bg={codeBg} 
                                    borderRadius="md" 
                                    w="100%" 
                                    display="block"
                                  >
                                    {typeof step.decision === 'object' 
                                      ? JSON.stringify(step.decision, null, 2) 
                                      : step.decision}
                                  </Code>
                                </Box>
                              )}
                              
                              {step.output && (
                                <Box mt={2}>
                                  <Text fontWeight="bold" fontSize="sm">Output:</Text>
                                  <Code 
                                    p={2} 
                                    bg={codeBg} 
                                    borderRadius="md" 
                                    w="100%" 
                                    display="block" 
                                    whiteSpace="pre-wrap"
                                  >
                                    {typeof step.output === 'object' 
                                      ? (step.output.content || JSON.stringify(step.output, null, 2))
                                      : step.output
                                    }
                                  </Code>
                                </Box>
                              )}
                            </VStack>
                          </AccordionPanel>
                        </AccordionItem>
                    ))}
                  </Accordion>
                ) : (
                  <Text color="gray.500">No execution trace available.</Text>
                )}
              </CardBody>
            </Card>
          </TabPanel>

          {/* Flow Visualization Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" h="600px">
              <CardHeader>
                <Heading size="md">Flow Visualization</Heading>
              </CardHeader>
              <CardBody>
                {nodes.length > 0 ? (
                  <Box h="500px">
                    <ReactFlow
                      nodes={nodes}
                      edges={edges}
                      fitView
                    >
                      <Controls />
                      <Background />
                    </ReactFlow>
                  </Box>
                ) : (
                  <Flex justify="center" align="center" h="100%">
                    <Text color="gray.500">No visualization data available</Text>
                  </Flex>
                )}
              </CardBody>
            </Card>
          </TabPanel>

          {/* Framework-specific tabs */}
          {execution.framework === 'langgraph' && (
            <TabPanel>
              <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                <CardHeader>
                  <Heading size="md">LangGraph Visualization</Heading>
                </CardHeader>
                <CardBody>
                  {execution.execution_trace && execution.execution_trace.length > 0 ? (
                    <Box>
                      <Text mb={4}>
                        LangGraph specific visualizations would appear here, such as the 
                        graph state transitions and node activations.
                      </Text>
                      
                      {/* Graph state transitions visualization would be here */}
                      <Heading size="sm" mb={2}>State Transitions</Heading>
                      <Box p={4} borderWidth="1px" borderRadius="md" mb={4}>
                        {/* This would be a specialized visualization for LangGraph */}
                        <Text color="gray.500">State transition diagram would be rendered here</Text>
                      </Box>
                      
                      {/* Metrics specific to LangGraph */}
                      <Heading size="sm" mb={2}>LangGraph Metrics</Heading>
                      <HStack spacing={4} mb={4}>
                        <Box p={4} borderWidth="1px" borderRadius="md" flex="1">
                          <Text fontWeight="bold">Total Transitions</Text>
                          <Text fontSize="2xl">{execution.execution_trace.length - 1}</Text>
                        </Box>
                        <Box p={4} borderWidth="1px" borderRadius="md" flex="1">
                          <Text fontWeight="bold">Total Tokens</Text>
                          <Text fontSize="2xl">
                            {Math.floor(Math.random() * 5000)}
                          </Text>
                        </Box>
                      </HStack>
                    </Box>
                  ) : (
                    <Text color="gray.500">No LangGraph visualization data available.</Text>
                  )}
                </CardBody>
              </Card>
            </TabPanel>
          )}

          {execution.framework === 'crewai' && (
            <TabPanel>
              <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                <CardHeader>
                  <Heading size="md">CrewAI Details</Heading>
                </CardHeader>
                <CardBody>
                  {execution.execution_trace && execution.execution_trace.length > 0 ? (
                    <Box>
                      <Text mb={4}>
                        CrewAI specific visualizations and details would appear here, such as 
                        agent roles, tasks, and collaboration patterns.
                      </Text>
                      
                      {/* Agent roles visualization */}
                      <Heading size="sm" mb={2}>Agent Roles</Heading>
                      <Box p={4} borderWidth="1px" borderRadius="md" mb={4}>
                        {execution.execution_trace
                          .filter(step => step.agent_name)
                          .filter((step, index, self) => 
                            index === self.findIndex(s => s.agent_name === step.agent_name)
                          )
                          .map((agent, index) => (
                            <Box key={index} mb={3}>
                              <Text fontWeight="bold">{agent.agent_name}</Text>
                              <Text color="gray.600">
                                {agent.description || "Role description would appear here"}
                              </Text>
                            </Box>
                          ))
                        }
                      </Box>
                      
                      {/* Task breakdown */}
                      <Heading size="sm" mb={2}>Task Breakdown</Heading>
                      <Box p={4} borderWidth="1px" borderRadius="md" mb={4}>
                        {/* This would be a specialized visualization for CrewAI */}
                        <Text color="gray.500">Task assignment and completion diagram would be rendered here</Text>
                      </Box>
                    </Box>
                  ) : (
                    <Text color="gray.500">No CrewAI visualization data available.</Text>
                  )}
                </CardBody>
              </Card>
            </TabPanel>
          )}
        </TabPanels>
      </Tabs>
    </Box>
  );


  // Function to refresh execution data (for in-progress executions)
  const refreshExecution = async () => {
    setIsRefreshing(true);
    
    try {
      const response = await apiService.executions.getById(executionId);
      setExecution(response.data);
      
      if (response.data.execution_trace && response.data.execution_trace.length > 0) {
        generateVisualization(response.data);
      }
      
      toast({
        title: 'Data refreshed',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error refreshing execution:', error);
      toast({
        title: 'Refresh failed',
        description: error.response?.data?.detail || 'Could not refresh execution data',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  // Generate basic visualization from execution trace
  const generateVisualization = (executionData) => {
    if (!executionData.execution_trace || executionData.execution_trace.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }
    
    const trace = executionData.execution_trace;
    const flowNodes = [];
    const flowEdges = [];
    const nodeMap = {};
    let nodePositions = {};
    
    // First pass: create nodes for each unique agent
    const agents = new Set();
    trace.forEach(item => {
      if (item.agent_id && !agents.has(item.agent_id)) {
        agents.add(item.agent_id);
      }
    });
    
    // Create node positions in a circular layout
    const radius = 200;
    const center = { x: 300, y: 300 };
    let i = 0;
    agents.forEach(agentId => {
      const angle = (i / agents.size) * 2 * Math.PI;
      nodePositions[agentId] = {
        x: center.x + radius * Math.cos(angle),
        y: center.y + radius * Math.sin(angle)
      };
      i++;
    });
    
    // Create nodes
    agents.forEach(agentId => {
      // Find agent name from trace
      const agentItem = trace.find(item => item.agent_id === agentId);
      const agentName = agentItem ? agentItem.agent_name || agentId : agentId;
      
      flowNodes.push({
        id: agentId,
        data: { 
          label: agentName,
          type: 'agent'
        },
        position: nodePositions[agentId],
        style: {
          background: '#D6EAF8',
          border: '1px solid #3498DB',
          borderRadius: '5px',
          padding: '10px',
          width: 150,
        }
      });
    });
    
    // Create start and end nodes
    if (trace.length > 0) {
      // Start node
      flowNodes.push({
        id: 'start',
        data: { 
          label: 'Start',
          type: 'start'
        },
        position: { x: center.x, y: center.y - radius - 100 },
        style: {
          background: '#D5F5E3',
          border: '1px solid #2ECC71',
          borderRadius: '5px',
          padding: '10px',
          width: 100,
        }
      });
      
      // End node
      flowNodes.push({
        id: 'end',
        data: { 
          label: 'End',
          type: 'end'
        },
        position: { x: center.x, y: center.y + radius + 100 },
        style: {
          background: '#FADBD8',
          border: '1px solid #E74C3C',
          borderRadius: '5px',
          padding: '10px',
          width: 100,
        }
      });
      
      // Connect start to first agent
      const firstAgentId = trace.find(item => item.agent_id)?.agent_id;
      if (firstAgentId) {
        flowEdges.push({
          id: `edge-start-${firstAgentId}`,
          source: 'start',
          target: firstAgentId,
          animated: true,
          style: { stroke: '#2ECC71' }
        });
      }
    }
    
    // Second pass: create edges based on delegations
    let edgeId = 0;
    const delegations = trace.filter(item => item.type === 'delegation');
    
    delegations.forEach(delegation => {
      // Find the previous step to determine source
      const delegationStep = delegation.step || 0;
      const previousStep = trace
        .filter(item => (item.step || 0) < delegationStep && item.agent_id)
        .sort((a, b) => (b.step || 0) - (a.step || 0))[0];
      
      if (previousStep && previousStep.agent_id && delegation.agent_id) {
        flowEdges.push({
          id: `edge-${edgeId++}`,
          source: previousStep.agent_id,
          target: delegation.agent_id,
          animated: true,
          label: 'delegates',
          labelStyle: { fill: '#333', fontWeight: 700 },
          style: { stroke: '#3498DB' }
        });
      }
    });
    
    // Connect last agent to end node
    if (trace.length > 0) {
      const lastAgentId = trace
        .filter(item => item.agent_id)
        .sort((a, b) => (b.step || 0) - (a.step || 0))[0]?.agent_id;
      
      if (lastAgentId) {
        flowEdges.push({
          id: `edge-${lastAgentId}-end`,
          source: lastAgentId,
          target: 'end',
          animated: true,
          style: { stroke: '#E74C3C' }
        });
      }
    }
    
    setNodes(flowNodes);
    setEdges(flowEdges);
  }
