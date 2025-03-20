// frontend/src/components/FlowToolConfiguration.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  FormHelperText,
  Select,
  Checkbox,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  HStack,
  VStack,
  IconButton,
  Badge,
  Text,
  Tag,
  Flex,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  ModalFooter,
  useDisclosure,
  useColorModeValue,
  Switch,
  Spinner,
  Divider,
  Alert,
  AlertIcon,
  Tooltip,
} from '@chakra-ui/react';
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiTool,
  FiInfo,
  FiCheckCircle,
  FiXCircle,
  FiSettings,
} from 'react-icons/fi';
import apiService from '../services/api';

// The FlowToolConfiguration component is used to configure tools for a flow
// It allows selecting which tools are available to agents in the flow
// It also handles framework-specific tool configurations
const FlowToolConfiguration = ({ 
  selectedTools = [], 
  framework = 'langgraph',
  onToolsChange,
  isReadOnly = false
}) => {
  const [availableTools, setAvailableTools] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedToolIds, setSelectedToolIds] = useState(
    selectedTools.map(tool => tool.id || tool.name)
  );
  const [activeToolConfig, setActiveToolConfig] = useState(null);
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // Fetch available tools
  useEffect(() => {
    fetchTools();
  }, [framework]);
  
  const fetchTools = async () => {
    setIsLoading(true);
    try {
      // In a real implementation, this would call the API with framework filter
      // const response = await apiService.tools.getAll({ framework });
      
      // Mock data for now
      await new Promise(resolve => setTimeout(resolve, 600)); // Simulate API delay
      
      // Mock tools data
      const mockTools = [
        {
          id: '1',
          name: 'web_search',
          description: 'Search the web for information',
          metadata: {
            category: 'utility',
            compatible_frameworks: ['langgraph', 'crewai', 'autogen'],
          },
          framework_config: {
            langgraph: {
              use_async: true,
              streaming: false,
            },
            crewai: {
              allow_delegation: true,
            }
          },
          is_enabled: true,
        },
        {
          id: '2',
          name: 'code_execution',
          description: 'Execute code in a secure sandbox environment',
          metadata: {
            category: 'data_processing',
            compatible_frameworks: ['langgraph', 'autogen'],
          },
          framework_config: {
            langgraph: {
              use_async: true,
              streaming: true,
            }
          },
          is_enabled: true,
        },
        {
          id: '3',
          name: 'data_analysis',
          description: 'Analyze data and generate insights',
          metadata: {
            category: 'data_processing',
            compatible_frameworks: ['langgraph', 'crewai', 'autogen', 'dspy'],
          },
          framework_config: {
            langgraph: {
              use_async: true,
              streaming: false,
            },
            crewai: {
              allow_delegation: false,
            }
          },
          is_enabled: true,
        },
        {
          id: '4',
          name: 'document_retrieval',
          description: 'Retrieve documents from a knowledge base',
          metadata: {
            category: 'utility',
            compatible_frameworks: ['langgraph', 'crewai', 'autogen', 'dspy'],
          },
          framework_config: {
            langgraph: {
              use_async: false,
              streaming: false,
            },
            crewai: {
              allow_delegation: true,
            }
          },
          is_enabled: true,
        },
      ];
      
      // Filter tools compatible with the selected framework
      const filteredTools = mockTools.filter(tool => 
        tool.is_enabled && 
        tool.metadata?.compatible_frameworks?.includes(framework)
      );
      
      setAvailableTools(filteredTools);
    } catch (error) {
      console.error('Error fetching tools:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle tool selection change
  const handleToolSelectionChange = (toolId, isSelected) => {
    if (isReadOnly) return;
    
    let newSelectedToolIds;
    if (isSelected) {
      newSelectedToolIds = [...selectedToolIds, toolId];
    } else {
      newSelectedToolIds = selectedToolIds.filter(id => id !== toolId);
    }
    
    setSelectedToolIds(newSelectedToolIds);
    
    // Update parent component
    if (onToolsChange) {
      const selectedToolObjects = availableTools
        .filter(tool => newSelectedToolIds.includes(tool.id))
        .map(tool => ({
          id: tool.id,
          name: tool.name,
          description: tool.description,
          // Include framework-specific configuration
          config: tool.framework_config?.[framework] || {}
        }));
      
      onToolsChange(selectedToolObjects);
    }
  };
  
  // Open tool configuration modal
  const handleConfigureTool = (tool) => {
    setActiveToolConfig({
      ...tool,
      config: tool.framework_config?.[framework] || createDefaultConfig(framework)
    });
    onOpen();
  };
  
  // Create default configuration for a framework
  const createDefaultConfig = (fw) => {
    switch (fw) {
      case 'langgraph':
        return {
          use_async: false,
          streaming: false,
          timeout: 30,
        };
      case 'crewai':
        return {
          allow_delegation: true,
          timeout: 30,
        };
      case 'autogen':
        return {
          use_async: false,
          timeout: 30,
        };
      default:
        return {};
    }
  };
  
  // Save tool configuration
  const handleSaveToolConfig = () => {
    if (!activeToolConfig) return;
    
    // Find the tool in available tools
    const updatedTools = availableTools.map(tool => {
      if (tool.id === activeToolConfig.id) {
        // Create or update framework configuration
        const updatedFrameworkConfig = {
          ...tool.framework_config,
          [framework]: activeToolConfig.config
        };
        
        return {
          ...tool,
          framework_config: updatedFrameworkConfig
        };
      }
      return tool;
    });
    
    setAvailableTools(updatedTools);
    
    // Update parent component
    if (onToolsChange) {
      const selectedToolObjects = updatedTools
        .filter(tool => selectedToolIds.includes(tool.id))
        .map(tool => ({
          id: tool.id,
          name: tool.name,
          description: tool.description,
          config: tool.framework_config?.[framework] || {}
        }));
      
      onToolsChange(selectedToolObjects);
    }
    
    onClose();
  };
  
  // Handle configuration changes
  const handleConfigChange = (field, value) => {
    if (!activeToolConfig) return;
    
    setActiveToolConfig({
      ...activeToolConfig,
      config: {
        ...activeToolConfig.config,
        [field]: value
      }
    });
  };
  
  // Render framework-specific configuration form
  const renderConfigForm = () => {
    if (!activeToolConfig) return null;
    
    switch (framework) {
      case 'langgraph':
        return (
          <VStack align="stretch" spacing={4}>
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Async Execution</FormLabel>
                <Switch
                  isChecked={activeToolConfig.config.use_async}
                  onChange={(e) => handleConfigChange('use_async', e.target.checked)}
                  isDisabled={isReadOnly}
                />
              </Flex>
              <FormHelperText>
                Run tool asynchronously to avoid blocking the flow
              </FormHelperText>
            </FormControl>
            
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Enable Streaming</FormLabel>
                <Switch
                  isChecked={activeToolConfig.config.streaming}
                  onChange={(e) => handleConfigChange('streaming', e.target.checked)}
                  isDisabled={isReadOnly}
                />
              </Flex>
              <FormHelperText>
                Stream results as they become available
              </FormHelperText>
            </FormControl>
            
            <FormControl>
              <FormLabel>Timeout (seconds)</FormLabel>
              <Select
                value={activeToolConfig.config.timeout || 30}
                onChange={(e) => handleConfigChange('timeout', parseInt(e.target.value))}
                isDisabled={isReadOnly}
              >
                <option value={10}>10 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={60}>1 minute</option>
                <option value={300}>5 minutes</option>
                <option value={600}>10 minutes</option>
              </Select>
            </FormControl>
          </VStack>
        );
        
      case 'crewai':
        return (
          <VStack align="stretch" spacing={4}>
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Allow Delegation</FormLabel>
                <Switch
                  isChecked={activeToolConfig.config.allow_delegation}
                  onChange={(e) => handleConfigChange('allow_delegation', e.target.checked)}
                  isDisabled={isReadOnly}
                />
              </Flex>
              <FormHelperText>
                Allow this tool to be delegated to other agents
              </FormHelperText>
            </FormControl>
            
            <FormControl>
              <FormLabel>Timeout (seconds)</FormLabel>
              <Select
                value={activeToolConfig.config.timeout || 30}
                onChange={(e) => handleConfigChange('timeout', parseInt(e.target.value))}
                isDisabled={isReadOnly}
              >
                <option value={10}>10 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={60}>1 minute</option>
                <option value={300}>5 minutes</option>
                <option value={600}>10 minutes</option>
              </Select>
            </FormControl>
          </VStack>
        );
        
      case 'autogen':
        return (
          <VStack align="stretch" spacing={4}>
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Async Execution</FormLabel>
                <Switch
                  isChecked={activeToolConfig.config.use_async}
                  onChange={(e) => handleConfigChange('use_async', e.target.checked)}
                  isDisabled={isReadOnly}
                />
              </Flex>
              <FormHelperText>
                Run tool asynchronously
              </FormHelperText>
            </FormControl>
            
            <FormControl>
              <FormLabel>Timeout (seconds)</FormLabel>
              <Select
                value={activeToolConfig.config.timeout || 30}
                onChange={(e) => handleConfigChange('timeout', parseInt(e.target.value))}
                isDisabled={isReadOnly}
              >
                <option value={10}>10 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={60}>1 minute</option>
                <option value={300}>5 minutes</option>
                <option value={600}>10 minutes</option>
              </Select>
            </FormControl>
          </VStack>
        );
        
      default:
        return (
          <Alert status="info">
            <AlertIcon />
            No specific configuration options available for this framework.
          </Alert>
        );
    }
  };
  
  return (
    <Box>
      <Heading size="sm" mb={4}>Tools Configuration</Heading>
      
      {isLoading ? (
        <Flex justify="center" align="center" height="100px">
          <Spinner size="md" />
        </Flex>
      ) : availableTools.length === 0 ? (
        <Alert status="warning">
          <AlertIcon />
          No tools available for the {framework} framework.
        </Alert>
      ) : (
        <Box maxH="500px" overflowY="auto" borderWidth="1px" borderRadius="md" borderColor={borderColor}>
          <Table variant="simple" size="sm">
            <Thead position="sticky" top={0} bg={cardBg} zIndex={1}>
              <Tr>
                <Th width="50px"></Th>
                <Th>Tool</Th>
                <Th>Description</Th>
                <Th width="100px">Category</Th>
                {!isReadOnly && <Th width="100px">Configure</Th>}
              </Tr>
            </Thead>
            <Tbody>
              {availableTools.map((tool) => (
                <Tr key={tool.id}>
                  <Td>
                    <Checkbox
                      isChecked={selectedToolIds.includes(tool.id)}
                      onChange={(e) => handleToolSelectionChange(tool.id, e.target.checked)}
                      isDisabled={isReadOnly}
                    />
                  </Td>
                  <Td fontWeight="medium">
                    <HStack>
                      <FiTool />
                      <Text>{tool.name}</Text>
                    </HStack>
                  </Td>
                  <Td>{tool.description}</Td>
                  <Td>
                    <Badge colorScheme="blue">
                      {tool.metadata?.category || 'utility'}
                    </Badge>
                  </Td>
                  {!isReadOnly && (
                    <Td>
                      <Tooltip label="Configure tool">
                        <IconButton
                          icon={<FiSettings />}
                          size="sm"
                          variant="ghost"
                          onClick={() => handleConfigureTool(tool)}
                          isDisabled={!selectedToolIds.includes(tool.id)}
                        />
                      </Tooltip>
                    </Td>
                  )}
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}
      
      {/* Framework-specific explanations */}
      <Box mt={4}>
        <Heading size="xs" mb={2}>Framework-Specific Tool Integration</Heading>
        <Text fontSize="sm" color="gray.600">
          {framework === 'langgraph' && 
            "In LangGraph, tools can be integrated as node functions. Each tool can be configured with async support and streaming capabilities."
          }
          {framework === 'crewai' && 
            "In CrewAI, tools are assigned to specific agents. They can be configured to allow delegation to other agents in the crew."
          }
          {framework === 'autogen' && 
            "In AutoGen, tools are registered with the conversation and can be used by any participating agent."
          }
        </Text>
      </Box>
      
      {/* Tool Configuration Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            Configure Tool: {activeToolConfig?.name}
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {activeToolConfig && (
              <>
                <HStack mb={4}>
                  <Badge colorScheme="blue">{framework}</Badge>
                  <Badge colorScheme="green">{activeToolConfig.metadata?.category || 'utility'}</Badge>
                </HStack>
                
                <Text mb={4}>{activeToolConfig.description}</Text>
                
                <Divider mb={4} />
                
                <Heading size="sm" mb={3}>Framework Configuration</Heading>
                
                {renderConfigForm()}
              </>
            )}
          </ModalBody>
          
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="blue" 
              onClick={handleSaveToolConfig}
              isDisabled={isReadOnly}
            >
              Save Configuration
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default FlowToolConfiguration;
