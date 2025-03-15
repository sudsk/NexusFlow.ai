/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
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
  List,
  ListItem,
  Code,
  useToast,
  useColorModeValue,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
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
} from 'react-icons/fi';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';

const ExecutionViewer = () => {
  const { executionId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [execution, setExecution] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const codeBg = useColorModeValue('gray.50', 'gray.700');

  useEffect(() => {
    const fetchExecutionData = async () => {
      setIsLoading(true);
      try {
        // In a real app, this would be an actual API call
        // Using mock data for now
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API delay

        // Mock execution data
        const mockExecution = {
          id: executionId,
          flow_id: '1',
          flow_name: 'Research Assistant',
          status: 'completed',
          started_at: '2025-03-14T09:23:45Z',
          completed_at: '2025-03-14T09:25:27Z',
          duration: '1m 42s',
          steps: 7,
          execution_trace: [
            {
              type: 'start',
              timestamp: '2025-03-14T09:23:45Z',
              step: 1,
              input: { query: 'What are the environmental impacts of electric vehicles?' }
            },
            {
              type: 'agent_execution',
              agent_id: 'coordinator',
              agent_name: 'Research Coordinator',
              timestamp: '2025-03-14T09:23:47Z',
              step: 2,
              output: {
                content: 'I need to delegate this research task to gather information about electric vehicles.',
                metadata: {
                  decision: {
                    action: 'delegate',
                    target: 'researcher',
                    reasoning: 'Need to gather information first'
                  }
                }
              }
            },
            {
              type: 'delegation',
              agent_id: 'researcher',
              agent_name: 'Information Retriever',
              timestamp: '2025-03-14T09:23:52Z',
              step: 3,
              input: { query: 'Find information about environmental impacts of electric vehicles' }
            },
            {
              type: 'tool_execution',
              agent_id: 'researcher',
              agent_name: 'Information Retriever',
              timestamp: '2025-03-14T09:24:05Z',
              step: 4,
              decision: {
                tool_name: 'web_search',
                tool_params: {
                  query: 'environmental impacts electric vehicles battery production electricity sources'
                }
              },
              output: {
                results: [
                  { title: 'Environmental Impact of EVs', snippet: 'Electric vehicles generally produce fewer emissions than conventional vehicles...' },
                  { title: 'Battery Production Impact', snippet: 'The production of lithium-ion batteries can be energy-intensive...' }
                ]
              }
            },
            {
              type: 'agent_execution',
              agent_id: 'researcher',
              agent_name: 'Information Retriever',
              timestamp: '2025-03-14T09:24:32Z',
              step: 5,
              output: {
                content: 'Based on my research, here are the key environmental impacts of electric vehicles...',
                metadata: {
                  decision: {
                    action: 'delegate',
                    target: 'analyst',
                    reasoning: 'Need expert analysis of the information'
                  }
                }
              }
            },
            {
              type: 'delegation',
              agent_id: 'analyst',
              agent_name: 'Data Analyst',
              timestamp: '2025-03-14T09:24:45Z',
              step: 6,
              input: { query: 'Analyze environmental impact data for electric vehicles' }
            },
            {
              type: 'agent_execution',
              agent_id: 'analyst',
              agent_name: 'Data Analyst',
              timestamp: '2025-03-14T09:25:10Z',
              step: 7,
              output: {
                content: 'My analysis of the environmental impacts of electric vehicles shows...',
                metadata: {
                  decision: {
                    action: 'final',
                    reasoning: 'Analysis complete'
                  }
                }
              }
            }
          ],
          output: {
            content: 'Electric vehicles (EVs) have several environmental impacts, both positive and negative:\n\n' +
              '1. **Lower Operational Emissions**: EVs produce no tailpipe emissions, reducing air pollution in urban areas.\n\n' +
              '2. **Overall Emissions Depend on Electricity Source**: The environmental benefit varies based on how clean the electricity grid is. In regions powered by renewables, EVs are much cleaner.\n\n' +
              '3. **Battery Production**: Manufacturing EV batteries is energy-intensive and requires mining of materials like lithium, cobalt, and nickel, which has environmental impacts.\n\n' +
              '4. **Lifecycle Assessment**: Studies show that even when accounting for battery production, EVs typically have a lower lifetime carbon footprint than gasoline vehicles.\n\n' +
              '5. **Recycling Challenges**: Battery recycling infrastructure is still developing but will be crucial for sustainability.\n\n' +
              'In conclusion, while EVs aren\'t perfect, they represent a significant environmental improvement over conventional vehicles, especially as electricity grids become cleaner.'
          }
        };

        setExecution(mockExecution);

        // Create visualization nodes and edges
        const flowNodes = [];
        const flowEdges = [];
        let nodeMap = {};
        
        // Create nodes for each agent
        const agents = new Set();
        mockExecution.execution_trace.forEach(item => {
          if (item.agent_id && !agents.has(item.agent_id)) {
            agents.add(item.agent_id);
            flowNodes.push({
              id: item.agent_id,
              data: { label: item.agent_name },
              position: { x: 0, y: 0 }, // Positions would be calculated properly in a real app
              type: 'default'
            });
            nodeMap[item.agent_id] = flowNodes.length - 1;
          }
        });
        
        // Create edges based on delegations
        let edgeId = 0;
        mockExecution.execution_trace.forEach(item => {
          if (item.type === 'delegation' && item.agent_id) {
            const sourceId = mockExecution.execution_trace[item.step - 2]?.agent_id;
            if (sourceId) {
              flowEdges.push({
                id: `edge-${edgeId++}`,
                source: sourceId,
                target: item.agent_id,
                animated: true,
                label: 'delegates'
              });
            }
          }
        });
        
        setNodes(flowNodes);
        setEdges(flowEdges);
      } catch (error) {
        console.error('Error fetching execution data:', error);
        toast({
          title: 'Error loading execution data',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/executions');
      } finally {
        setIsLoading(false);
      }
    };

    fetchExecutionData();
  }, [executionId, navigate, toast]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      case 'running':
        return 'blue';
      default:
        return 'gray';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return FiCheck;
      case 'failed':
        return FiX;
      case 'running':
        return FiClock;
      default:
        return FiAlertCircle;
    }
  };

  const getStepIcon = (type) => {
    switch (type) {
      case 'agent_execution':
        return FiCpu;
      case 'delegation':
        return FiSend;
      case 'tool_execution':
        return FiTool;
      case 'start':
        return FiInfo;
      case 'complete':
        return FiCheck;
      default:
        return FiInfo;
    }
  };

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

  if (isLoading) {
    return (
      <Flex justify="center" align="center" height="500px">
        <Spinner size="xl" color="blue.500" />
      </Flex>
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
        <Button 
          leftIcon={<FiDownload />} 
          onClick={handleExportResults}
        >
          Export Results
        </Button>
      </Flex>

      {/* Execution Summary Card */}
      <Card mb={6} bg={cardBg} borderColor={borderColor} borderWidth="1px">
        <CardBody>
          <Flex direction={{ base: 'column', md: 'row' }} justify="space-between">
            <VStack align="start" spacing={2} mb={{ base: 4, md: 0 }}>
              <Heading size="md">{execution.flow_name}</Heading>
              <HStack>
                <Badge colorScheme={getStatusColor(execution.status)} px={2} py={1}>
                  <Flex align="center">
                    <Icon as={getStatusIcon(execution.status)} mr={1} />
                    {execution.status}
                  </Flex>
                </Badge>
                <Tag>Steps: {execution.steps}</Tag>
                <Tag>Duration: {execution.duration}</Tag>
              </HStack>
            </VStack>
            
            <VStack align={{ base: 'start', md: 'end' }} spacing={1}>
              <Text fontSize="sm" color="gray.500">
                Started at: {new Date(execution.started_at).toLocaleString()}
              </Text>
              {execution.completed_at && (
                <Text fontSize="sm" color="gray.500">
                  Completed at: {new Date(execution.completed_at).toLocaleString()}
                </Text>
              )}
              <Text fontSize="sm" color="gray.500">
                Flow ID: {execution.flow_id}
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
        </TabList>

        <TabPanels>
          {/* Results Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Heading size="md">Final Output</Heading>
              </CardHeader>
              <CardBody>
                <Box whiteSpace="pre-wrap">{execution.output.content}</Box>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Execution Trace Tab */}
          <TabPanel>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardHeader>
                <Heading size="md">Execution Steps</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  {execution.execution_trace.map((step, index) => (
                    <Box 
                      key={index} 
                      p={4} 
                      borderWidth="1px" 
                      borderRadius="md" 
                      borderColor={borderColor}
                    >
                      <HStack mb={2}>
                        <Badge>Step {step.step}</Badge>
                        <Icon as={getStepIcon(step.type)} />
                        <Text fontWeight="bold">{step.type}</Text>
                        {step.agent_name && (
                          <Tag colorScheme="blue">{step.agent_name}</Tag>
                        )}
                        <Text fontSize="sm" color="gray.500">
                          {new Date(step.timestamp).toLocaleTimeString()}
                        </Text>
                      </HStack>
                      
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
                            {JSON.stringify(step.input, null, 2)}
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
                            {JSON.stringify(step.decision, null, 2)}
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
                    </Box>
                  ))}
                </VStack>
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
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default ExecutionViewer;
