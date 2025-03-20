// frontend/src/pages/ExecutionsPage.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Flex,
  HStack,
  Icon,
  Text,
  Spinner,
  Button,
  Select,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputLeftElement,
  Card,
  CardHeader,
  CardBody,
  Tooltip,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  useColorModeValue,
  useToast
} from '@chakra-ui/react';
import { 
  FiRefreshCw, 
  FiSearch, 
  FiFilter, 
  FiCheck, 
  FiX, 
  FiActivity, 
  FiUsers, 
  FiCpu, 
  FiCode,
  FiClock,
  FiMoreVertical,
  FiEye,
  FiDownload,
  FiTrash2
} from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const ExecutionsPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [executions, setExecutions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState({
    framework: '',
    status: '',
    query: '',
  });
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  useEffect(() => {
    fetchExecutions();
  }, []);
  
  const fetchExecutions = async () => {
    setIsLoading(true);
    try {
      // In a real implementation, this would use the API service
      // For now, let's use mock data
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
      
      // Mock data
      const mockExecutions = [
        {
          id: '101',
          flow_id: '1',
          flow_name: 'Research Assistant',
          framework: 'langgraph',
          status: 'completed',
          started_at: '2025-03-14T09:23:45Z',
          completed_at: '2025-03-14T09:25:27Z',
          duration: '1m 42s',
          steps: 7,
          input: { query: "What are the latest developments in AI?" },
          result: { output: "Here's a summary of the latest AI developments..." }
        },
        {
          id: '102',
          flow_id: '2',
          flow_name: 'Code Generator',
          framework: 'langgraph',
          status: 'completed',
          started_at: '2025-03-14T08:15:22Z',
          completed_at: '2025-03-14T08:17:39Z',
          duration: '2m 17s',
          steps: 9,
          input: { query: "Generate a React component for a dashboard" },
          result: { output: "Here's a React dashboard component..." }
        },
        {
          id: '103',
          flow_id: '3',
          flow_name: 'Customer Support',
          framework: 'crewai',
          status: 'failed',
          started_at: '2025-03-13T17:05:11Z',
          completed_at: '2025-03-13T17:05:48Z',
          duration: '0m 37s',
          steps: 3,
          input: { query: "I need help with my account" },
          error: "Tool execution error: API rate limit exceeded"
        },
        {
          id: '104',
          flow_id: '1',
          flow_name: 'Research Assistant',
          framework: 'langgraph',
          status: 'completed',
          started_at: '2025-03-13T14:52:37Z',
          completed_at: '2025-03-13T14:54:32Z',
          duration: '1m 55s',
          steps: 8,
          input: { query: "Summarize recent climate research" },
          result: { output: "Recent climate research has focused on..." }
        },
        {
          id: '105',
          flow_id: '4',
          flow_name: 'Data Analyzer',
          framework: 'autogen',
          status: 'running',
          started_at: '2025-03-14T10:12:15Z',
          completed_at: null,
          duration: '30m+',
          steps: 12,
          input: { query: "Analyze this financial dataset and provide insights" }
        },
        {
          id: '106',
          flow_id: '3',
          flow_name: 'Customer Support',
          framework: 'crewai',
          status: 'completed',
          started_at: '2025-03-12T11:34:22Z',
          completed_at: '2025-03-12T11:37:45Z',
          duration: '3m 23s',
          steps: 5,
          input: { query: "How do I reset my password?" },
          result: { output: "You can reset your password by..." }
        }
      ];
      
      setExecutions(mockExecutions);
    } catch (error) {
      console.error('Error fetching executions:', error);
      toast({
        title: 'Error fetching executions',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Executions</Heading>
        
        <HStack>
          <Button
            leftIcon={<FiRefreshCw />}
            colorScheme="blue"
            variant="outline"
            onClick={handleRefresh}
            isLoading={isLoading}
          >
            Refresh
          </Button>
        </HStack>
      </Flex>
      
      {/* Filters */}
      <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={6}>
        <CardBody>
          <Flex flexWrap="wrap" gap={4} align="flex-end">
            <FormControl maxW="180px">
              <FormLabel fontSize="sm">Framework</FormLabel>
              <Select 
                size="sm"
                value={filter.framework}
                onChange={(e) => handleFilterChange('framework', e.target.value)}
              >
                <option value="">All Frameworks</option>
                <option value="langgraph">LangGraph</option>
                <option value="crewai">CrewAI</option>
                <option value="autogen">AutoGen</option>
                <option value="dspy">DSPy</option>
              </Select>
            </FormControl>
            
            <FormControl maxW="180px">
              <FormLabel fontSize="sm">Status</FormLabel>
              <Select 
                size="sm"
                value={filter.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="running">Running</option>
                <option value="pending">Pending</option>
              </Select>
            </FormControl>
            
            <FormControl maxW="300px">
              <FormLabel fontSize="sm">Search</FormLabel>
              <InputGroup size="sm">
                <InputLeftElement pointerEvents="none">
                  <FiSearch color="gray.300" />
                </InputLeftElement>
                <Input 
                  placeholder="Search flows or inputs..." 
                  value={filter.query}
                  onChange={(e) => handleFilterChange('query', e.target.value)}
                />
              </InputGroup>
            </FormControl>
            
            <Button 
              leftIcon={<FiFilter />} 
              size="sm"
              onClick={() => setFilter({ framework: '', status: '', query: '' })}
            >
              Clear Filters
            </Button>
          </Flex>
        </CardBody>
      </Card>
      
      {/* Executions Table */}
      {isLoading ? (
        <Flex justify="center" align="center" h="300px">
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : filteredExecutions.length === 0 ? (
        <Flex direction="column" align="center" justify="center" py={10}>
          <Text fontSize="lg" mb={4}>No executions found matching your filters</Text>
          <Button 
            leftIcon={<FiFilter />}
            onClick={() => setFilter({ framework: '', status: '', query: '' })}
          >
            Clear Filters
          </Button>
        </Flex>
      ) : (
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Flow Name</Th>
                <Th>Framework</Th>
                <Th>Status</Th>
                <Th>Started</Th>
                <Th>Duration</Th>
                <Th>Steps</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredExecutions.map((execution) => (
                <Tr 
                  key={execution.id} 
                  _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
                  cursor="pointer"
                  onClick={() => handleViewExecution(execution.id)}
                >
                  <Td fontWeight="medium">{execution.flow_name}</Td>
                  <Td>
                    <HStack>
                      <Icon as={getFrameworkIcon(execution.framework)} color={`${getFrameworkColor(execution.framework)}.500`} />
                      <Text>{execution.framework}</Text>
                    </HStack>
                  </Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(execution.status)}>
                      <Flex align="center">
                        <Icon as={getStatusIcon(execution.status)} mr={1} />
                        {execution.status}
                      </Flex>
                    </Badge>
                  </Td>
                  <Td>{new Date(execution.started_at).toLocaleString()}</Td>
                  <Td>{execution.duration}</Td>
                  <Td>{execution.steps}</Td>
                  <Td onClick={(e) => e.stopPropagation()}>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="sm"
                      />
                      <MenuList>
                        <MenuItem 
                          icon={<FiEye />}
                          onClick={() => handleViewExecution(execution.id)}
                        >
                          View Details
                        </MenuItem>
                        <MenuItem 
                          icon={<FiDownload />}
                          onClick={() => handleDownloadResults(execution)}
                          isDisabled={execution.status === 'running' || execution.status === 'pending'}
                        >
                          Download Results
                        </MenuItem>
                        <MenuItem 
                          icon={<FiTrash2 />}
                          onClick={() => handleDeleteExecution(execution.id)}
                          color="red.500"
                        >
                          Delete
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Card>
      )}
      
      {/* Stats Summary Card */}
      <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mt={6} p={4}>
        <HStack spacing={6}>
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Total Executions:</Text>
            <Text>{executions.length}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Completed:</Text>
            <Text>{executions.filter(e => e.status === 'completed').length}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Failed:</Text>
            <Text>{executions.filter(e => e.status === 'failed').length}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Running:</Text>
            <Text>{executions.filter(e => e.status === 'running').length}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Success Rate:</Text>
            <Text>
              {executions.length > 0 
                ? Math.round((executions.filter(e => e.status === 'completed').length / executions.length) * 100) 
                : 0}%
            </Text>
          </Flex>
        </HStack>
      </Card>
    </Box>
  );
  
  const handleRefresh = () => {
    fetchExecutions();
  };
  
  const handleFilterChange = (field, value) => {
    setFilter({
      ...filter,
      [field]: value
    });
  };
  
  const handleViewExecution = (executionId) => {
    navigate(`/executions/${executionId}`);
  };
  
  const handleDeleteExecution = (executionId) => {
    // In a real implementation, this would call the API
    toast({
      title: 'Execution deleted',
      description: `Execution ${executionId} has been deleted`,
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
    
    // Remove from state
    setExecutions(executions.filter(exec => exec.id !== executionId));
  };
  
  const handleDownloadResults = (execution) => {
    // Create a JSON blob with execution results
    const data = {
      id: execution.id,
      flow_name: execution.flow_name,
      framework: execution.framework,
      input: execution.input,
      result: execution.result || { error: execution.error },
      started_at: execution.started_at,
      completed_at: execution.completed_at,
      status: execution.status,
      steps: execution.steps
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create a link and trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = `execution-${execution.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Results downloaded',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };
  
  // Apply filters to executions
  const filteredExecutions = executions.filter(exec => {
    // Framework filter
    if (filter.framework && exec.framework !== filter.framework) {
      return false;
    }
    
    // Status filter
    if (filter.status && exec.status !== filter.status) {
      return false;
    }
    
    // Query filter (search in flow_name and input)
    if (filter.query) {
      const query = filter.query.toLowerCase();
      const flowNameMatch = exec.flow_name.toLowerCase().includes(query);
      const inputMatch = exec.input?.query?.toLowerCase().includes(query);
      
      return flowNameMatch || inputMatch;
    }
    
    return true;
  });
  
  // Helper function to get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'running': return 'blue';
      case 'pending': return 'orange';
      default: return 'gray';
    }
  };
  
  // Helper function to get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return FiCheck;
      case 'failed': return FiX;
      case 'running': case 'pending': return FiClock;
      default: return FiActivity;
    }
  };
  
  // Helper function to get framework icon
  const getFrameworkIcon = (framework) => {
    switch (framework) {
      case 'langgraph': return FiActivity;
      case 'crewai': return FiUsers;
      case 'autogen': return FiCpu;
      case 'dspy': return FiCode;
      default: return FiActivity;
    }
  };
  
  // Helper function to get framework color
  const getFrameworkColor = (framework) => {
    switch (framework) {
      case 'langgraph': return 'blue';
      case 'crewai': return 'purple';
      case 'autogen': return 'green';
      case 'dspy': return 'orange';
      default: return 'gray';
    }
  }
