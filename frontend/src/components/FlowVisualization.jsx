// frontend/src/components/FlowVisualization.jsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Flex,
  Spinner,
  Text,
  Select,
  FormControl,
  FormLabel,
  HStack,
  Button,
  useColorModeValue,
} from '@chakra-ui/react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { FiRefreshCw } from 'react-icons/fi';

// Custom node styles
const nodeStyles = {
  agent: {
    background: '#D6EAF8',
    border: '1px solid #3498DB',
    color: '#2C3E50',
    fontWeight: 'bold',
    borderRadius: '8px',
    padding: '10px',
    width: 180,
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  },
  tool: {
    background: '#FCF3CF',
    border: '1px solid #F1C40F',
    color: '#7D6608',
    fontWeight: 'bold',
    borderRadius: '8px',
    padding: '10px',
    width: 180,
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  },
  start: {
    background: '#D5F5E3',
    border: '1px solid #2ECC71',
    color: '#1E8449',
    fontWeight: 'bold',
    borderRadius: '8px',
    padding: '10px',
    width: 100,
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  },
  end: {
    background: '#FADBD8',
    border: '1px solid #E74C3C',
    color: '#943126',
    fontWeight: 'bold',
    borderRadius: '8px',
    padding: '10px',
    width: 100,
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  },
  router: {
    background: '#E8DAEF',
    border: '1px solid #8E44AD',
    color: '#4A235A',
    fontWeight: 'bold',
    borderRadius: '8px',
    padding: '10px',
    width: 140,
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  }
};

// Custom edge styles
const edgeStyles = {
  default: {
    stroke: '#3498DB',
    strokeWidth: 2,
  },
  delegation: {
    stroke: '#9B59B6',
    strokeWidth: 2,
  },
  tool: {
    stroke: '#F1C40F',
    strokeWidth: 2,
  },
  final: {
    stroke: '#E74C3C',
    strokeWidth: 2,
  },
  initial: {
    stroke: '#2ECC71',
    strokeWidth: 2,
  }
};

