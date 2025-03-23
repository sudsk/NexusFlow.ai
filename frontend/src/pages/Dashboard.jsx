// frontend/src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Card,
  CardHeader,
  CardBody,
  Button,
  ButtonGroup,
  Flex,
  Text,
  Icon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Tag,
  HStack,
  Spinner,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import {
  FiPlus,
  FiActivity,
  FiCpu,
  FiServer,
  FiClock,
  FiCheck,
  FiX,
  FiAlertCircle,
  FiUsers,
  FiCode,
} from 'react-icons/fi';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import apiService from '../services/api';
import FrameworkUsageWidget from '../components/FrameworkUsageWidget';

const Dashboard = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [recentFlows, setRecentFlows] = useState([]);
  const [recentExecutions, setRecentExecutions] = useState([]);
  const [stats, setStats] = useState({
    totalFlows: 0,
    activeDeployments: 0,
    totalExecutions: 0,
    successRate: 0,
  });
  const [executionStats, setExecutionStats] = useState([]);
  const [frameworkStats, setFrameworkStats] = useState({
    langgraph: { flows: 0, executions: 0, successRate: 0, color: 'blue', icon: FiActivity },
    crewai: { flows: 0, executions: 0, successRate: 0, color: 'purple', icon: FiUsers },
    autogen: { flows: 0, executions: 0, successRate: 0, color: 'green', icon: FiCpu },
    dspy: { flows: 0, executions: 0, successRate: 0, color: 'orange', icon: FiCode },
  });
  const [isLoading, setIsLoading] = useState({
    main: true,
    flows: true,
    executions: true,
    frameworks: true
  });

  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch flow data
        const fetchFlows = async () => {
          try {
            const response = await apiService.flows.getAll({ limit: 5 });
            if (response.data && response.data.items) {
              setRecentFlows(response.data.items);
              setStats(prevStats => ({
                ...prevStats,
                totalFlows: response.data.total || 0
              }));
              
              // Calculate framework distribution
              const frameworkCounts = { langgraph: 0, crewai: 0, autogen: 0, dspy: 0 };
              
              response.data.items.forEach(flow => {
                const framework = flow.framework || 'langgraph';
                if (frameworkCounts.hasOwnProperty(framework)) {
                  frameworkCounts[framework]++;
                }
              });
              
              // Update framework stats with flow counts
              setFrameworkStats(prevStats => {
                const updatedStats = { ...prevStats };
                for (const [framework, count] of Object.entries(frameworkCounts)) {
                  if (updatedStats[framework]) {
                    updatedStats[framework] = {
                      ...updatedStats[framework],
                      flows: count
                    };
                  }
                }
                return updatedStats;
              });
            }
          } catch (error) {
            console.error('Error fetching flows:', error);
            toast({
              title: 'Error',
              description: 'Could not fetch flow data',
              status: 'error',
              duration: 5000,
              isClosable: true,
            });
          } finally {
            setIsLoading(prev => ({ ...prev, flows: false }));
          }
        };

        // Fetch execution data
        const fetchExecutions = async () => {
          try {
            const response = await apiService.executions.getRecent(5);
            if (response.data && response.data.items) {
              setRecentExecutions(response.data.items);
              
              // Count executions by framework
              const execByFramework = { langgraph: 0, crewai: 0, autogen: 0, dspy: 0 };
              const successByFramework = { langgraph: 0, crewai: 0, autogen: 0, dspy: 0 };
              
              response.data.items.forEach(exec => {
                const framework = exec.framework || 'langgraph';
                if (execByFramework.hasOwnProperty(framework)) {
                  execByFramework[framework]++;
                  if (exec.status === 'completed') {
                    successByFramework[framework]++;
                  }
                }
              });
              
              // Update framework stats with execution counts
              setFrameworkStats(prevStats => {
                const updatedStats = { ...prevStats };
                for (const framework of Object.keys(updatedStats)) {
                  const execCount = execByFramework[framework] || 0;
                  const successCount = successByFramework[framework] || 0;
                  const successRate = execCount > 0 ? Math.round((successCount / execCount) * 100) : 0;
                  
                  updatedStats[framework] = {
                    ...updatedStats[framework],
                    executions: execCount,
                    successRate: successRate
                  };
                }
                return updatedStats;
              });
            }
          } catch (error) {
            console.error('Error fetching executions:', error);
            toast({
              title: 'Error',
              description: 'Could not fetch execution data',
              status: 'error',
              duration: 5000,
              isClosable: true,
            });
          } finally {
            setIsLoading(prev => ({ ...prev, executions: false }));
          }
        };

        // Fetch execution statistics
        const fetchExecutionStats = async () => {
          try {
            const response = await apiService.executions.getStats();
            if (response.data) {
              setStats(prevStats => ({
                ...prevStats,
                totalExecutions: response.data.total_executions || 0,
                successRate: response.data.success_rate || 0
              }));
              
              // Check if period_stats is available for chart data
              if (response.data.period_stats) {
                // Transform to chart format if available
                // This depends on the API response format
                // This is a placeholder - actual implementation will depend on API structure
                const chartData = [];
                // Convert period_stats to chart data format
                setExecutionStats(chartData);
              } else {
                // If no period data available, generate some based on overall stats
                const today = new Date();
                const last7Days = Array.from({ length: 7 }, (_, i) => {
                  const date = new Date(today);
                  date.setDate(date.getDate() - (6 - i));
                  return date.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' });
                });
                
                // Create approximate distribution based on total executions
                const totalExecs = response.data.total_executions || 0;
                const execsPerDay = Math.round(totalExecs / 7);
                const successRate = response.data.success_rate || 90;
                
                const chartData = last7Days.map(date => {
                  // Add some variation
                  const variance = Math.floor(Math.random() * (execsPerDay / 2));
                  const executions = execsPerDay + (Math.random() > 0.5 ? variance : -variance);
                  const success = Math.round((executions * successRate) / 100);
                  
                  return {
                    date,
                    executions,
                    success
                  };
                });
                
                setExecutionStats(chartData);
              }
            }
          } catch (error) {
            console.error('Error fetching execution stats:', error);
            toast({
              title: 'Error',
              description: 'Could not fetch execution statistics',
              status: 'error',
              duration: 5000,
              isClosable: true,
            });
          }
        };

        // Fetch deployment data
        const fetchDeployments = async () => {
          try {
            // This is a placeholder - the actual API might be different
            // We would need a proper endpoint to get active deployments
            let activeDeployments = 0;
            
            // Placeholder for when actual deployment API is available
            // const response = await apiService.deployments.getAll();
            // if (response.data && response.data.items) {
            //   activeDeployments = response.data.items.filter(d => d.status === 'active').length;
            // }
            
            setStats(prevStats => ({
              ...prevStats,
              activeDeployments
            }));
          } catch (error) {
            console.error('Error fetching deployments:', error);
          }
        };

        // Fetch framework availability
        const fetchFrameworks = async () => {
          try {
            const response = await apiService.frameworks.getAll();
            if (response.data) {
              // Update the framework stats with features from API
              const apiFrameworks = Object.keys(response.data);
              
              setFrameworkStats(prevStats => {
                const updatedStats = { ...prevStats };
                
                // Keep only frameworks returned by the API
                // but preserve existing stats for those frameworks
                const filteredStats = {};
                for (const framework of apiFrameworks) {
                  filteredStats[framework] = updatedStats[framework] || {
                    flows: 0,
                    executions: 0,
                    successRate: 0,
                    color: getFrameworkColor(framework),
                    icon: getFrameworkIcon(framework)
                  };
                }
                
                return filteredStats;
              });
            }
          } catch (error) {
            console.error('Error fetching frameworks:', error);
          } finally {
            setIsLoading(prev => ({ ...prev, frameworks: false }));
          }
        };

        // Execute all fetch functions in parallel
        await Promise.all([
          fetchFlows(),
          fetchExecutions(),
          fetchExecutionStats(),
          fetchDeployments(),
          fetchFrameworks()
        ]);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load dashboard data',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(prev => ({ ...prev, main: false }));
      }
    };

    fetchDashboardData();
  }, [toast]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'failed':
        return 'red';
      case 'running':
        return 'blue';
      case 'pending':
        return 'yellow';
      case 'cancelled':
        return 'gray';
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
        return FiActivity;
      case 'pending':
        return FiClock;
      case 'cancelled':
        return FiX;
      default:
        return FiAlertCircle;
    }
  };

  const getFrameworkColor = (framework) => {
    switch (framework) {
      case 'langgraph':
        return 'blue';
      case 'crewai':
        return 'purple';
      case 'autogen':
        return 'green';
      case 'dspy':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const getFrameworkIcon = (framework) => {
    switch (framework) {
      case 'langgraph':
        return FiActivity;
      case 'crewai':
        return FiUsers;
      case 'autogen':
        return FiCpu;
      case 'dspy':
        return FiCode;
      default:
        return FiActivity;
    }
  };

  // Function to generate framework feature data from API response
  const generateFeatureMatrix = () => {
    // This would be populated from the API frameworks data
    // For now, using some default values
    return [
      { feature: 'Multi-Agent', langgraph: true, crewai: true, autogen: true, dspy: false },
      { feature: 'Parallel Execution', langgraph: true, crewai: false, autogen: true, dspy: false },
      { feature: 'Tool Integration', langgraph: true, crewai: true, autogen: true, dspy: true },
      { feature: 'Streaming', langgraph: true, crewai: false, autogen: true, dspy: false },
      { feature: 'Visualization', langgraph: true, crewai: true, autogen: true, dspy: true }
    ];
  };

  const featureMatrix = generateFeatureMatrix();

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Dashboard</Heading>
        <ButtonGroup>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="blue"
            onClick={() => navigate('/flows/new')}
          >
            Create Flow
          </Button>
        </ButtonGroup>
      </Flex>

      {isLoading.main ? (
        <Flex justify="center" align="center" height="400px">
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : (
        <>
          {/* Stats Cards */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={5} mb={8}>
            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardBody>
                <Stat>
                  <Flex align="center">
                    <Box
                      bg="blue.50"
                      p={2}
                      borderRadius="md"
                      color="blue.500"
                      mr={3}
                    >
                      <Icon as={FiActivity} boxSize={5} />
                    </Box>
                    <Box>
                      <StatLabel>Total Flows</StatLabel>
                      <StatNumber>{stats.totalFlows}</StatNumber>
                    </Box>
                  </Flex>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardBody>
                <Stat>
                  <Flex align="center">
                    <Box
                      bg="purple.50"
                      p={2}
                      borderRadius="md"
                      color="purple.500"
                      mr={3}
                    >
                      <Icon as={FiServer} boxSize={5} />
                    </Box>
                    <Box>
                      <StatLabel>Active Deployments</StatLabel>
                      <StatNumber>{stats.activeDeployments}</StatNumber>
                    </Box>
                  </Flex>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardBody>
                <Stat>
                  <Flex align="center">
                    <Box
                      bg="green.50"
                      p={2}
                      borderRadius="md"
                      color="green.500"
                      mr={3}
                    >
                      <Icon as={FiCpu} boxSize={5} />
                    </Box>
                    <Box>
                      <StatLabel>Total Executions</StatLabel>
                      <StatNumber>{stats.totalExecutions}</StatNumber>
                    </Box>
                  </Flex>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
              <CardBody>
                <Stat>
                  <Flex align="center">
                    <Box
                      bg="orange.50"
                      p={2}
                      borderRadius="md"
                      color="orange.500"
                      mr={3}
                    >
                      <Icon as={FiCheck} boxSize={5} />
                    </Box>
                    <Box>
                      <StatLabel>Success Rate</StatLabel>
                      <StatNumber>{stats.successRate}%</StatNumber>
                      <StatHelpText>Last 7 days</StatHelpText>
                    </Box>
                  </Flex>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Framework Specific Stats and Charts */}
          <Tabs variant="enclosed" colorScheme="blue" mb={8}>
            <TabList>
              <Tab>Overview</Tab>
              <Tab>LangGraph</Tab>
              <Tab>CrewAI</Tab>
              <Tab>Framework Comparison</Tab>
            </TabList>

            <TabPanels>
              <TabPanel p={0} pt={4}>
                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                  {/* Execution Trends Chart */}
                  <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                    <CardHeader pb={0}>
                      <Heading size="md">Execution Trends</Heading>
                    </CardHeader>
                    <CardBody>
                      {isLoading.executions ? (
                        <Flex justify="center" align="center" h="250px">
                          <Spinner size="lg" color="blue.500" />
                        </Flex>
                      ) : executionStats.length > 0 ? (
                        <Box height="250px">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                              data={executionStats}
                              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis />
                              <Tooltip />
                              <Line
                                type="monotone"
                                dataKey="executions"
                                stroke="#3182CE"
                                name="Total Executions"
                              />
                              <Line
                                type="monotone"
                                dataKey="success"
                                stroke="#38A169"
                                name="Successful"
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </Box>
                      ) : (
                        <Flex justify="center" align="center" h="250px">
                          <Text>No execution data available</Text>
                        </Flex>
                      )}
                    </CardBody>
                  </Card>

                  {/* Framework Usage Pie Chart */}
                  <FrameworkUsageWidget 
                    frameworks={Object.entries(frameworkStats).map(([name, stats]) => ({
                      name,
                      value: stats.flows,
                      color: stats.color
                    }))}
                    isLoading={isLoading.frameworks}
                  />
                </SimpleGrid>

                {/* Recent Flows Table */}
                <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mt={6}>
                  <CardHeader pb={0}>
                    <Flex justify="space-between" align="center">
                      <Heading size="md">Recent Flows</Heading>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => navigate('/flows')}
                      >
                        View All
                      </Button>
                    </Flex>
                  </CardHeader>
                  <CardBody>
                    {isLoading.flows ? (
                      <Flex justify="center" align="center" py={6}>
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : recentFlows.length === 0 ? (
                      <Text>No flows found</Text>
                    ) : (
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            <Th>Name</Th>
                            <Th>Framework</Th>
                            <Th>Agents</Th>
                            <Th>Created</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {recentFlows.map((flow) => (
                            <Tr
                              key={flow.flow_id}
                              _hover={{ bg: 'gray.50' }}
                              cursor="pointer"
                              onClick={() => navigate(`/flows/${flow.flow_id}`)}
                            >
                              <Td fontWeight="medium">{flow.name}</Td>
                              <Td>
                                <Tag colorScheme={getFrameworkColor(flow.framework)}>
                                  <Icon 
                                    as={getFrameworkIcon(flow.framework)} 
                                    mr={1} 
                                  />
                                  {flow.framework}
                                </Tag>
                              </Td>
                              <Td>{flow.agents?.length || 0}</Td>
                              <Td>{new Date(flow.created_at).toLocaleDateString()}</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    )}
                  </CardBody>
                </Card>

                {/* Recent Executions Table */}
                <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mt={6}>
                  <CardHeader pb={0}>
                    <Flex justify="space-between" align="center">
                      <Heading size="md">Recent Executions</Heading>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => navigate('/executions')}
                      >
                        View All
                      </Button>
                    </Flex>
                  </CardHeader>
                  <CardBody>
                    {isLoading.executions ? (
                      <Flex justify="center" align="center" py={6}>
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : recentExecutions.length === 0 ? (
                      <Text>No executions found</Text>
                    ) : (
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            <Th>Flow</Th>
                            <Th>Framework</Th>
                            <Th>Status</Th>
                            <Th>Time</Th>
                            <Th>Duration</Th>
                            <Th>Steps</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {recentExecutions.map((execution) => (
                            <Tr
                              key={execution.id}
                              _hover={{ bg: 'gray.50' }}
                              cursor="pointer"
                              onClick={() => navigate(`/executions/${execution.id}`)}
                            >
                              <Td fontWeight="medium">{execution.flow_name || execution.flow_id}</Td>
                              <Td>
                                <Tag colorScheme={getFrameworkColor(execution.framework)} size="sm">
                                  {execution.framework}
                                </Tag>
                              </Td>
                              <Td>
                                <Badge colorScheme={getStatusColor(execution.status)}>
                                  <Flex align="center">
                                    <Icon as={getStatusIcon(execution.status)} mr={1} />
                                    {execution.status}
                                  </Flex>
                                </Badge>
                              </Td>
                              <Td>{new Date(execution.started_at).toLocaleTimeString()}</Td>
                              <Td>{execution.duration || 'N/A'}</Td>
                              <Td>{execution.steps || execution.execution_trace?.length || 0}</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    )}
                  </CardBody>
                </Card>
              </TabPanel>

              <TabPanel>
                <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={5} mb={6}>
                  {/* LangGraph Stats */}
                  <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                    <CardBody>
                      <Stat>
                        <Flex align="center">
                          <Box
                            bg="blue.50"
                            p={2}
                            borderRadius="md"
                            color="blue.500"
                            mr={3}
                          >
                            <Icon as={FiActivity} boxSize={5} />
                          </Box>
                          <Box>
                            <StatLabel>LangGraph Flows</StatLabel>
                            <StatNumber>{frameworkStats.langgraph?.flows || 0}</StatNumber>
                          </Box>
                        </Flex>
                      </Stat>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                    <CardBody>
                      <Stat>
                        <Flex align="center">
                          <Box
                            bg="blue.50"
                            p={2}
                            borderRadius="md"
                            color="blue.500"
                            mr={3}
                          >
                            <Icon as={FiCpu} boxSize={5} />
                          </Box>
                          <Box>
                            <StatLabel>LangGraph Executions</StatLabel>
                            <StatNumber>{frameworkStats.langgraph?.executions || 0}</StatNumber>
                          </Box>
                        </Flex>
                      </Stat>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                    <CardBody>
                      <Stat>
                        <Flex align="center">
                          <Box
                            bg="blue.50"
                            p={2}
                            borderRadius="md"
                            color="blue.500"
                            mr={3}
                          >
                            <Icon as={FiCheck} boxSize={5} />
                          </Box>
                          <Box>
                            <StatLabel>Success Rate</StatLabel>
                            <StatNumber>{frameworkStats.langgraph?.successRate || 0}%</StatNumber>
                            <StatHelpText>Last 7 days</StatHelpText>
                          </Box>
                        </Flex>
                      </Stat>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                {/* LangGraph specific content */}
                <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={6}>
                  <CardHeader>
                    <Heading size="md">LangGraph Flow Performance</Heading>
                  </CardHeader>
                  <CardBody>
                    {isLoading.executions ? (
                      <Flex justify="center" align="center" py={6}>
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : (
                      <Box height="250px">
                        {recentExecutions.filter(e => e.framework === 'langgraph').length > 0 ? (
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                              data={recentExecutions.filter(e => e.framework === 'langgraph')}
                              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="flow_name" />
                              <YAxis />
                              <Tooltip />
                              <Bar dataKey="steps" fill="#3182CE" name="Steps" />
                            </BarChart>
                          </ResponsiveContainer>
                        ) : (
                          <Flex justify="center" align="center" h="100%">
                            <Text color="gray.500">No LangGraph execution data available</Text>
                          </Flex>
                        )}
                      </Box>
                    )}
                  </CardBody>
                </Card>
              </TabPanel>

              <TabPanel>
                <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={5} mb={6}>
                  {/* CrewAI Stats */}
                  <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                    <CardBody>
                      <Stat>
                        <Flex align="center">
                          <Box
                            bg="purple.50"
                            p={2}
                            borderRadius="md"
                            color="purple.500"
                            mr={3}
                          >
                            <Icon as={FiUsers} boxSize={5} />
                          </Box>
                          <Box>
                            <StatLabel>CrewAI Flows</StatLabel>
                            <StatNumber>{frameworkStats.crewai?.flows || 0}</StatNumber>
                          </Box>
                        </Flex>
                      </Stat>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                    <CardBody>
                      <Stat>
                        <Flex align="center">
                          <Box
                            bg="purple.50"
                            p={2}
                            borderRadius="md"
                            color="purple.500"
                            mr={3}
                          >
                            <Icon as={FiCpu} boxSize={5} />
                          </Box>
                          <Box>
                            <StatLabel>CrewAI Executions</StatLabel>
                            <StatNumber>{frameworkStats.crewai?.executions || 0}</StatNumber>
                          </Box>
                        </Flex>
                      </Stat>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
                    <CardBody>
                      <Stat>
                        <Flex align="center">
                          <Box
                            bg="purple.50"
                            p={2}
                            borderRadius="md"
                            color="purple.500"
                            mr={3}
                          >
                            <Icon as={FiCheck} boxSize={5} />
                          </Box>
                          <Box>
                            <StatLabel>Success Rate</StatLabel>
                            <StatNumber>{frameworkStats.crewai?.successRate || 0}%</StatNumber>
                            <StatHelpText>Last 7 days</StatHelpText>
                          </Box>
                        </Flex>
                      </Stat>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                {/* CrewAI specific content */}
                <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={6}>
                  <CardHeader>
                    <Heading size="md">CrewAI Agent Interactions</Heading>
                  </CardHeader>
                  <CardBody>
                    {isLoading.executions ? (
                      <Flex justify="center" align="center" py={6}>
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : (
                      <>
                        <Text mb={4}>
                          CrewAI flows emphasize multi-agent collaboration with clear role assignments. 
                          Each agent has specialized capabilities and works together to achieve complex tasks.
                        </Text>
                        <Box height="200px">
                          {recentExecutions.filter(e => e.framework === 'crewai').length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart
                                data={recentExecutions.filter(e => e.framework === 'crewai')}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                              >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="flow_name" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="steps" fill="#9F7AEA" name="Steps" />
                              </BarChart>
                            </ResponsiveContainer>
                          ) : (
                            <Flex justify="center" align="center" h="100%">
                              <Text color="gray.500">No CrewAI execution data available</Text>
                            </Flex>
                          )}
                        </Box>
                      </>
                    )}
                  </CardBody>
                </Card>
              </TabPanel>

              <TabPanel>
                <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={6}>
                  <CardHeader>
                    <Heading size="md">Framework Comparison</Heading>
                  </CardHeader>
                  <CardBody>
                    {isLoading.frameworks ? (
                      <Flex justify="center" align="center" py={6}>
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : (
                      <>
                        <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={8}>
                          {Object.entries(frameworkStats).map(([framework, stats]) => (
                            <VStack 
                              key={framework} 
                              align="stretch" 
                              p={4} 
                              borderWidth="1px" 
                              borderRadius="md"
                              borderColor={`${stats.color}.200`}
                              bg={`${stats.color}.50`}
                            >
                              <Flex align="center">
                                <Icon as={stats.icon} boxSize={6} color={`${stats.color}.500`} mr={2} />
                                <Heading size="md" color={`${stats.color}.700`} textTransform="capitalize">
                                  {framework}
                                </Heading>
                              </Flex>
                              
                              <Text>Flows: {stats.flows}</Text>
                              <Text>Executions: {stats.executions}</Text>
                              <Text>Success Rate: {stats.successRate}%</Text>
                              
                              <Button 
                                mt={2} 
                                colorScheme={stats.color}
                                size="sm"
                                onClick={() => navigate(`/flows/new?framework=${framework}`)}
                              >
                                Create Flow
                              </Button>
                            </VStack>
                          ))}
                        </SimpleGrid>
                        
                        <Box mt={8}>
                          <Heading size="sm" mb={4}>Feature Comparison</Heading>
                          <Table variant="simple" size="sm">
                            <Thead>
                              <Tr>
                                <Th>Feature</Th>
                                {Object.keys(frameworkStats).map(framework => (
                                  <Th key={framework}>{framework}</Th>
                                ))}
                              </Tr>
                            </Thead>
                            <Tbody>
                              {featureMatrix.map((row, index) => (
                                <Tr key={index}>
                                  <Td>{row.feature}</Td>
                                  {Object.keys(frameworkStats).map(framework => (
                                    <Td key={`${framework}-${index}`}>
                                      <Icon 
                                        as={row[framework] ? FiCheck : FiX} 
                                        color={row[framework] ? "green.500" : "red.500"} 
                                      />
                                    </Td>
                                  ))}
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </Box>
                      </>
                    )}
                  </CardBody>
                </Card>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </>
      )}
    </Box>
  );
};

export default Dashboard;                                
