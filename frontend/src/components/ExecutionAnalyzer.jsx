// ExecutionAnalyzer.js - Component for analyzing execution data
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Badge, 
  Heading, 
  Divider,
  Card, 
  CardBody,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Tabs, 
  TabList, 
  TabPanels, 
  Tab, 
  TabPanel,
  Spinner,
  Button,
  useToast,
  Code,
  Tag,
  TagLabel
} from '@chakra-ui/react';
import { FiClock, FiTool, FiUser, FiArrowRight, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import { ResponsiveContainer, Sankey, Tooltip as RechartsTooltip } from 'recharts';

// Helper function to format timestamps
const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A';
  const date = new Date(timestamp);
  return date.toLocaleString();
};

// Helper to format duration
const formatDuration = (durationSeconds) => {
  if (!durationSeconds) return 'N/A';
  
  const minutes = Math.floor(durationSeconds / 60);
  const seconds = Math.floor(durationSeconds % 60);
  
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }
  return `${seconds}s`;
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

// Component for execution metadata
const ExecutionMetadata = ({ execution }) => {
  if (!execution) return null;
  
  return (
    <Card variant="outline" mb={4}>
      <CardBody>
        <HStack spacing={4} wrap="wrap">
          <Box minW="150px">
            <Text fontSize="sm" color="gray.500">Flow</Text>
            <Text fontWeight="medium">{execution.flow_name || 'Unknown'}</Text>
          </Box>
          
          <Box minW="150px">
            <Text fontSize="sm" color="gray.500">Framework</Text>
            <Text fontWeight="medium">{execution.framework}</Text>
          </Box>
          
          <Box minW="150px">
            <Text fontSize="sm" color="gray.500">Status</Text>
            <StatusBadge status={execution.status} />
          </Box>
          
          <Box minW="150px">
            <Text fontSize="sm" color="gray.500">Duration</Text>
            <HStack>
              <FiClock />
              <Text>{formatDuration(execution.duration_seconds)}</Text>
            </HStack>
          </Box>
          
          <Box minW="150px">
            <Text fontSize="sm" color="gray.500">Started</Text>
            <Text fontSize="sm">{formatTimestamp(execution.started_at)}</Text>
          </Box>
          
          <Box minW="150px">
            <Text fontSize="sm" color="gray.500">Completed</Text>
            <Text fontSize="sm">{formatTimestamp(execution.completed_at)}</Text>
          </Box>
        </HStack>
      </CardBody>
    </Card>
  );
};

// Component for displaying input data
const InputData = ({ input }) => {
  if (!input) return null;
  
  return (
    <Card variant="outline" mb={4}>
      <CardBody>
        <Heading size="sm" mb={2}>Input Data</Heading>
        <Code p={2} w="100%" display="block" whiteSpace="pre-wrap" borderRadius="md">
          {JSON.stringify(input, null, 2)}
        </Code>
      </CardBody>
    </Card>
  );
};

// Component for displaying result data
const ResultData = ({ result, error }) => {
  if (error) {
    return (
      <Card variant="outline" bg="red.50" mb={4}>
        <CardBody>
          <Heading size="sm" mb={2} color="red.500">Error</Heading>
          <Text color="red.500">{error}</Text>
        </CardBody>
      </Card>
    );
  }
  
  if (!result) return null;
  
  return (
    <Card variant="outline" mb={4}>
      <CardBody>
        <Heading size="sm" mb={2}>Result</Heading>
        {result.output && result.output.content ? (
          <Text p={2}>{result.output.content}</Text>
        ) : (
          <Code p={2} w="100%" display="block" whiteSpace="pre-wrap" borderRadius="md">
            {JSON.stringify(result, null, 2)}
          </Code>
        )}
      </CardBody>
    </Card>
  );
};

