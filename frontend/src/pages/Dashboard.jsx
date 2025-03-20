// frontend/src/pages/Dashboard.jsx (updated with framework statistics)
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
    langgraph: { flows: 0, executions: 0, successRate: 0 },
    crewai: { flows: 0, executions: 0, successRate: 0 },
  });
  const [isLoading, setIsLoading] = useState(true);

  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        // In a real app, these would be actual API calls
        // Using mock data for now
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API delay

        // Mock data
        setRecentFlows([
          {
            id: '1',
            name: 'Research Assistant',
            created_at: '2025-03-12T14:25:00Z',
            agents: 4,
            framework: 'langgraph',
            type: 'Dynamic',
          },
          {
            id: '2',
            name: 'Code Generator',
            created_at: '2025-03-10T09:17:32Z',
            agents: 3,
            framework: 'langgraph',
            type: 'Dynamic',
          },
          {
            id: '3',
            name: 'Customer Support',
            created_at: '2025-03-05T16:42:19Z',
            agents: 5,
            framework: 'crewai',
            type: 'Dynamic',
          },
        ]);

        setRecentExecutions([
          {
            id: '101',
            flow_name: 'Research Assistant',
            framework: 'langgraph',
            status: 'completed',
            started_at: '2025-03-14T09:23:45Z',
            duration: '1m 42s',
            steps: 7,
          },
          {
            id: '102',
            flow_name: 'Code Generator',
            framework: 'langgraph',
            status: 'completed',
            started_at: '2025-03-14T08:15:22Z',
            duration: '2m 17s',
            steps: 9,
          },
          {
            id: '103',
            flow_name: 'Customer Support',
            framework: 'crewai',
            status: 'failed',
            started_at: '2025-03-13T17:05:11Z',
            duration: '0m 37s',
            steps: 3,
          },
          {
            id: '104',
            flow_name: 'Research Assistant',
            framework: 'langgraph',
            status: 'completed',
            started_at: '2025-03-13T14:52:37Z',
            duration: '1m 55s',
            steps: 8,
          },
        ]);

        setStats({
          totalFlows: 12,
          activeDeployments: 5,
          totalExecutions: 87,
          successRate: 94.3,
        });

        setExecutionStats([
          { date: '03/08', executions: 8, success: 7 },
          { date: '03/09', executions: 12, success: 11 },
          { date: '03/10', executions: 10, success: 9 },
          { date: '03/11', executions: 15, success: 14 },
          { date: '03/12', executions: 18, success: 17 },
          { date: '03/13', executions: 16, success: 15 },
          { date: '03/14', executions: 8, success: 8 },
        ]);

        // Mock framework-specific stats
        setFrameworkStats({
          langgraph: { 
            flows: 8, 
            executions: 62, 
            successRate: 96.8,
            color: 'blue',
            icon: FiActivity
          },
          crewai: { 
            flows: 3, 
            executions: 20, 
            successRate: 85.0,
            color: 'purple',
            icon: FiUsers
          },
          autogen: { 
            flows: 1, 
            executions: 5, 
            successRate: 100.0,
            color: 'green',
            icon: FiCpu
          },
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

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
        return FiActivity;
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

      {isLoading ? (
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
                    </CardBody>
                  </Card>

                  {/* Framework Usage Pie Chart */}
                  <FrameworkUsageWidget />
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
                            key={flow.id}
                            _hover={{ bg: 'gray.50' }}
                            cursor="pointer"
                            onClick={() => navigate(`/flows/${flow.id}`)}
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
                            <Td>{flow.agents}</Td>
                            <Td>{new Date(flow.created_at).toLocaleDateString()}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
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
                            <StatNumber>{frameworkStats.langgraph.flows}</StatNumber>
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
                            <StatNumber>{frameworkStats.langgraph.executions}</StatNumber>
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
                            <StatNumber>{frameworkStats.langgraph.successRate}%</StatNumber>
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
                    <Text>
                      LangGraph-specific visualizations and metrics would be displayed here.
                    </Text>
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
                            <StatNumber>{frameworkStats.crewai.flows}</StatNumber>
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
                            <StatNumber>{frameworkStats.crewai.executions}</StatNumber>
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
                            <StatNumber>{frameworkStats.crewai.successRate}%</StatNumber>
                            <StatHelpText>Last 7 days</StatHelpText>
                          </Box>
                        </Flex>
                      </Stat>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                {/* CrewAI specific content */}
                <Card bg={cardBg}
