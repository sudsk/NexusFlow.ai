// frontend/src/pages/ToolManagement.jsx
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
  HStack,
  Text,
  Button,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Switch,
  Code,
  Select,
  Spinner,
  useDisclosure,
  Flex,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Card,
  CardHeader,
  CardBody,
  VStack,
  Divider,
  useColorModeValue,
  useToast,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
} from '@chakra-ui/react';
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiMoreVertical,
  FiTool,
  FiCheckCircle,
  FiInfo,
  FiPlayCircle,
  FiLock,
  FiUnlock,
  FiLink,
  FiCode,
  FiSearch,
  FiTag,
} from 'react-icons/fi';
import apiService from '../services/api';

// Schema editor component (simplified for now)
const SchemaEditor = ({ schema, onChange }) => {
  const [schemaText, setSchemaText] = useState(
    typeof schema === 'object' ? JSON.stringify(schema, null, 2) : '{}'
  );
  const [error, setError] = useState('');

  const handleChange = (value) => {
    setSchemaText(value);
    try {
      const parsedSchema = JSON.parse(value);
      setError('');
      onChange(parsedSchema);
    } catch (err) {
      setError('Invalid JSON schema');
    }
  };

  return (
    <Box>
      <Textarea
        value={schemaText}
        onChange={(e) => handleChange(e.target.value)}
        minH="200px"
        fontFamily="monospace"
        placeholder='{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The search query"
    }
  },
  "required": ["query"]
}'
        isInvalid={!!error}
      />
      {error && (
        <Text color="red.500" fontSize="sm" mt={1}>
          {error}
        </Text>
      )}
    </Box>
  );
};

// Tool form component
const ToolForm = ({ tool, onSave, isLoading }) => {
  const initialFormState = {
    name: '',
    description: '',
    parameters: {},
    function_name: '',
    is_enabled: true,
    requires_authentication: false,
    metadata: {
      category: 'utility',
      tags: [],
      compatible_frameworks: ['langgraph', 'crewai', 'autogen'],
    },
  };

  const [formData, setFormData] = useState(initialFormState);
  const [activeTab, setActiveTab] = useState(0);

  // Initialize form with tool data if editing
  useEffect(() => {
    if (tool) {
      setFormData({
        name: tool.name || '',
        description: tool.description || '',
        parameters: tool.parameters || {},
        function_name: tool.function_name || '',
        is_enabled: tool.is_enabled !== undefined ? tool.is_enabled : true,
        requires_authentication: tool.requires_authentication || false,
        metadata: tool.metadata || initialFormState.metadata,
      });
    }
  }, [tool]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleMetadataChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      metadata: {
        ...prev.metadata,
        [field]: value,
      },
    }));
  };

  const handleSubmit = () => {
    onSave(formData);
  };

  return (
    <Tabs index={activeTab} onChange={setActiveTab} isLazy>
      <TabList>
        <Tab>Basic Info</Tab>
        <Tab>Parameters</Tab>
        <Tab>Advanced</Tab>
      </TabList>

      <TabPanels>
        <TabPanel>
          <VStack spacing={4} align="stretch">
            <FormControl isRequired>
              <FormLabel>Tool Name</FormLabel>
              <Input
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="web_search"
              />
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Description</FormLabel>
              <Textarea
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                placeholder="Search the web for information"
                rows={3}
              />
            </FormControl>

            <FormControl>
              <FormLabel>Function Name (optional)</FormLabel>
              <Input
                value={formData.function_name}
                onChange={(e) => handleChange('function_name', e.target.value)}
                placeholder="search_web"
              />
              <Text fontSize="sm" color="gray.500" mt={1}>
                Name of the Python function that implements this tool
              </Text>
            </FormControl>

            <HStack>
              <Button
                onClick={() => setActiveTab(1)}
                colorScheme="blue"
                rightIcon={<FiCode />}
              >
                Next: Define Parameters
              </Button>
            </HStack>
          </VStack>
        </TabPanel>

        <TabPanel>
          <VStack spacing={4} align="stretch">
            <FormControl isRequired>
              <FormLabel>Parameters Schema</FormLabel>
              <SchemaEditor
                schema={formData.parameters}
                onChange={(schema) => handleChange('parameters', schema)}
              />
              <Text fontSize="sm" color="gray.500" mt={1}>
                Define the parameters that this tool accepts using JSON Schema
              </Text>
            </FormControl>

            <HStack justify="space-between">
              <Button onClick={() => setActiveTab(0)}>Back</Button>
              <Button
                onClick={() => setActiveTab(2)}
                colorScheme="blue"
                rightIcon={<FiInfo />}
              >
                Next: Advanced Settings
              </Button>
            </HStack>
          </VStack>
        </TabPanel>

        <TabPanel>
          <VStack spacing={4} align="stretch">
            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">Enabled</FormLabel>
              <Switch
                isChecked={formData.is_enabled}
                onChange={(e) => handleChange('is_enabled', e.target.checked)}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">Auth Required</FormLabel>
              <Switch
                isChecked={formData.requires_authentication}
                onChange={(e) =>
                  handleChange('requires_authentication', e.target.checked)
                }
              />
            </FormControl>

            <FormControl mt={4}>
              <FormLabel>Category</FormLabel>
              <Select
                value={formData.metadata.category}
                onChange={(e) => handleMetadataChange('category', e.target.value)}
              >
                <option value="utility">Utility</option>
                <option value="data_processing">Data Processing</option>
                <option value="ai_services">AI Services</option>
                <option value="external_api">External API</option>
                <option value="custom">Custom</option>
              </Select>
            </FormControl>

            <FormControl mt={4}>
              <FormLabel>Compatible Frameworks</FormLabel>
              <HStack spacing={2} mt={2} flexWrap="wrap">
                {['langgraph', 'crewai', 'autogen', 'dspy'].map((fw) => (
                  <Badge
                    key={fw}
                    px={2}
                    py={1}
                    borderRadius="full"
                    colorScheme={
                      formData.metadata.compatible_frameworks?.includes(fw)
                        ? 'blue'
                        : 'gray'
                    }
                    cursor="pointer"
                    onClick={() => {
                      const current = formData.metadata.compatible_frameworks || [];
                      if (current.includes(fw)) {
                        handleMetadataChange(
                          'compatible_frameworks',
                          current.filter((f) => f !== fw)
                        );
                      } else {
                        handleMetadataChange('compatible_frameworks', [
                          ...current,
                          fw,
                        ]);
                      }
                    }}
                  >
                    {fw}
                  </Badge>
                ))}
              </HStack>
            </FormControl>

            <FormControl mt={4}>
              <FormLabel>Tags (comma separated)</FormLabel>
              <Input
                value={(formData.metadata.tags || []).join(', ')}
                onChange={(e) =>
                  handleMetadataChange(
                    'tags',
                    e.target.value.split(',').map((tag) => tag.trim())
                  )
                }
                placeholder="search, web, retrieval"
              />
            </FormControl>

            <HStack justify="space-between" mt={4}>
              <Button onClick={() => setActiveTab(1)}>Back</Button>
              <Button
                onClick={handleSubmit}
                colorScheme="blue"
                isLoading={isLoading}
              >
                {tool ? 'Update Tool' : 'Create Tool'}
              </Button>
            </HStack>
          </VStack>
        </TabPanel>
      </TabPanels>
    </Tabs>
  );
};

