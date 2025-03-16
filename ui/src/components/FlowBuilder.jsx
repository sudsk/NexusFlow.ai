/* eslint-disable no-unused-vars */
import React, { useState, useCallback, useRef, useEffect } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  Button,
  HStack,
  VStack,
  useToast,
  IconButton,
  Text,
  Flex,
  useDisclosure,
  Spinner,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  ModalFooter,
  Select,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from '@chakra-ui/react';
import { FiSave, FiPlay, FiPlus, FiTrash2, FiLink, FiSettings } from 'react-icons/fi';
import AgentNode from './AgentNode';
import AgentConfigEditor from './AgentConfigEditor';
import NodePropertiesPanel from './NodePropertiesPanel';
import FlowPropertiesPanel from './FlowPropertiesPanel';
import FlowTestConsole from './FlowTestConsole';
import apiService from '../services/api';

// Define custom node types
const nodeTypes = {
  agent: AgentNode,
};

const FlowBuilder = ({ flowId, initialData, onSave }) => {
  const toast = useToast();
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [flowName, setFlowName] = useState('Untitled Flow');
  const [flowDescription, setFlowDescription] = useState('');
  const [maxSteps, setMaxSteps] = useState(10);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [availableCapabilities, setAvailableCapabilities] = useState([]);
  const [availableTools, setAvailableTools] = useState([]);
  
  const {
    isOpen: isConfigEditorOpen,
    onOpen: onConfigEditorOpen,
    onClose: onConfigEditorClose,
  } = useDisclosure();

  const {
    isOpen: isTestConsoleOpen,
    onOpen: onTestConsoleOpen,
    onClose: onTestConsoleClose,
  } = useDisclosure();

  const {
    isOpen: isSettingsOpen,
    onOpen: onSettingsOpen,
    onClose: onSettingsClose,
  } = useDisclosure();

  // Fetch capabilities and tools on mount
  useEffect(() => {
    const fetchCapabilitiesAndTools = async () => {
      try {
        // Fetch capabilities
        const capabilitiesResponse = await apiService.capabilities.getAll();
        setAvailableCapabilities(capabilitiesResponse.data || []);

        // For tools, we could either fetch from a dedicated endpoint or extract from existing tools
        // Using mock data for now
        setAvailableTools([
          { name: 'web_search', description: 'Search the web for information' },
          { name: 'data_analysis', description: 'Analyze data and generate insights' },
          { name: 'code_execution', description: 'Execute code in a secure sandbox' },
        ]);
      } catch (error) {
        console.error('Error fetching capabilities and tools:', error);
      }
    };

    fetchCapabilitiesAndTools();
  }, []);

  // Load initial data if provided
  useEffect(() => {
    if (initialData) {
      // If this is an existing flow, load its configuration
      if (initialData.nodes && initialData.edges) {
        // Visual flow representation already provided
        setNodes(initialData.nodes);
        setEdges(initialData.edges);
      } else if (initialData.config && initialData.config.agents) {
        // Convert backend format to visual nodes and edges
        const newNodes = initialData.config.agents.map((agent, index) => ({
          id: agent.agent_id || `agent-${Date.now()}-${index}`,
          type: 'agent',
          position: { x: 100 + (index * 250), y: 100 + (index * 50) },
          data: {
            label: agent.name,
            capabilities: agent.capabilities || [],
            model: `${agent.model_provider}/${agent.model_name}`,
            systemMessage: agent.system_message || '',
            temperature: agent.temperature || 0.7,
            toolNames: agent.tool_names || [],
          },
        }));
        setNodes(newNodes);

        // Create default edges if there are multiple agents
        if (newNodes.length > 1) {
          const newEdges = [];
          for (let i = 0; i < newNodes.length - 1; i++) {
            newEdges.push({
              id: `edge-${i}`,
              source: newNodes[i].id,
              target: newNodes[i + 1].id,
              animated: true,
            });
          }
          setEdges(newEdges);
        }
      }
      
      if (initialData.name) setFlowName(initialData.name);
      if (initialData.description) setFlowDescription(initialData.description);
      if (initialData.max_steps || initialData.config?.max_steps) {
        setMaxSteps(initialData.max_steps || initialData.config?.max_steps);
      }
    }
  }, [initialData, setNodes, setEdges]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const agentType = event.dataTransfer.getData('application/agentType');
      
      // Check if we dropped a valid agent type
      if (!agentType) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode = {
        id: `agent-${Date.now()}`,
        type: 'agent',
        position,
        data: {
          label: `New ${agentType}`,
          agentType,
          capabilities: [],
          model: 'openai/gpt-4',
          temperature: 0.7,
          systemMessage: '',
          toolNames: [],
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const handleDeleteNode = useCallback(() => {
    if (selectedNode) {
      setNodes((nodes) => nodes.filter((node) => node.id !== selectedNode.id));
      setEdges((edges) => edges.filter(
        (edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id
      ));
      setSelectedNode(null);
    }
  }, [selectedNode, setNodes, setEdges]);

  // Format agent configuration for backend
  const formatAgentConfig = (node) => {
    return {
      name: node.data.label,
      agent_id: node.id.startsWith('agent-') ? undefined : node.id, // Only include if it's a valid ID
      capabilities: node.data.capabilities || [],
      model_provider: node.data.model ? node.data.model.split('/')[0] : 'openai',
      model_name: node.data.model ? node.data.model.split('/')[1] : 'gpt-4',
      system_message: node.data.systemMessage || '',
      temperature: node.data.temperature || 0.7,
      tool_names: node.data.toolNames || [],
      can_delegate: true
    };
  };

  const handleSaveFlow = useCallback(async () => {
    if (!flowName.trim()) {
      toast({
        title: 'Flow name required',
        description: 'Please provide a name for your flow',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Check if there are any agents
    const agentNodes = nodes.filter(node => node.type === 'agent');
    if (agentNodes.length === 0) {
      toast({
        title: 'No agents defined',
        description: 'Your flow must contain at least one agent',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Convert agent nodes to backend configuration format
    const agentConfigs = agentNodes.map(formatAgentConfig);

    // Build complete flow configuration
    const flowConfig = {
      name: flowName,
      description: flowDescription,
      agents: agentConfigs,
      max_steps: maxSteps,
      tools: {} // In a real implementation, we would build the tool configurations here
    };

    setIsSaving(true);
    try {
      let response;
      if (flowId) {
        // Update existing flow
        response = await apiService.flows.update(flowId, { flow_config: flowConfig });
      } else {
        // Create new flow
        response = await apiService.flows.create(flowConfig);
      }
      
      toast({
        title: 'Success',
        description: `Flow ${flowId ? 'updated' : 'created'} successfully`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      if (onSave) {
        onSave(response.data.id || response.data.flow_id, flowConfig);
      }
    } catch (error) {
      console.error('Error saving flow:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to save flow',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSaving(false);
    }
  }, [flowId, flowName, flowDescription, nodes, maxSteps, toast, onSave]);

  const handleNodeConfigChange = useCallback((nodeId, newConfig) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              ...newConfig,
            },
          };
        }
        return node;
      })
    );
  }, [setNodes]);

  // Generate flow configuration for testing
  const getFlowConfig = useCallback(() => {
    const agentNodes = nodes.filter(node => node.type === 'agent');
    const agentConfigs = agentNodes.map(formatAgentConfig);
    
    return {
      name: flowName,
      description: flowDescription,
      agents: agentConfigs,
      max_steps: maxSteps,
      tools: {} // Would be populated in a real implementation
    };
  }, [flowName, flowDescription, nodes, maxSteps]);

  return (
    <ReactFlowProvider>
      <Box h="calc(100vh - 160px)" position="relative">
        <Flex h="full">
          <Box
            ref={reactFlowWrapper}
            flex="1"
            h="full"
            border="1px"
            borderColor="gray.200"
            borderRadius="md"
          >
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onInit={setReactFlowInstance}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
            >
              <Controls />
              <Background color="#aaa" gap={16} />
              
              <Panel position="top-right">
                <HStack spacing={2}>
                  <Button
                    leftIcon={<FiSave />}
                    colorScheme="blue"
                    onClick={handleSaveFlow}
                    isLoading={isSaving}
                  >
                    Save
                  </Button>
                  <Button
                    leftIcon={<FiPlay />}
                    colorScheme="green"
                    onClick={onTestConsoleOpen}
                  >
                    Test
                  </Button>
                  <IconButton
                    icon={<FiSettings />}
                    aria-label="Flow settings"
                    onClick={onSettingsOpen}
                  />
                </HStack>
              </Panel>
              
              {selectedNode && (
                <Panel position="bottom-center">
                  <HStack spacing={2} bg="white" p={2} borderRadius="md" shadow="md">
                    <Text fontWeight="bold">Selected: {selectedNode.data.label}</Text>
                    <IconButton
                      icon={<FiTrash2 />}
                      aria-label="Delete node"
                      colorScheme="red"
                      size="sm"
                      onClick={handleDeleteNode}
                    />
                    <IconButton
                      icon={<FiLink />}
                      aria-label="Add connection"
                      size="sm"
                    />
                  </HStack>
                </Panel>
              )}
            </ReactFlow>
          </Box>
          
          <VStack w="300px" h="full" spacing={4} align="stretch" p={4} bg="gray.50">
            {selectedNode ? (
              <NodePropertiesPanel
                node={selectedNode}
                onChange={(newConfig) => handleNodeConfigChange(selectedNode.id, newConfig)}
                capabilities={availableCapabilities}
                tools={availableTools}
              />
            ) : (
              <FlowPropertiesPanel
                name={flowName}
                description={flowDescription}
                maxSteps={maxSteps}
                onNameChange={setFlowName}
                onDescriptionChange={setFlowDescription}
                onMaxStepsChange={setMaxSteps}
              />
            )}
          </VStack>
        </Flex>
      </Box>
      
      {/* Agent Config Editor Modal */}
      {isConfigEditorOpen && selectedNode && (
        <AgentConfigEditor
          isOpen={isConfigEditorOpen}
          onClose={onConfigEditorClose}
          agent={selectedNode.data}
          onSave={(newConfig) => {
            handleNodeConfigChange(selectedNode.id, newConfig);
            onConfigEditorClose();
          }}
        />
      )}

      {/* Flow Settings Modal */}
      <Modal isOpen={isSettingsOpen} onClose={onSettingsClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Flow Settings</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Maximum Execution Steps</FormLabel>
                <NumberInput
                  value={maxSteps}
                  onChange={(_, val) => setMaxSteps(val)}
                  min={1}
                  max={50}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
              <FormControl>
                <FormLabel>Default Tool Timeout (seconds)</FormLabel>
                <NumberInput defaultValue={30} min={1} max={300}>
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onSettingsClose}>
              Save Settings
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Test Console Modal */}
      <Modal isOpen={isTestConsoleOpen} onClose={onTestConsoleClose} size="xl">
        <ModalOverlay />
        <ModalContent maxWidth="80vw">
          <ModalHeader>Test Flow</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FlowTestConsole 
              flowId={flowId} 
              flowConfig={getFlowConfig()} 
            />
          </ModalBody>
          <ModalFooter>
            <Button onClick={onTestConsoleClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </ReactFlowProvider>
  );
};

export default FlowBuilder;
