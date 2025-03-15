import React, { useState } from 'react';
import {
  Box,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  HStack,
  VStack,
  Badge,
  Text,
  Code,
  Button,
  Icon,
  Flex,
  useColorModeValue,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Select,
} from '@chakra-ui/react';
import {
  FiCpu,
  FiTool,
  FiSend,
  FiInfo,
  FiCheck,
  FiX,
  FiSearch,
  FiFilter,
  FiChevronUp,
  FiChevronDown,
} from 'react-icons/fi';

const ExecutionTraceViewer = ({ executionTrace }) => {
  const [filter, setFilter] = useState('all');
  const [expandedSteps, setExpandedSteps] = useState([]);
  const [sort, setSort] = useState('chronological');
  const [groupBy, setGroupBy] = useState('none');
  
  const codeBg = useColorModeValue('gray.50', 'gray.700');
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Filter the execution trace based on selected filter
  const filteredTrace = React.useMemo(() => {
    if (!executionTrace || !Array.isArray(executionTrace)) return [];
    
    if (filter === 'all') return executionTrace;
    
    return executionTrace.filter(step => {
      switch (filter) {
        case 'agent_execution':
          return step.type === 'agent_execution';
        case 'tool_execution':
          return step.type === 'tool_execution';
        case 'delegation':
          return step.type === 'delegation';
        case 'error':
          return step.error || (step.output && step.output.error);
        default:
          return true;
      }
    });
  }, [executionTrace, filter]);
  
  // Sort the filtered trace
  const sortedTrace = React.useMemo(() => {
    if (!filteredTrace || !Array.isArray(filteredTrace)) return [];
    
    const sorted = [...filteredTrace];
    
    switch (sort) {
      case 'chronological':
        return sorted.sort((a, b) => (a.step || 0) - (b.step || 0));
      case 'reverse':
        return sorted.sort((a, b) => (b.step || 0) - (a.step || 0));
      case 'agent':
        return sorted.sort((a, b) => {
          if (!a.agent_name && !b.agent_name) return 0;
          if (!a.agent_name) return 1;
          if (!b.agent_name) return -1;
          return a.agent_name.localeCompare(b.agent_name);
        });
      case 'type':
        return sorted.sort((a, b) => {
          if (!a.type && !b.type) return 0;
          if (!a.type) return 1;
          if (!b.type) return -1;
          return a.type.localeCompare(b.type);
        });
      default:
        return sorted;
    }
  }, [filteredTrace, sort]);
  
  // Group the sorted trace if needed
  const groupedTrace = React.useMemo(() => {
    if (groupBy === 'none') return { default: sortedTrace };
    
    const groups = {};
    
    sortedTrace.forEach(step => {
      let groupKey;
      
      switch (groupBy) {
        case 'agent':
          groupKey = step.agent_name || 'Unknown Agent';
          break;
        case 'type':
          groupKey = step.type || 'Unknown Type';
          break;
        default:
          groupKey = 'default';
      }
      
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      
      groups[groupKey].push(step);
    });
    
    return groups;
  }, [sortedTrace, groupBy]);
  
  // Handler for expanding/collapsing steps
  const toggleStep = (stepIndex) => {
    if (expandedSteps.includes(stepIndex)) {
      setExpandedSteps(expandedSteps.filter(i => i !== stepIndex));
    } else {
      setExpandedSteps([...expandedSteps, stepIndex]);
    }
  };
  
  // Toggle all steps
  const toggleAllSteps = () => {
    if (expandedSteps.length === sortedTrace.length) {
      setExpandedSteps([]);
    } else {
      setExpandedSteps(sortedTrace.map((_, index) => index));
    }
  };
  
  // Helper to get icon for step type
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
  
  // Helper to format step content
  const formatStepContent = (content) => {
    if (typeof content === 'object') {
      if (content.content) {
        return content.content;
      }
      return JSON.stringify(content, null, 2);
    }
    return content;
  };
  
  // Render grouped trace
  const renderGroupedTrace = () => {
    return Object.entries(groupedTrace).map(([groupName, steps], groupIndex) => (
      <Box key={groupIndex} mb={4}>
        {groupBy !== 'none' && (
          <Text fontWeight="bold" fontSize="lg" mb={2}>
            {groupName}
          </Text>
        )}
        
        <Accordion allowMultiple>
          {steps.map((step, stepIndex) => renderTraceStep(step, stepIndex))}
        </Accordion>
      </Box>
    ));
  };
  
  // Render individual step
  const renderTraceStep = (step, index) => {
    const isExpanded = expandedSteps.includes(index);
    const StepIcon = getStepIcon(step.type);
    
    return (
      <AccordionItem
        key={index}
        bg={cardBg}
        mb={2}
        borderWidth="1px"
        borderRadius="md"
        borderColor={borderColor}
      >
        <AccordionButton 
          py={2}
          onClick={() => toggleStep(index)}
          _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
        >
          <Box flex="1" textAlign="left">
            <HStack spacing={2}>
              <Badge colorScheme="blue">Step {step.step || index + 1}</Badge>
              <Icon as={StepIcon} color="gray.500" />
              <Text fontWeight="medium">{step.type}</Text>
              {step.agent_name && (
                <Badge colorScheme="purple">{step.agent_name}</Badge>
              )}
              <Text fontSize="sm" color="gray.500">
                {step.timestamp && new Date(step.timestamp).toLocaleTimeString()}
              </Text>
            </HStack>
          </Box>
          <AccordionIcon />
        </AccordionButton>
        
        <AccordionPanel pb={4}>
          <VStack align="stretch" spacing={3}>
            {step.input && (
              <Box>
                <Text fontWeight="bold" fontSize="sm">Input:</Text>
                <Code 
                  p={2} 
                  bg={codeBg} 
                  borderRadius="md" 
                  w="100%" 
                  display="block"
                  whiteSpace="pre-wrap"
                  maxH="200px"
                  overflowY="auto"
                >
                  {typeof step.input === 'object' 
                    ? JSON.stringify(step.input, null, 2) 
                    : step.input}
                </Code>
              </Box>
            )}
            
            {step.decision && (
              <Box>
                <Text fontWeight="bold" fontSize="sm">Decision:</Text>
                <Table size="sm" variant="simple" bg={codeBg} borderRadius="md">
                  <Tbody>
                    {step.decision.action && (
                      <Tr>
                        <Td fontWeight="medium">Action</Td>
                        <Td>{step.decision.action}</Td>
                      </Tr>
                    )}
                    {step.decision.target && (
                      <Tr>
                        <Td fontWeight="medium">Target</Td>
                        <Td>{step.decision.target}</Td>
                      </Tr>
                    )}
                    {step.decision.tool_name && (
                      <Tr>
                        <Td fontWeight="medium">Tool</Td>
                        <Td>{step.decision.tool_name}</Td>
                      </Tr>
                    )}
                    {step.decision.reasoning && (
                      <Tr>
                        <Td fontWeight="medium">Reasoning</Td>
                        <Td>{step.decision.reasoning}</Td>
                      </Tr>
                    )}
                  </Tbody>
                </Table>
                
                {step.decision.tool_params && (
                  <Box mt={2}>
                    <Text fontWeight="bold" fontSize="sm">Tool Parameters:</Text>
                    <Code 
                      p={2} 
                      bg={codeBg} 
                      borderRadius="md" 
                      w="100%" 
                      display="block"
                    >
                      {JSON.stringify(step.decision.tool_params, null, 2)}
                    </Code>
                  </Box>
                )}
              </Box>
            )}
            
            {step.output && (
              <Box>
                <Text fontWeight="bold" fontSize="sm">Output:</Text>
                <Code 
                  p={2} 
                  bg={codeBg} 
                  borderRadius="md" 
                  w="100%" 
                  display="block" 
                  whiteSpace="pre-wrap"
                  maxH="300px"
                  overflowY="auto"
                >
                  {formatStepContent(step.output)}
                </Code>
              </Box>
            )}
            
            {step.error && (
              <Box>
                <Text fontWeight="bold" fontSize="sm" color="red.500">Error:</Text>
                <Code 
                  p={2} 
                  bg="red.50" 
                  color="red.500"
                  borderRadius="md" 
                  w="100%" 
                  display="block"
                >
                  {step.error}
                </Code>
              </Box>
            )}
          </VStack>
        </AccordionPanel>
      </AccordionItem>
    );
  };
  
  if (!executionTrace || !Array.isArray(executionTrace) || executionTrace.length === 0) {
    return (
      <Flex h="200px" justify="center" align="center">
        <Text color="gray.500">No execution trace available</Text>
      </Flex>
    );
  }
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={4} wrap="wrap" gap={2}>