const FlowVisualization = ({ executionTrace, flowData, framework = 'auto' }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [layoutType, setLayoutType] = useState('dagre');
  const [highlightPath, setHighlightPath] = useState(true);
  const cardBg = useColorModeValue('white', 'gray.700');

  useEffect(() => {
    if (executionTrace && executionTrace.length > 0) {
      generateFlowFromTrace(executionTrace);
    }
  }, [executionTrace, layoutType, highlightPath]);

  // Generate flow visualization from execution trace
  const generateFlowFromTrace = (trace) => {
    setIsLoading(true);
    
    try {
      // Process trace to extract nodes and connections
      const agentNodes = new Map();
      const toolNodes = new Map();
      const connections = [];
      
      // First identify all unique agents and tools
      trace.forEach(step => {
        if (step.agent_id && step.agent_name && !agentNodes.has(step.agent_id)) {
          agentNodes.set(step.agent_id, {
            id: step.agent_id,
            type: 'agent',
            name: step.agent_name,
            steps: []
          });
        }
        
        if (step.type === 'tool_execution' && step.decision?.tool_name) {
          const toolId = `tool-${step.decision.tool_name}-${step.step || 0}`;
          if (!toolNodes.has(toolId)) {
            toolNodes.set(toolId, {
              id: toolId,
              type: 'tool',
              name: step.decision.tool_name,
              params: step.decision.tool_params || {},
              step: step.step
            });
          }
        }
      });
      
      // Track step execution by agents
      trace.forEach(step => {
        if (step.agent_id && agentNodes.has(step.agent_id)) {
          agentNodes.get(step.agent_id).steps.push(step.step || 0);
        }
      });
      
      // Identify connections between nodes
      for (let i = 0; i < trace.length; i++) {
        const currentStep = trace[i];
        
        // Handle delegations
        if (currentStep.type === 'delegation' && currentStep.agent_id) {
          // Find the previous agent step
          let prevAgentStep = null;
          for (let j = i - 1; j >= 0; j--) {
            if (trace[j].agent_id && trace[j].type !== 'delegation') {
              prevAgentStep = trace[j];
              break;
            }
          }
          
          if (prevAgentStep && prevAgentStep.agent_id) {
            connections.push({
              source: prevAgentStep.agent_id,
              target: currentStep.agent_id,
              type: 'delegation',
              stepOrder: currentStep.step || i
            });
          }
        }
        
        // Handle tool executions
        if (currentStep.type === 'tool_execution' && currentStep.agent_id && currentStep.decision?.tool_name) {
          const toolId = `tool-${currentStep.decision.tool_name}-${currentStep.step || 0}`;
          if (toolNodes.has(toolId)) {
            connections.push({
              source: currentStep.agent_id,
              target: toolId,
              type: 'tool',
              stepOrder: currentStep.step || i
            });
            
            // Add connection back from tool to agent
            connections.push({
              source: toolId,
              target: currentStep.agent_id,
              type: 'tool',
              stepOrder: (currentStep.step || i) + 0.5
            });
          }
        }
      }
      
      // Create start and end nodes
      const startNode = {
        id: 'start',
        type: 'start',
        name: 'Start',
      };
      
      const endNode = {
        id: 'end',
        type: 'end',
        name: 'End',
      };
      
      // Connect start to first agent
      if (trace.length > 0 && trace[0].agent_id) {
        connections.push({
          source: 'start',
          target: trace[0].agent_id,
          type: 'initial',
          stepOrder: 0
        });
      }
      
      // Connect last agent to end
      if (trace.length > 0) {
        const lastAgentStep = trace
          .filter(step => step.agent_id && step.type !== 'delegation')
          .sort((a, b) => (b.step || 0) - (a.step || 0))[0];
        
        if (lastAgentStep && lastAgentStep.agent_id) {
          connections.push({
            source: lastAgentStep.agent_id,
            target: 'end',
            type: 'final',
            stepOrder: (lastAgentStep.step || trace.length) + 1
          });
        }
      }
      
      // Generate positions for nodes
      const positions = calculateNodePositions(
        [startNode, ...agentNodes.values(), ...toolNodes.values(), endNode],
        connections,
        layoutType
      );
      
      // Create ReactFlow nodes
      const flowNodes = [];
      
      // Add start node
      flowNodes.push({
        id: startNode.id,
        data: { label: startNode.name },
        position: positions[startNode.id] || { x: 50, y: 50 },
        style: nodeStyles.start,
      });
      
      // Add end node
      flowNodes.push({
        id: endNode.id,
        data: { label: endNode.name },
        position: positions[endNode.id] || { x: 50, y: 400 },
        style: nodeStyles.end,
      });
      
      // Add agent nodes
      agentNodes.forEach((agent) => {
        flowNodes.push({
          id: agent.id,
          data: { 
            label: agent.name,
            steps: agent.steps.join(', ')
          },
          position: positions[agent.id] || { x: 200, y: 200 },
          style: nodeStyles.agent,
        });
      });
      
      // Add tool nodes
      toolNodes.forEach((tool) => {
        flowNodes.push({
          id: tool.id,
          data: { 
            label: `${tool.name} (Step ${tool.step})`,
            params: JSON.stringify(tool.params, null, 2)
          },
          position: positions[tool.id] || { x: 400, y: 200 },
          style: nodeStyles.tool,
        });
      });
      
      // Create ReactFlow edges
      const flowEdges = connections.map((conn, index) => {
        const edgeStyle = edgeStyles[conn.type] || edgeStyles.default;
        
        return {
          id: `edge-${conn.source}-${conn.target}-${index}`,
          source: conn.source,
          target: conn.target,
          animated: true,
          label: getEdgeLabel(conn.type),
          style: edgeStyle,
          type: 'default' // Can be 'default', 'step', etc.
        };
      });
      
      // Sort connections by step order
      flowEdges.sort((a, b) => {
        const aConn = connections.find(c => `edge-${c.source}-${c.target}` === a.id);
        const bConn = connections.find(c => `edge-${c.source}-${c.target}` === b.id);
        return (aConn?.stepOrder || 0) - (bConn?.stepOrder || 0);
      });
      
      // Set nodes and edges
      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (error) {
      console.error('Error generating flow visualization:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Helper to calculate node positions based on layout algorithm
  const calculateNodePositions = (nodes, connections, layout) => {
    const positions = {};
    
    // Simple positioning algorithm - this would be replaced with a proper layout algorithm in production
    if (layout === 'horizontal') {
      // Horizontal layout
      const agentNodes = nodes.filter(n => n.type === 'agent');
      const toolNodes = nodes.filter(n => n.type === 'tool');
      
      // Position start node
      positions['start'] = { x: 50, y: 200 };
      
      // Position agent nodes in a horizontal line
      agentNodes.forEach((node, index) => {
        positions[node.id] = { x: 200 + (index * 200), y: 200 };
      });
      
      // Position tool nodes below their respective agents
      toolNodes.forEach(node => {
        // Find associated agent
        const agentConn = connections.find(c => c.target === node.id);
        if (agentConn && positions[agentConn.source]) {
          const agentPos = positions[agentConn.source];
          positions[node.id] = { x: agentPos.x, y: agentPos.y + 150 };
        } else {
          // Default position if no connection found
          positions[node.id] = { x: 400, y: 350 };
        }
      });
      
      // Position end node
      const lastAgentNode = agentNodes[agentNodes.length - 1];
      positions['end'] = { x: (lastAgentNode ? positions[lastAgentNode.id].x + 200 : 600), y: 200 };
    } else if (layout === 'vertical') {
      // Vertical layout
      const agentNodes = nodes.filter(n => n.type === 'agent');
      const toolNodes = nodes.filter(n => n.type === 'tool');
      
      // Position start node
      positions['start'] = { x: 300, y: 50 };
      
      // Position agent nodes in a vertical line
      agentNodes.forEach((node, index) => {
        positions[node.id] = { x: 300, y: 150 + (index * 150) };
      });
      
      // Position tool nodes to the right of their respective agents
      toolNodes.forEach(node => {
        // Find associated agent
        const agentConn = connections.find(c => c.target === node.id);
        if (agentConn && positions[agentConn.source]) {
          const agentPos = positions[agentConn.source];
          positions[node.id] = { x: agentPos.x + 300, y: agentPos.y };
        } else {
          // Default position if no connection found
          positions[node.id] = { x: 600, y: 300 };
        }
      });
      
      // Position end node
      const lastAgentNode = agentNodes[agentNodes.length - 1];
      positions['end'] = { x: 300, y: (lastAgentNode ? positions[lastAgentNode.id].y + 150 : 600) };
    } else {
      // Default dagre-like layout (simple implementation)
      const nodesByLevel = {};
      const levelHeight = 120;
      const levelWidth = 250;
      
      // Start with start node at level 0
      nodesByLevel[0] = ['start'];
      positions['start'] = { x: 300, y: 50 };
      
      // Assign levels to each node based on connections
      let maxLevel = 0;
      let processed = new Set(['start']);
      
      // Depth-first traversal to assign levels
      const assignLevels = (nodeId, level) => {
        if (!nodesByLevel[level]) {
          nodesByLevel[level] = [];
        }
        
        if (!nodesByLevel[level].includes(nodeId)) {
          nodesByLevel[level].push(nodeId);
        }
        
        maxLevel = Math.max(maxLevel, level);
        processed.add(nodeId);
        
        // Find outgoing connections
        const outgoing = connections.filter(c => c.source === nodeId);
        
        outgoing.forEach(conn => {
          if (!processed.has(conn.target)) {
            assignLevels(conn.target, level + 1);
          }
        });
      };
      
      assignLevels('start', 0);
      
      // Handle any unprocessed nodes
      nodes.forEach(node => {
        if (!processed.has(node.id)) {
          const level = maxLevel + 1;
          if (!nodesByLevel[level]) {
            nodesByLevel[level] = [];
          }
          nodesByLevel[level].push(node.id);
          maxLevel = level;
        }
      });
      
      // Position nodes by level
      Object.entries(nodesByLevel).forEach(([level, nodeIds]) => {
        const numNodesInLevel = nodeIds.length;
        nodeIds.forEach((nodeId, index) => {
          const xPos = ((index + 1) * levelWidth) / (numNodesInLevel + 1);
          positions[nodeId] = { 
            x: xPos, 
            y: parseInt(level) * levelHeight + 50 
          };
        });
      });
      
      // Special case for the end node
      positions['end'] = { x: 300, y: (maxLevel + 1) * levelHeight + 50 };
    }
    
    return positions;
  };

  // Helper to get edge label
  const getEdgeLabel = (type) => {
    switch (type) {
      case 'delegation': return 'delegates';
      case 'tool': return 'uses';
      case 'initial': return 'start';
      case 'final': return 'end';
      default: return '';
    }
  };

  return (
    <Box h="100%" w="100%">
      <HStack spacing={4} mb={4}>
        <FormControl w="200px">
          <FormLabel fontSize="sm">Layout</FormLabel>
          <Select
            size="sm"
            value={layoutType}
            onChange={(e) => setLayoutType(e.target.value)}
          >
            <option value="dagre">Hierarchical</option>
            <option value="horizontal">Horizontal</option>
            <option value="vertical">Vertical</option>
          </Select>
        </FormControl>
        
        <Button
          size="sm"
          leftIcon={<FiRefreshCw />}
          onClick={() => generateFlowFromTrace(executionTrace)}
          isLoading={isLoading}
        >
          Refresh Layout
        </Button>
      </HStack>
      
      {isLoading ? (
        <Flex h="400px" justify="center" align="center">
          <Spinner />
        </Flex>
      ) : nodes.length > 0 ? (
        <Box h="500px" bg={cardBg} borderRadius="md">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap
              nodeStrokeColor={(n) => {
                return '#fff';
              }}
              nodeColor={(n) => {
                return n.style?.background || '#eee';
              }}
            />
          </ReactFlow>
        </Box>
      ) : (
        <Flex h="400px" justify="center" align="center">
          <Text color="gray.500">No visualization data available</Text>
        </Flex>
      )}
    </Box>
  );
};

export default FlowVisualization;
