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
  CardBody,
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
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    failed: 0,
    running: 0,
    successRate: 0
  });
  const [filter, setFilter] = useState({
    framework: '',
    status: '',
    query: '',
  });
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBgColor = useColorModeValue('gray.50', 'gray.700');  
  
  // Helper function to get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'running': return 'blue';
      case 'pending': return 'orange';
      case 'cancelled': return 'gray';
      default: return 'gray';
    }
  };
  
  // Helper function to get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return FiCheck;
      case 'failed': return FiX;
      case 'running': case 'pending': return FiClock;
      case 'cancelled': return FiX;
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
  };
  
  const fetchExecutions = async () => {
    setIsLoading(true);
    try {
      // Fetch recent executions from the API
      const response = await apiService.executions.getRecent(20);
      
      if (response.data && response.data.items) {
        setExecutions(response.data.items);
        
        // Calculate stats
        const executionData = response.data.items;
        const completedCount = executionData.filter(e => e.status === 'completed').length;
        const failedCount = executionData.filter(e => e.status === 'failed').length;
        const runningCount = executionData.filter(e => e.status === 'running' || e.status === 'pending').length;
        const successRate = executionData.length > 0 
          ? Math.round((completedCount / (completedCount + failedCount)) * 100) 
          : 0;
          
        setStats({
          total: executionData.length,
          completed: completedCount,
          failed: failedCount,
          running: runningCount,
          successRate: successRate
        });
      } else {
        // Handle empty or unexpected response format
        setExecutions([]);
        setStats({
          total: 0,
          completed: 0,
          failed: 0,
          running: 0,
          successRate: 0
        });
        toast({
          title: 'Warning',
          description: 'Received empty or unexpected data format from server',
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      }
    } catch (error) {
      console.error('Error fetching executions:', error);
      toast({
        title: 'Error fetching executions',
        description: error.message || 'Failed to fetch executions from server',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setExecutions([]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchExecutionStats = async () => {
    try {
      // Fetch execution statistics from the API
      const response = await apiService.executions.getStats();
      
      if (response.data) {
        setStats({
          total: response.data.total_executions || 0,
          completed: response.data.completed_executions || 0,
          failed: response.data.failed_executions || 0,
          running: response.data.running_executions || 0,
          successRate: response.data.success_rate || 0
        });
      }
    } catch (error) {
      console.error('Error fetching execution stats:', error);
      // We'll use the calculated stats from executionData if this fails
    }
  };
  
  const handleRefresh = () => {
    fetchExecutions();
    fetchExecutionStats();
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
  
  const handleDeleteExecution = async (executionId) => {
    try {
      await apiService.executions.delete(executionId);
      
      toast({
        title: 'Execution deleted',
        description: `Execution ${executionId} has been deleted`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // Remove from state
      setExecutions(executions.filter(exec => exec.id !== executionId));
      
      // Update stats
      setStats({
        ...stats,
        total: stats.total - 1
      });
    } catch (error) {
      console.error('Error deleting execution:', error);
      toast({
        title: 'Error deleting execution',
        description: error.message || 'Failed to delete execution',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  const handleDownloadResults = (execution) => {
    // Create a JSON blob with execution results
    const data = {
      id: execution.id,
      flow_name: execution.flow_name || `Flow ${execution.flow_id}`,
      framework: execution.framework,
      input: execution.input,
      result: execution.result || { error: execution.error },
      started_at: execution.started_at,
      completed_at: execution.completed_at,
      status: execution.status,
      steps: execution.steps || execution.execution_trace?.length || 0
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
  
  useEffect(() => {
    // Fetch both executions and stats when component mounts
    fetchExecutions();
    fetchExecutionStats();
  }, []);
  
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
    
    // Query filter (search in flow_id, flow_name and input)
    if (filter.query) {
      const query = filter.query.toLowerCase();
      const flowIdMatch = exec.flow_id?.toLowerCase().includes(query);
      const flowNameMatch = exec.flow_name?.toLowerCase().includes(query);
      const inputMatch = typeof exec.input?.query === 'string' && 
                         exec.input.query.toLowerCase().includes(query);
      
      return flowIdMatch || flowNameMatch || inputMatch;
    }
    
    return true;
  });

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
                <option value="cancelled">Cancelled</option>
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
                <Th>Flow ID</Th>
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
                  _hover={{ bg: hoverBgColor }}
                  cursor="pointer"
                  onClick={() => handleViewExecution(execution.id)}
                >
                  <Td fontWeight="medium">{execution.flow_name || execution.flow_id}</Td>
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
                  <Td>{execution.duration || 'N/A'}</Td>
                  <Td>{execution.steps || execution.execution_trace?.length || 0}</Td>
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
                          isDisabled={execution.status === 'running' || execution.status === 'pending'}
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
        <HStack spacing={6} flexWrap="wrap">
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Total Executions:</Text>
            <Text>{stats.total}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Completed:</Text>
            <Text>{stats.completed}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Failed:</Text>
            <Text>{stats.failed}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Running:</Text>
            <Text>{stats.running}</Text>
          </Flex>
          
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Success Rate:</Text>
            <Text>{stats.successRate}%</Text>
          </Flex>
        </HStack>
      </Card>
    </Box>
  );
};

export default ExecutionsPage;
