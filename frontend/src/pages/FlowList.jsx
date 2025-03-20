// frontend/src/pages/FlowList.jsx (updated)
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
  Tag,
  useToast,
  useColorModeValue,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
} from '@chakra-ui/react';
import { FiPlus, FiPlay, FiEdit, FiTrash2, FiMoreVertical, FiDownload, FiServer } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const FlowList = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [flows, setFlows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [flowToDelete, setFlowToDelete] = useState(null);
  const cancelRef = React.useRef();

  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchFlows();
  }, []);

  const fetchFlows = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.flows.getAll();
      setFlows(response.data.items || []);
    } catch (error) {
      console.error('Error fetching flows:', error);
      toast({
        title: 'Error fetching flows',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (flowId) => {
    navigate(`/flows/${flowId}`);
  };

  const confirmDelete = (flow) => {
    setFlowToDelete(flow);
    onOpen();
  };

  const handleDelete = async () => {
    if (!flowToDelete) return;
    
    try {
      await apiService.flows.delete(flowToDelete.id);
      toast({
        title: 'Flow deleted',
        description: 'The flow has been successfully deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      // Remove from local state
      setFlows(flows.filter(flow => flow.id !== flowToDelete.id));
    } catch (error) {
      toast({
        title: 'Error deleting flow',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setFlowToDelete(null);
      onClose();
    }
  };

  const handleTestFlow = (flowId) => {
    navigate(`/flows/${flowId}/test`);
  };

  const handleDeployFlow = (flowId) => {
    navigate(`/deployments/new?flowId=${flowId}`);
  };

  const handleExportFlow = async (flowId, framework) => {
    try {
      const response = await apiService.flows.export(flowId, framework);
      
      // Create a blob with the exported flow
      const blob = new Blob([JSON.stringify(response.data.exported_config, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      // Create a temporary anchor element and trigger download
      const a = document.createElement('a');
      a.href = url;
      a.download = `flow-${flowId}-${framework}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        title: 'Flow exported',
        description: `Flow has been exported to ${framework} format`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error exporting flow',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
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
                <Th>Framework</Th>
                <Th>Agents</Th>
                <Th>Created</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {flows.map((flow) => (
                <Tr key={flow.id}>
                  <Td fontWeight="medium">{flow.name}</Td>
                  <Td>{flow.description}</Td>
                  <Td>
                    <Tag colorScheme={flow.framework === 'langgraph' ? 'blue' : 'purple'}>
                      {flow.framework}
                    </Tag>
                  </Td>
                  <Td><Badge>{flow.agents.length}</Badge></Td>
                  <Td>{new Date(flow.created_at).toLocaleDateString()}</Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        size="sm"
                        icon={<FiEdit />}
                        aria-label="Edit flow"
                        onClick={() => handleEdit(flow.id)}
                      />
                      <IconButton
                        size="sm"
                        icon={<FiPlay />}
                        colorScheme="green"
                        aria-label="Test flow"
                        onClick={() => handleTestFlow(flow.id)}
                      />
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          aria-label="More options"
                          icon={<FiMoreVertical />}
                          size="sm"
                          variant="ghost"
                        />
                        <MenuList>
                          <MenuItem 
                            icon={<FiServer />}
                            onClick={() => handleDeployFlow(flow.id)}
                          >
                            Deploy
                          </MenuItem>
                          <MenuItem 
                            icon={<FiDownload />}
                            onClick={() => handleExportFlow(flow.id, flow.framework)}
                          >
                            Export ({flow.framework})
                          </MenuItem>
                          <MenuItem 
                            icon={<FiTrash2 />}
                            color="red.500"
                            onClick={() => confirmDelete(flow)}
                          >
                            Delete
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Flow
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete the flow "{flowToDelete?.name}"? This action cannot be undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleDelete} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};

export default FlowList;
