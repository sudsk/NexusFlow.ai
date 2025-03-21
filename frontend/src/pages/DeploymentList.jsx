// frontend/src/pages/DeploymentList.jsx
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
  Flex,
  Spinner,
  Text,
  Badge,
  Tag,
  IconButton,
  HStack,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useToast,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  Card,
  CardBody,
  useColorModeValue,
  Code,
  Switch,
} from '@chakra-ui/react';
import { 
  FiPlus, 
  FiEdit, 
  FiTrash2, 
  FiMoreVertical, 
  FiServer, 
  FiPlayCircle, 
  FiPauseCircle,
  FiCopy,
  FiExternalLink
} from 'react-icons/fi';
import { useNavigate, useLocation } from 'react-router-dom';
import apiService from '../services/api';

const DeploymentList = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const flowIdParam = searchParams.get('flowId');
  
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const [deployments, setDeployments] = useState([]);
  const [flows, setFlows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentDeployment, setCurrentDeployment] = useState(null);
  const [formData, setFormData] = useState({
    flow_id: '',
    name: '',
    version: 'v1',
    settings: {
      rate_limit: 10,
      timeout_seconds: 30,
      log_level: 'info',
      cors_enabled: true,
    }
  });
  
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchDeployments();
    fetchFlows();
    
    // If flowId is provided in the URL, pre-select it in the form
    if (flowIdParam) {
      setFormData(prev => ({
        ...prev,
        flow_id: flowIdParam
      }));
    }
  }, [flowIdParam]);

  const fetchDeployments = async () => {
    setIsLoading(true);
    try {
      // In a real implementation, this would call the API
      // const response = await apiService.deployments.getAll();
      // setDeployments(response.data.items || []);
      
      // Mock data for development
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const mockDeployments = [
        {
          id: 'd1',
          flow_id: '1',
          flow_name: 'Research Assistant',
          name: 'Research Assistant API',
          version: 'v1',
          status: 'active',
          endpoint_url: 'https://api.nexusflow.ai/api/flows/d1/execute',
          created_at: '2025-03-12T14:30:00Z',
          updated_at: '2025-03-12T14:30:00Z',
          settings: {
            rate_limit: 10,
            timeout_seconds: 30,
            log_level: 'info',
            cors_enabled: true,
          }
        },
        {
          id: 'd2',
          flow_id: '2',
          flow_name: 'Code Generator',
          name: 'Code Generator API',
          version: 'v2',
          status: 'active',
          endpoint_url: 'https://api.nexusflow.ai/api/flows/d2/execute',
          created_at: '2025-03-10T11:15:00Z',
          updated_at: '2025-03-14T09:30:00Z',
          settings: {
            rate_limit: 5,
            timeout_seconds: 60,
            log_level: 'debug',
            cors_enabled: true,
          }
        },
        {
          id: 'd3',
          flow_id: '3',
          flow_name: 'Customer Support',
          name: 'Customer Support API',
          version: 'v1',
          status: 'inactive',
          endpoint_url: 'https://api.nexusflow.ai/api/flows/d3/execute',
          created_at: '2025-03-05T16:45:00Z',
          updated_at: '2025-03-13T10:20:00Z',
          settings: {
            rate_limit: 20,
            timeout_seconds: 45,
            log_level: 'info',
            cors_enabled: false,
          }
        },
      ];
      
      setDeployments(mockDeployments);
    } catch (error) {
      console.error('Error fetching deployments:', error);
      toast({
        title: 'Error fetching deployments',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchFlows = async () => {
    try {
      // In a real implementation, this would call the API
      // const response = await apiService.flows.getAll();
      // setFlows(response.data.items || []);
      
      // Mock data for development
      const mockFlows = [
        {
          id: '1',
          name: 'Research Assistant',
          framework: 'langgraph',
        },
        {
          id: '2',
          name: 'Code Generator',
          framework: 'langgraph',
        },
        {
          id: '3',
          name: 'Customer Support',
          framework: 'crewai',
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
    }
  };

  const handleNewDeployment = () => {
    setCurrentDeployment(null);
    setFormData({
      flow_id: flowIdParam || '',
      name: '',
      version: 'v1',
      settings: {
        rate_limit: 10,
        timeout_seconds: 30,
        log_level: 'info',
        cors_enabled: true,
      }
    });
    onOpen();
  };

  const handleEditDeployment = (deployment) => {
    setCurrentDeployment(deployment);
    setFormData({
      flow_id: deployment.flow_id,
      name: deployment.name,
      version: deployment.version,
      settings: {
        ...deployment.settings
      }
    });
    onOpen();
  };

  const handleDeleteDeployment = async (deploymentId) => {
    try {
      // In a real implementation, this would call the API
      // await apiService.deployments.delete(deploymentId);
      
      // Remove from UI
      setDeployments(deployments.filter(d => d.id !== deploymentId));
      
      toast({
        title: 'Deployment deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error deleting deployment:', error);
      toast({
        title: 'Error deleting deployment',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleToggleStatus = async (deployment) => {
    const newStatus = deployment.status === 'active' ? 'inactive' : 'active';
    
    try {
      // In a real implementation, this would call the API
      // await apiService.deployments.update(deployment.id, { status: newStatus });
      
      // Update UI
      setDeployments(deployments.map(d => 
        d.id === deployment.id ? { ...d, status: newStatus } : d
      ));
      
      toast({
        title: `Deployment ${newStatus === 'active' ? 'activated' : 'deactivated'}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error updating deployment status:', error);
      toast({
        title: 'Error updating deployment',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleCopyEndpoint = (url) => {
    navigator.clipboard.writeText(url);
    toast({
      title: 'Endpoint URL copied',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };

  const handleFormChange = (field, value) => {
    if (field.includes('.')) {
      // Handle nested fields in settings
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleSaveDeployment = async () => {
    // Set name from flow if not provided
    if (!formData.name && formData.flow_id) {
      const selectedFlow = flows.find(f => f.id === formData.flow_id);
      if (selectedFlow) {
        formData.name = `${selectedFlow.name} API`;
      }
    }
    
    // Validate form
    if (!formData.flow_id || !formData.name) {
      toast({
        title: 'Missing required fields',
        description: 'Flow and name are required',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    try {
      if (currentDeployment) {
        // Update existing deployment
        // In a real implementation, this would call the API
        // await apiService.deployments.update(currentDeployment.id, formData);
        
        // Update UI
        setDeployments(deployments.map(d => 
          d.id === currentDeployment.id ? { 
            ...d, 
            ...formData,
            updated_at: new Date().toISOString()
          } : d
        ));
        
        toast({
          title: 'Deployment updated',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        // Create new deployment
        // In a real implementation, this would call the API
        // const response = await apiService.deployments.create(formData);
        
        // Mock response
        const flowName = flows.find(f => f.id === formData.flow_id)?.name || 'Unknown Flow';
        const newDeployment = {
          id: `d${deployments.length + 1}`,
          flow_id: formData.flow_id,
          flow_name: flowName,
          name: formData.name,
          version: formData.version,
          status: 'active',
          endpoint_url: `https://api.nexusflow.ai/api/flows/d${deployments.length + 1}/execute`,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          settings: formData.settings
        };
        
        setDeployments([...deployments, newDeployment]);
        
        toast({
          title: 'Deployment created',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
      
      onClose();
    } catch (error) {
      console.error('Error saving deployment:', error);
      toast({
        title: 'Error saving deployment',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Deployments</Heading>
        <Button
          leftIcon={<FiPlus />}
          colorScheme="blue"
          onClick={handleNewDeployment}
        >
          Create Deployment
        </Button>
      </Flex>

      {isLoading ? (
        <Flex justify="center" align="center" height="300px">
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : deployments.length === 0 ? (
        <Card bg={bgColor} borderColor={borderColor} borderWidth="1px">
          <CardBody textAlign="center" py={10}>
            <Text mb={4}>No deployments found</Text>
            <Button
              colorScheme="blue"
              onClick={handleNewDeployment}
            >
              Create Your First Deployment
            </Button>
          </CardBody>
        </Card>
      ) : (
        <Card bg={bgColor} borderColor={borderColor} borderWidth="1px">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Flow</Th>
                <Th>Version</Th>
                <Th>Status</Th>
                <Th>Endpoint</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {deployments.map((deployment) => (
                <Tr key={deployment.id}>
                  <Td fontWeight="bold">{deployment.name}</Td>
                  <Td>{deployment.flow_name}</Td>
                  <Td>{deployment.version}</Td>
                  <Td>
                    <Badge 
                      colorScheme={deployment.status === 'active' ? 'green' : 'red'}
                      variant={deployment.status === 'active' ? 'solid' : 'outline'}
                    >
                      {deployment.status}
                    </Badge>
                  </Td>
                  <Td maxW="300px" isTruncated>
                    <HStack>
                      <Text isTruncated>{deployment.endpoint_url}</Text>
                      <IconButton
                        icon={<FiCopy />}
                        aria-label="Copy endpoint URL"
                        size="xs"
                        variant="ghost"
                        onClick={() => handleCopyEndpoint(deployment.endpoint_url)}
                      />
                    </HStack>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        icon={deployment.status === 'active' ? <FiPauseCircle /> : <FiPlayCircle />}
                        aria-label={deployment.status === 'active' ? 'Deactivate' : 'Activate'}
                        size="sm"
                        variant="ghost"
                        colorScheme={deployment.status === 'active' ? 'red' : 'green'}
                        onClick={() => handleToggleStatus(deployment)}
                      />
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          icon={<FiMoreVertical />}
                          variant="ghost"
                          size="sm"
                        />
                        <MenuList>
                          <MenuItem 
                            icon={<FiEdit />}
                            onClick={() => handleEditDeployment(deployment)}
                          >
                            Edit
                          </MenuItem>
                          <MenuItem 
                            icon={<FiExternalLink />}
                            onClick={() => window.open(deployment.endpoint_url, '_blank')}
                          >
                            Test Endpoint
                          </MenuItem>
                          <MenuItem 
                            icon={<FiTrash2 />}
                            color="red.500"
                            onClick={() => handleDeleteDeployment(deployment.id)}
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
        </Card>
      )}

      {/* Deployment Form Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {currentDeployment ? 'Edit Deployment' : 'Create Deployment'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl mb={4} isRequired>
              <FormLabel>Flow</FormLabel>
              <Select
                value={formData.flow_id}
                onChange={(e) => handleFormChange('flow_id', e.target.value)}
                placeholder="Select a flow"
                isDisabled={!!currentDeployment}
              >
                {flows.map((flow) => (
                  <option key={flow.id} value={flow.id}>
                    {flow.name} ({flow.framework})
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <FormControl mb={4} isRequired>
              <FormLabel>Deployment Name</FormLabel>
              <Input
                value={formData.name}
                onChange={(e) => handleFormChange('name', e.target.value)}
                placeholder="Customer Support API"
              />
            </FormControl>
            
            <FormControl mb={4}>
              <FormLabel>Version</FormLabel>
              <Input
                value={formData.version}
                onChange={(e) => handleFormChange('version', e.target.value)}
                placeholder="v1"
              />
            </FormControl>
            
            <Heading size="sm" mb={2}>Settings</Heading>
            
            <FormControl mb={4}>
              <FormLabel>Rate Limit (requests per minute)</FormLabel>
              <Input
                type="number"
                value={formData.settings.rate_limit}
                onChange={(e) => handleFormChange('settings.rate_limit', parseInt(e.target.value))}
              />
            </FormControl>
            
            <FormControl mb={4}>
              <FormLabel>Timeout (seconds)</FormLabel>
              <Input
                type="number"
                value={formData.settings.timeout_seconds}
                onChange={(e) => handleFormChange('settings.timeout_seconds', parseInt(e.target.value))}
              />
            </FormControl>
            
            <FormControl mb={4}>
              <FormLabel>Log Level</FormLabel>
              <Select
                value={formData.settings.log_level}
                onChange={(e) => handleFormChange('settings.log_level', e.target.value)}
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </Select>
            </FormControl>
            
            <FormControl mb={4} display="flex" alignItems="center">
              <FormLabel mb="0">Enable CORS</FormLabel>
              <Switch
                isChecked={formData.settings.cors_enabled}
                onChange={(e) => handleFormChange('settings.cors_enabled', e.target.checked)}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={handleSaveDeployment}>
              {currentDeployment ? 'Update' : 'Deploy'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default DeploymentList;
