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
  Button,
  HStack,
  Flex,
  Spinner,
  Text,
  Badge,
  useToast,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiPlus, FiPlay, FiEdit, FiTrash2 } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const FlowList = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [flows, setFlows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    const fetchFlows = async () => {
      setIsLoading(true);
      try {
        // In a real app, fetch flows from API
        // Mocking data for now
        const mockFlows = [
          {
            id: '1',
            name: 'Research Assistant',
            description: 'A flow for research tasks',
            created_at: '2025-03-12T14:25:00Z',
            updated_at: '2025-03-12T14:25:00Z',
            agents: 4,
          },
          {
            id: '2',
            name: 'Code Generator',
            description: 'Generates code from requirements',
            created_at: '2025-03-10T09:17:32Z',
            updated_at: '2025-03-10T09:17:32Z',
            agents: 3,
          },
          {
            id: '3',
            name: 'Customer Support',
            description: 'Handles customer queries automatically',
            created_at: '2025-03-05T16:42:19Z',
            updated_at: '2025-03-05T16:42:19Z',
            agents: 5,
          },
        ];
        
        setFlows(mockFlows);
      } catch (error) {
        console.error('Error fetching flows:', error);
        toast({
          title: 'Error fetching flows',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchFlows();
  }, [toast]);

  const handleEdit = (flowId) => {
    navigate(`/flows/${flowId}`);
  };

  const handleDelete = async (flowId) => {
    // In a real app, this would call API to delete
    toast({
      title: 'Flow deleted',
      description: 'The flow has been successfully deleted',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
    // Remove from local state
    setFlows(flows.filter(flow => flow.id !== flowId));
  };

  const handleTestFlow = (flowId) => {
    toast({
      title: 'Test started',
      description: 'Flow test has been initiated',
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Flows</Heading>
        <Button
          leftIcon={<FiPlus />}
          colorScheme="blue"
          onClick={() => navigate('/flows/new')}
        >
          Create Flow
        </Button>
      </Flex>

      {isLoading ? (
        <Flex justify="center" align="center" height="300px">
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : flows.length === 0 ? (
        <Box
          textAlign="center"
          py={10}
          px={6}
          borderWidth="1px"
          borderRadius="lg"
          borderColor={borderColor}
          bg={bgColor}
        >
          <Text mb={4}>No flows found</Text>
          <Button
            colorScheme="blue"
            onClick={() => navigate('/flows/new')}
          >
            Create Your First Flow
          </Button>
        </Box>
      ) : (
        <Box
          borderWidth="1px"
          borderRadius="lg"
          overflow="hidden"
          bg={bgColor}
          borderColor={borderColor}
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Description</Th>
                <Th>Created</Th>
                <Th>Agents</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {flows.map((flow) => (
                <Tr key={flow.id}>
                  <Td fontWeight="medium">{flow.name}</Td>
                  <Td>{flow.description}</Td>
                  <Td>{new Date(flow.created_at).toLocaleDateString()}</Td>
                  <Td><Badge>{flow.agents}</Badge></Td>
                  <Td>
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        leftIcon={<FiEdit />}
                        onClick={() => handleEdit(flow.id)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        leftIcon={<FiPlay />}
                        colorScheme="green"
                        onClick={() => handleTestFlow(flow.id)}
                      >
                        Test
                      </Button>
                      <Button
                        size="sm"
                        leftIcon={<FiTrash2 />}
                        colorScheme="red"
                        variant="ghost"
                        onClick={() => handleDelete(flow.id)}
                      >
                        Delete
                      </Button>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}
    </Box>
  );
};

export default FlowList;
