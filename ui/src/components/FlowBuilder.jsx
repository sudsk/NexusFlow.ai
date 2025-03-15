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
} from '@chakra-ui/react';
import { FiSave, FiPlay, FiPlus, FiTrash2, FiLink, FiUnlink } from 'react-icons/fi';
import AgentNode from './AgentNode';
import AgentConfigEditor from './AgentConfigEditor';
import NodePropertiesPanel from './NodePropertiesPanel';
import FlowPropertiesPanel from './FlowPropertiesPanel';
import apiService from '../services/api'

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
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    isOpen: isConfigEditorOpen,
    onOpen: onConfigEditorOpen,
    onClose: onConfigEditorClose,
  } = useDisclosure();

  // Load initial data if provided
  useEffect(() => {
    if (initialData) {
      if (initialData.nodes) setNodes(initialData.nodes);
      if (initialData.edges) setEdges(initialData.edges);
      if (initialData.name) setFlowName(initialData.name);
      if (initialData.description) setFlowDescription(initialData.description);
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
          model: 'gpt-4',
          temperature: 0.7,
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

    // Convert flow structure to NexusFlow format
    const agentConfigs = nodes
      .filter(node => node.type === 'agent')
      .map(node => ({
        name: node.data.label,
        capabilities: node.data.capabilities,
        model_provider: node.data.model.split('/')[0] || 'openai',
        model_name: node.data.model.split('/')[1] || 'gpt-4',
        system_message: node.data.systemMessage,
        temperature: node.data.temperature,
        tool_names: node.data.toolNames,
        can_delegate: true
      }));

    const flowConfig = {
      name: flowName,
      description: flowDescription,
      agents: agentConfigs,
      max_steps: 10, // Default, could be made configurable
      tools: {} // Default, could be populated based on selected tools
    };

    setIsLoading(true);
    try {
      const response = flowId
        ? await apiService.flows.update(flowId, flowConfig)
        : await apiService.flows.create(flowConfig);
      
      toast({
        title: 'Success',
        description: `Flow ${flowId ? 'updated' : 'created'} successfully`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      if (onSave) {
        onSave(response.data.flow_id, flowConfig);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to save flow',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  }, [flowId, flowName, flowDescription, nodes, toast, onSave]);

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

  const handleTestFlow = useCallback(async () => {
    // Simple test with a default query
    const testQuery = 'What is the capital of France?';
    toast({
      title: 'Testing flow',
      description: `Running test with query: "${testQuery}"`,
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
    
    // In a real implementation, this would open a test panel or redirect to the test page
  }, [toast]);

  return (
    <ReactFlowProvider>
      <Box h="calc(100vh - 80px)" position="relative">
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
                    isLoading={isLoading}
                  >
                    Save
                  </Button>
                  <Button
                    leftIcon={<FiPlay />}
                    colorScheme="green"
                    onClick={handleTestFlow}
                  >
                    Test
                  </Button>
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
              />
            ) : (
              <FlowPropertiesPanel
                name={flowName}
                description={flowDescription}
                onNameChange={setFlowName}
                onDescriptionChange={setFlowDescription}
              />
            )}
          </VStack>
        </Flex>
      </Box>
      
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
    </ReactFlowProvider>
  );
};

export default FlowBuilder;
