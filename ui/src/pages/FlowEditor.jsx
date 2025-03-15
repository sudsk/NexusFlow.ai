import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Flex,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  IconButton,
  Divider,
  Skeleton,
  useToast,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
} from '@chakra-ui/react';
import { FiHome, FiActivity, FiCpu, FiDatabase, FiCode, FiSearch } from 'react-icons/fi';
import { useParams, useNavigate, Link } from 'react-router-dom';
import FlowBuilder from '../components/FlowBuilder';
import axios from 'axios';

const FlowEditor = () => {
  const { flowId } = useParams();
  const isNewFlow = !flowId;
  const navigate = useNavigate();
  const toast = useToast();
  const [flowData, setFlowData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch flow data if editing an existing flow
  useEffect(() => {
    if (!isNewFlow) {
      const fetchFlowData = async () => {
        setIsLoading(true);
        try {
          const response = await axios.get(`/api/nexusflow/flows/${flowId}`);
          setFlowData(response.data);
        } catch (error) {
          toast({
            title: 'Error fetching flow',
            description: error.response?.data?.detail || 'Could not load flow data',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          // Redirect to flows list on error
          navigate('/flows');
        } finally {
          setIsLoading(false);
        }
      };

      fetchFlowData();
    }
  }, [flowId, isNewFlow, navigate, toast]);

  // Agent types that can be dragged onto the canvas
  const agentTypes = [
    { type: 'coordinator', name: 'Coordinator', icon: FiActivity, description: 'Coordinates other agents' },
    { type: 'researcher', name: 'Researcher', icon: FiSearch, description: 'Retrieves information' },
    { type: 'analyst', name: 'Analyst', icon: FiDatabase, description: 'Analyzes data' },
    { type: 'coder', name: 'Coder', icon: FiCode, description: 'Generates code' },
    { type: 'reasoner', name: 'Reasoner', icon: FiCpu, description: 'General reasoning' },
  ];

  // Handle flow save
  const handleFlowSave = (savedFlowId, flowConfig) => {
    // If this was a new flow, redirect to the edit page for the new flow
    if (isNewFlow) {
      navigate(`/flows/${savedFlowId}`);
    }
  };

  const onDragStart = (event, agentType) => {
    event.dataTransfer.setData('application/agentType', agentType);
    event.dataTransfer.effectAllowed = 'move';
  };

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
          <BreadcrumbLink as={Link} to="/flows">
            Flows
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>
          <BreadcrumbLink>{isNewFlow ? 'New Flow' : flowData?.name || 'Edit Flow'}</BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>

      <Flex mb={6}>
        <Heading size="lg">
          {isNewFlow ? 'Create New Flow' : `Edit Flow: ${flowData?.name || ''}`}
        </Heading>
      </Flex>

      <Flex>
        {/* Agent palette */}
        <VStack
          spacing={4}
          align="stretch"
          width="220px"
          mr={4}
          pr={2}
          overflowY="auto"
          maxHeight="calc(100vh - 200px)"
        >
          <Text fontWeight="bold" fontSize="sm" color="gray.500">
            DRAG AGENTS TO CANVAS
          </Text>
          <Divider />
          
          {agentTypes.map((agent) => (
            <Card
              key={agent.type}
              variant="outline"
              cursor="grab"
              onDragStart={(event) => onDragStart(event, agent.type)}
              draggable
              _hover={{ borderColor: 'brand.500', shadow: 'md' }}
            >
              <CardBody>
                <HStack spacing={3}>
                  <Box
                    borderRadius="md"
                    bg="brand.50"
                    p={2}
                    color="brand.500"
                  >
                    <agent.icon size={18} />
                  </Box>
                  <VStack spacing={0} align="start">
                    <Text fontWeight="bold" fontSize="sm">
                      {agent.name}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      {agent.description}
                    </Text>
                  </VStack>
                </HStack>
              </CardBody>
            </Card>
          ))}
        </VStack>

        {/* Flow builder */}
        <Box flex="1">
          {isLoading ? (
            <Skeleton height="600px" />
          ) : (
            <FlowBuilder
              flowId={flowId}
              initialData={flowData}
              onSave={handleFlowSave}
            />
          )}
        </Box>
      </Flex>
    </Box>
  );
};

export default FlowEditor;
