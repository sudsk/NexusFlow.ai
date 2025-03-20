// frontend/src/pages/FlowEditor.jsx
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
  CardHeader,
  IconButton,
  Divider,
  Skeleton,
  useToast,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Alert,
  AlertIcon,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  ModalFooter,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Badge,
} from '@chakra-ui/react';
import { FiHome, FiActivity, FiCpu, FiDatabase, FiCode, FiSearch, FiSettings, FiTool } from 'react-icons/fi';
import { useParams, useNavigate, Link } from 'react-router-dom';
import FlowBuilder from '../components/FlowBuilder';
import FrameworkSelector from '../components/FrameworkSelector';
import FlowToolConfiguration from '../components/FlowToolConfiguration';
import apiService from '../services/api';

const FlowEditor = () => {
  const { flowId } = useParams();
  const isNewFlow = !flowId;
  const navigate = useNavigate();
  const toast = useToast();
  const [flowData, setFlowData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [selectedFramework, setSelectedFramework] = useState('langgraph');
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedTools, setSelectedTools] = useState([]);
  
  const { isOpen: isFrameworkModalOpen, onOpen: onFrameworkModalOpen, onClose: onFrameworkModalClose } = useDisclosure();
  const { isOpen: isToolsModalOpen, onOpen: onToolsModalOpen, onClose: onToolsModalClose } = useDisclosure();

  // Fetch flow data if editing an existing flow
  useEffect(() => {
    if (!isNewFlow) {
      fetchFlowData();
    }
  }, [flowId, isNewFlow]);

  const fetchFlowData = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.flows.getById(flowId);
      setFlowData(response.data);
      
      // Set the framework from the flow data
      if (response.data.framework) {
        setSelectedFramework(response.data.framework);
      }
      
      // Set selected tools from flow data
      if (response.data.tools) {
        setSelectedTools(Object.entries(response.data.tools).map(([name, config]) => ({
          id: name,
          name,
          description: config.description || "",
          config: config.config || {}
        })));
      }
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

  // Handle flow save
  const handleFlowSave = async (flowConfig) => {
    setIsSaving(true);
    try {
      // Add tools to the flow configuration
      const flowWithTools = {
        ...flowConfig,
        framework: selectedFramework,
        tools: selectedTools.reduce((acc, tool) => {
          acc[tool.name] = {
            description: tool.description,
            config: tool.config || {}
          };
          return acc;
        }, {})
      };
      
      let response;
      if (isNewFlow) {
        response = await apiService.flows.create(flowWithTools);
      } else {
        response = await apiService.flows.update(flowId, flowWithTools);
      }
      
      toast({
        title: 'Success',
        description: `Flow ${isNewFlow ? 'created' : 'updated'} successfully`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      // If this was a new flow, redirect to the edit page for the new flow
      if (isNewFlow && response.data.flow_id) {
        navigate(`/flows/${response.data.flow_id}`);
      }
    } catch (error) {
      toast({
        title: 'Error saving flow',
        description: error.response?.data?.detail || 'Failed to save flow',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Handle framework change
  const handleFrameworkChange = (newFramework) => {
    if (newFramework !== selectedFramework) {
      setSelectedFramework(newFramework);
      
      // Reset selected tools when changing frameworks
      setSelectedTools([]);
      
      toast({
        title: `Framework changed to ${newFramework}`,
        description: "Your flow will be built and executed using this framework.",
        status: "info",
        duration: 3000,
        isClosable: true,
      });
    }
    onFrameworkModalClose();
  };
  
  // Handle tools change
  const handleToolsChange = (tools) => {
    setSelectedTools(tools);
  };

  // Agent types that can be dragged onto the canvas
  const agentTypes = [
    { type: 'coordinator', name: 'Coordinator', icon: FiActivity, description: 'Coordinates other agents' },
    { type: 'researcher', name: 'Researcher', icon: FiSearch, description: 'Retrieves information' },
    { type: 'analyst', name: 'Analyst', icon: FiDatabase, description: 'Analyzes data' },
    { type: 'coder', name: 'Coder', icon: FiCode, description: 'Generates code' },
    { type: 'reasoner', name: 'Reasoner', icon: FiCpu, description: 'General reasoning' },
  ];

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

      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">
          {isNewFlow ? 'Create New Flow' : `Edit Flow: ${flowData?.name || ''}`}
        </Heading>
        <HStack>
          <Button 
            leftIcon={<FiTool />} 
            onClick={onToolsModalOpen}
            colorScheme="blue"
            variant="outline"
          >
            Configure Tools {selectedTools.length > 0 && `(${selectedTools.length})`}
          </Button>
          <Button 
            leftIcon={<FiSettings />} 
            onClick={onFrameworkModalOpen}
            colorScheme="blue"
            variant="outline"
          >
            Framework: {selectedFramework}
          </Button>
        </HStack>
      </Flex>

      {/* Framework/Tools info */}
      <Card mb={6}>
        <CardBody>
          <Flex justify="space-between" align="center">
            <HStack>
              <Text fontWeight="medium">Framework:</Text>
              <Badge colorScheme="blue">{selectedFramework}</Badge>
            </HStack>
            <HStack>
              <Text fontWeight="medium">Tools:</Text>
              <Badge colorScheme="green">{selectedTools.length}</Badge>
            </HStack>
          </Flex>
        </CardBody>
      </Card>

      {/* Main Editor UI */}
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
              initialData={{
                ...(flowData || {}),
                framework: selectedFramework,
                tools: selectedTools
              }}
              onSave={handleFlowSave}
              framework={selectedFramework}
              isSaving={isSaving}
            />
          )}
        </Box>
      </Flex>

      {/* Framework Selection Modal */}
      <Modal isOpen={isFrameworkModalOpen} onClose={onFrameworkModalClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Select Framework</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text mb={4}>
              Choose the AI orchestration framework for this flow. Each framework has different capabilities and characteristics.
            </Text>
            <FrameworkSelector
              value={selectedFramework}
              onChange={handleFrameworkChange}
            />
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={onFrameworkModalClose}>
              Done
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Tools Configuration Modal */}
      <Modal isOpen={isToolsModalOpen} onClose={onToolsModalClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Configure Flow Tools</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text mb={4}>
              Select and configure the tools that will be available to agents in this flow.
            </Text>
            <FlowToolConfiguration
              selectedTools={selectedTools}
              framework={selectedFramework}
              onToolsChange={handleToolsChange}
            />
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={onToolsModalClose}>
              Done
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default FlowEditor;