// Tool Management main component
const ToolManagement = () => {
  const toast = useToast();
  const [tools, setTools] = useState([]);
  const [currentTool, setCurrentTool] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [frameworkFilter, setFrameworkFilter] = useState('');
  const [toolToDelete, setToolToDelete] = useState(null);

  const {
    isOpen: isFormOpen,
    onOpen: onFormOpen,
    onClose: onFormClose,
  } = useDisclosure();

  const {
    isOpen: isDeleteAlertOpen,
    onOpen: onDeleteAlertOpen,
    onClose: onDeleteAlertClose,
  } = useDisclosure();

  const cancelRef = React.useRef();
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Fetch tools on mount
  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.tools.getAll();
      setTools(response.data.items || []);
    } catch (error) {
      console.error('Error fetching tools:', error);
      toast({
        title: 'Error fetching tools',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewTool = () => {
    setCurrentTool(null);
    onFormOpen();
  };

  const handleEditTool = (tool) => {
    setCurrentTool(tool);
    onFormOpen();
  };

  const handleSaveTool = async (formData) => {
    setIsSaving(true);
    try {
      if (currentTool) {
        // Update existing tool
        const response = await apiService.tools.update(currentTool.id, formData);
        
        // Update state with the response data
        setTools(tools.map((t) => (t.id === currentTool.id ? response.data : t)));

        toast({
          title: 'Tool updated',
          description: `The tool "${formData.name}" has been updated.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        // Create new tool
        const response = await apiService.tools.create(formData);
        
        // Add new tool to state
        setTools([...tools, response.data]);

        toast({
          title: 'Tool created',
          description: `The tool "${formData.name}" has been created.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }

      onFormClose();
    } catch (error) {
      console.error('Error saving tool:', error);
      toast({
        title: 'Error saving tool',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!toolToDelete) return;

    try {
      await apiService.tools.delete(toolToDelete.id);

      // Update state
      setTools(tools.filter((t) => t.id !== toolToDelete.id));

      toast({
        title: 'Tool deleted',
        description: `The tool "${toolToDelete.name}" has been deleted.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error deleting tool:', error);
      toast({
        title: 'Error deleting tool',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setToolToDelete(null);
      onDeleteAlertClose();
    }
  };

  const handleDeleteTool = (tool) => {
    setToolToDelete(tool);
    onDeleteAlertOpen();
  };

  const handleToggleToolStatus = async (tool) => {
    try {
      const updatedToolData = { is_enabled: !tool.is_enabled };
      const response = await apiService.tools.update(tool.id, updatedToolData);
      
      // Update the tool in the state with the response data
      setTools(tools.map((t) => (t.id === tool.id ? response.data : t)));

      toast({
        title: response.data.is_enabled ? 'Tool enabled' : 'Tool disabled',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error toggling tool status:', error);
      toast({
        title: 'Error updating tool',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  // Apply filters to tools
  const filteredTools = tools.filter((tool) => {
    // Framework filter
    if (frameworkFilter && !tool.metadata?.compatible_frameworks?.includes(frameworkFilter)) {
      return false;
    }

    // Search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        tool.name.toLowerCase().includes(query) ||
        tool.description.toLowerCase().includes(query) ||
        tool.metadata?.tags?.some((tag) => tag.toLowerCase().includes(query))
      );
    }

    return true;
  });

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Tool Management</Heading>
        <Button
          leftIcon={<FiPlus />}
          colorScheme="blue"
          onClick={handleNewTool}
        >
          Register New Tool
        </Button>
      </Flex>

      {/* Filters */}
      <Card bg={cardBg} borderColor={borderColor} borderWidth="1px" mb={6}>
        <CardBody>
          <Flex gap={4} flexWrap="wrap">
            <Box flex="1" minW="200px">
              <FormControl>
                <FormLabel fontSize="sm">Search Tools</FormLabel>
                <Input
                  placeholder="Search by name, description, or tags..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  size="md"
                />
              </FormControl>
            </Box>

            <Box width="200px">
              <FormControl>
                <FormLabel fontSize="sm">Framework</FormLabel>
                <Select
                  value={frameworkFilter}
                  onChange={(e) => setFrameworkFilter(e.target.value)}
                  size="md"
                >
                  <option value="">All Frameworks</option>
                  <option value="langgraph">LangGraph</option>
                  <option value="crewai">CrewAI</option>
                  <option value="autogen">AutoGen</option>
                  <option value="dspy">DSPy</option>
                </Select>
              </FormControl>
            </Box>
          </Flex>
        </CardBody>
      </Card>

      {/* Tools Table */}
      {isLoading ? (
        <Flex justify="center" align="center" height="300px">
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : filteredTools.length === 0 ? (
        <Flex direction="column" align="center" justify="center" py={10}>
          <Text fontSize="lg" mb={4}>No tools found matching your filters</Text>
          <Button 
            onClick={() => {
              setSearchQuery('');
              setFrameworkFilter('');
            }}
          >
            Clear Filters
          </Button>
        </Flex>
      ) : (
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Description</Th>
                <Th>Frameworks</Th>
                <Th>Category</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredTools.map((tool) => (
                <Tr key={tool.id}>
                  <Td fontWeight="bold">
                    <HStack>
                      <FiTool />
                      <Text>{tool.name}</Text>
                    </HStack>
                  </Td>
                  <Td maxW="300px" isTruncated>
                    {tool.description}
                  </Td>
                  <Td>
                    <HStack spacing={1} flexWrap="wrap">
                      {tool.metadata?.compatible_frameworks?.map((fw) => (
                        <Badge 
                          key={fw} 
                          colorScheme={
                            fw === 'langgraph' ? 'blue' : 
                            fw === 'crewai' ? 'purple' : 
                            fw === 'autogen' ? 'green' : 
                            fw === 'dspy' ? 'orange' : 'gray'
                          }
                          size="sm"
                        >
                          {fw}
                        </Badge>
                      ))}
                    </HStack>
                  </Td>
                  <Td>
                    <Badge colorScheme="blue">
                      {tool.metadata?.category || 'utility'}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={tool.is_enabled ? 'green' : 'red'}
                      variant={tool.is_enabled ? 'solid' : 'outline'}
                    >
                      {tool.is_enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        size="sm"
                        variant="ghost"
                        icon={tool.is_enabled ? <FiCheckCircle /> : <FiPlayCircle />}
                        aria-label={tool.is_enabled ? 'Disable tool' : 'Enable tool'}
                        onClick={() => handleToggleToolStatus(tool)}
                        colorScheme={tool.is_enabled ? 'green' : 'red'}
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
                            onClick={() => handleEditTool(tool)}
                          >
                            Edit Tool
                          </MenuItem>
                          <MenuItem
                            icon={tool.requires_authentication ? <FiLock /> : <FiUnlock />}
                          >
                            {tool.requires_authentication ? 'Authentication Required' : 'No Authentication Required'}
                          </MenuItem>
                          <MenuItem
                            icon={<FiTrash2 />}
                            color="red.500"
                            onClick={() => handleDeleteTool(tool)}
                          >
                            Delete Tool
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

      {/* Tool Form Modal */}
      <Modal isOpen={isFormOpen} onClose={onFormClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {currentTool ? 'Edit Tool' : 'Register New Tool'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <ToolForm
              tool={currentTool}
              onSave={handleSaveTool}
              isLoading={isSaving}
            />
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isDeleteAlertOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteAlertClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Tool
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete the tool "{toolToDelete?.name}"? This action cannot be undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteAlertClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleConfirmDelete} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};

export default ToolManagement;