// Component for displaying execution trace
const ExecutionTrace = ({ trace }) => {
  if (!trace || trace.length === 0) return null;
  
  return (
    <Accordion allowMultiple defaultIndex={[0]}>
      {trace.map((step, index) => {
        // Determine step icon and color based on type
        let icon = <FiUser />;
        let tagColor = "blue";
        
        if (step.type === 'tool_execution') {
          icon = <FiTool />;
          tagColor = "purple";
        } else if (step.type === 'delegation') {
          icon = <FiArrowRight />;
          tagColor = "orange";
        } else if (step.type === 'complete') {
          icon = <FiCheckCircle />;
          tagColor = "green";
        } else if (step.type === 'error') {
          icon = <FiAlertCircle />;
          tagColor = "red";
        }
        
        return (
          <AccordionItem key={index}>
            <AccordionButton>
              <HStack flex="1" spacing={4} textAlign="left">
                <Tag colorScheme={tagColor} size="md">
                  <TagLabel>Step {step.step}</TagLabel>
                </Tag>
                {icon}
                <Text fontWeight="medium">
                  {step.type === 'agent_execution' && `Agent: ${step.agent_name || 'Unknown'}`}
                  {step.type === 'tool_execution' && `Tool: ${step.output?.metadata?.tool || 'Unknown'}`}
                  {step.type === 'delegation' && 'Delegation'}
                  {step.type === 'complete' && 'Completion'}
                  {step.type === 'error' && 'Error'}
                </Text>
                <Text fontSize="sm" color="gray.500">
                  {formatTimestamp(step.timestamp)}
                </Text>
              </HStack>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel pb={4}>
              {/* Input */}
              {step.input && (
                <Box mb={4}>
                  <Text fontWeight="medium" mb={1}>Input:</Text>
                  <Code p={2} w="100%" display="block" whiteSpace="pre-wrap" borderRadius="md">
                    {JSON.stringify(step.input, null, 2)}
                  </Code>
                </Box>
              )}
              
              {/* Output */}
              {step.output && (
                <Box mb={4}>
                  <Text fontWeight="medium" mb={1}>Output:</Text>
                  {step.output.content ? (
                    <Text p={2} bg="gray.50" borderRadius="md">{step.output.content}</Text>
                  ) : (
                    <Code p={2} w="100%" display="block" whiteSpace="pre-wrap" borderRadius="md">
                      {JSON.stringify(step.output, null, 2)}
                    </Code>
                  )}
                  
                  {/* Metadata if available */}
                  {step.output.metadata && (
                    <HStack mt={2} fontSize="sm" color="gray.500">
                      {step.output.metadata.model && (
                        <Text>Model: {step.output.metadata.model}</Text>
                      )}
                      {step.output.metadata.tool && (
                        <Text>Tool: {step.output.metadata.tool}</Text>
                      )}
                    </HStack>
                  )}
                </Box>
              )}
              
              {/* Decision for delegation steps */}
              {step.decision && (
                <Box mb={4}>
                  <Text fontWeight="medium" mb={1}>Decision:</Text>
                  <HStack spacing={4} mb={2}>
                    <Text>Action: {step.decision.action}</Text>
                    {step.decision.target && (
                      <Text>Target: {step.decision.target}</Text>
                    )}
                  </HStack>
                  {step.decision.reasoning && (
                    <Text p={2} bg="gray.50" borderRadius="md">{step.decision.reasoning}</Text>
                  )}
                </Box>
              )}
              
              {/* Error */}
              {step.error && (
                <Box mb={4}>
                  <Text fontWeight="medium" color="red.500" mb={1}>Error:</Text>
                  <Text color="red.500">{step.error}</Text>
                </Box>
              )}
            </AccordionPanel>
          </AccordionItem>
        );
      })}
    </Accordion>
  );
};

// Component for visualizing execution flow
const ExecutionFlow = ({ trace }) => {
  const [flowData, setFlowData] = useState({ nodes: [], links: [] });
  
  useEffect(() => {
    if (!trace || trace.length === 0) return;
    
    // Process trace to create Sankey diagram data
    const nodes = [];
    const links = [];
    const nodeMap = {};
    
    // Helper to get or create node index
    const getNodeIndex = (id, name, type) => {
      const nodeKey = `${type}-${id}`;
      if (nodeMap[nodeKey] === undefined) {
        nodeMap[nodeKey] = nodes.length;
        nodes.push({ name: name || id });
      }
      return nodeMap[nodeKey];
    };
    
    // Process trace steps to build graph
    for (let i = 0; i < trace.length - 1; i++) {
      const currentStep = trace[i];
      const nextStep = trace[i + 1];
      
      // Skip if this is a completion or error step
      if (currentStep.type === 'complete' || currentStep.type === 'error') continue;
      
      // Source node
      let sourceId, sourceName, sourceType;
      if (currentStep.type === 'agent_execution') {
        sourceId = currentStep.agent_id;
        sourceName = currentStep.agent_name;
        sourceType = 'agent';
      } else if (currentStep.type === 'tool_execution') {
        sourceId = currentStep.output?.metadata?.tool || `tool-${i}`;
        sourceName = currentStep.output?.metadata?.tool || 'Tool';
        sourceType = 'tool';
      } else if (currentStep.type === 'delegation') {
        sourceId = currentStep.agent_id;
        sourceName = currentStep.agent_name;
        sourceType = 'agent';
      }
      
      // Target node
      let targetId, targetName, targetType;
      if (nextStep.type === 'agent_execution') {
        targetId = nextStep.agent_id;
        targetName = nextStep.agent_name;
        targetType = 'agent';
      } else if (nextStep.type === 'tool_execution') {
        targetId = nextStep.output?.metadata?.tool || `tool-${i+1}`;
        targetName = nextStep.output?.metadata?.tool || 'Tool';
        targetType = 'tool';
      } else if (nextStep.type === 'complete') {
        targetId = 'complete';
        targetName = 'Complete';
        targetType = 'system';
      } else if (nextStep.type === 'error') {
        targetId = 'error';
        targetName = 'Error';
        targetType = 'system';
      }
      
      // Add link if we have valid source and target
      if (sourceId && targetId) {
        const sourceIndex = getNodeIndex(sourceId, sourceName, sourceType);
        const targetIndex = getNodeIndex(targetId, targetName, targetType);
        
        links.push({
          source: sourceIndex,
          target: targetIndex,
          value: 1, // All links have same weight for simplicity
        });
      }
    }
    
    setFlowData({ nodes, links });
  }, [trace]);
  
  if (!trace || trace.length === 0 || flowData.nodes.length === 0) {
    return (
      <Box textAlign="center" p={10}>
        <Text color="gray.500">No flow data available to visualize</Text>
      </Box>
    );
  }
  
  return (
    <Box h="400px" w="100%">
      <ResponsiveContainer width="100%" height="100%">
        <Sankey
          data={flowData}
          node={{
            onClick: (e) => console.log(e),
            fill: '#8884d8',
          }}
          link={{
            stroke: '#77c3ec',
          }}
          nodePadding={50}
          nodeWidth={10}
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        >
          <RechartsTooltip />
        </Sankey>
      </ResponsiveContainer>
    </Box>
  );
};

// Main execution analyzer component
const ExecutionAnalyzer = ({ executionData, loading, onRefresh }) => {
  const toast = useToast();
  
  if (loading) {
    return (
      <Box textAlign="center" p={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading execution data...</Text>
      </Box>
    );
  }
  
  if (!executionData) {
    return (
      <Box textAlign="center" p={10}>
        <Text color="gray.500">No execution data available</Text>
      </Box>
    );
  }
  
  const handleRefresh = () => {
    if (onRefresh) {
      toast({
        title: "Refreshing data",
        status: "info",
        duration: 3000,
        isClosable: true,
      });
      onRefresh();
    }
  };
  
  return (
    <VStack spacing={4} align="stretch">
      <HStack justify="space-between">
        <Heading size="lg">Execution Details</Heading>
        <Button onClick={handleRefresh} size="sm">Refresh</Button>
      </HStack>
      
      <Divider />
      
      <ExecutionMetadata execution={executionData} />
      
      <Tabs isFitted variant="enclosed">
        <TabList mb="1em">
          <Tab>Overview</Tab>
          <Tab>Execution Trace</Tab>
          <Tab>Flow Visualization</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <VStack spacing={4} align="stretch">
              <InputData input={executionData.input} />
              <ResultData 
                result={executionData.result} 
                error={executionData.error} 
              />
            </VStack>
          </TabPanel>
          <TabPanel>
            <ExecutionTrace trace={executionData.execution_trace} />
          </TabPanel>
          <TabPanel>
            <ExecutionFlow trace={executionData.execution_trace} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
};

export default ExecutionAnalyzer;
