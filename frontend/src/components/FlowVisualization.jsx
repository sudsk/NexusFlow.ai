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
  IconButton,
  Tooltip,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Divider,
} from '@chakra-ui/react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { 
  FiRefreshCw,
  FiZoomIn,
  FiZoomOut,
  FiMaximize,
  FiMoreVertical,
  FiDownload,
  FiSettings,
  FiInfo,
} from 'react-icons/fi';

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
  },
  // Add framework-specific styles
  langgraph: {
    background: '#D6EAF8',
    border: '2px solid #3498DB',
    color: '#2C3E50',
    fontWeight: 'bold',
    borderRadius: '8px',
    padding: '10px',
    width: 180,
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  },
  crewai: {
    background: '#E8DAEF',
    border: '2px solid #8E44AD',
    color: '#4A235A',
    fontWeight: 'bold',
    borderRadius: '8px',
    padding: '10px',
    width: 180,
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
  },
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
  },
  // Add framework-specific styles
  langgraph: {
    stroke: '#3498DB',
    strokeWidth: 2,
    animated: true,
  },
  crewai: {
    stroke: '#8E44AD',
    strokeWidth: 2,
    animated: true,
  }
};

const FlowVisualization = ({ executionTrace, flowData, framework = 'auto', onDownload }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [layoutType, setLayoutType] = useState('dagre');
  const [highlightPath, setHighlightPath] = useState(true);
  const [showDetails, setShowDetails] = useState(true);
  const [selectedElement, setSelectedElement] = useState(null);
  const [fitView, setFitView] = useState(true);
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'white');  

  useEffect(() => {
    if (executionTrace && executionTrace.length > 0) {
      generateFlowFromTrace(executionTrace);
    } else if (flowData) {
      generateFlowFromData(flowData);
    }
  }, [executionTrace, flowData, layoutType, highlightPath, framework, showDetails]);

  // Generate flow visualization from data
  const generateFlowFromData = (data) => {
    setIsLoading(true);
    
    try {
      // Create nodes from flow data
      const flowNodes = [];
      const flowEdges = [];
      
      // Process based on framework
      if (framework === 'langgraph' || (framework === 'auto' && data.framework === 'langgraph')) {
        // Special handling for LangGraph data
        generateLangGraphVisualization(data, flowNodes, flowEdges);
      } else if (framework === 'crewai' || (framework === 'auto' && data.framework === 'crewai')) {
        // Special handling for CrewAI data
        generateCrewAIVisualization(data, flowNodes, flowEdges);
      } else {
        // Generic flow visualization
        generateGenericVisualization(data, flowNodes, flowEdges);
      }
      
      // Set nodes and edges with calculated positions
      const nodePositions = calculateNodePositions(flowNodes, flowEdges, layoutType);
      
      // Position nodes
      flowNodes.forEach(node => {
        node.position = nodePositions[node.id] || { x: 100, y: 100 };
      });
      
      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (error) {
      console.error('Error generating flow visualization:', error);
    } finally {
      setIsLoading(false);
    }
  };

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
      
      // Collect all nodes
      const allNodes = [
        startNode, 
        ...Array.from(agentNodes.values()), 
        ...Array.from(toolNodes.values()), 
        endNode
      ];
      
      // Generate positions for nodes
      const positions = calculateNodePositions(allNodes, connections, layoutType);
      
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
        // Add framework-specific styles based on detected framework
        let nodeStyle = nodeStyles.agent;
        if (framework !== 'auto') {
          nodeStyle = nodeStyles[framework] || nodeStyles.agent;
        }
        
        flowNodes.push({
          id: agent.id,
          data: { 
            label: agent.name,
            steps: agent.steps.join(', '),
            nodeType: 'agent'
          },
          position: positions[agent.id] || { x: 200, y: 200 },
          style: nodeStyle,
        });
      });
      
      // Add tool nodes
      toolNodes.forEach((tool) => {
        flowNodes.push({
          id: tool.id,
          data: { 
            label: `${tool.name} (Step ${tool.step})`,
            params: JSON.stringify(tool.params, null, 2),
            nodeType: 'tool'
          },
          position: positions[tool.id] || { x: 400, y: 200 },
          style: nodeStyles.tool,
        });
      });
      
      // Create ReactFlow edges
      const flowEdges = connections.map((conn, index) => {
        const edgeStyle = edgeStyles[conn.type] || edgeStyles.default;
        
        // Add framework-specific styles
        let edgeStyleFinal = {...edgeStyle};
        if (framework !== 'auto') {
          edgeStyleFinal = {...edgeStyle, ...edgeStyles[framework]};
        }
        
        return {
          id: `edge-${conn.source}-${conn.target}-${index}`,
          source: conn.source,
          target: conn.target,
          animated: conn.type === 'delegation',
          label: getEdgeLabel(conn.type),
          style: edgeStyleFinal,
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
  
  // Helper to generate LangGraph-specific visualization
  const generateLangGraphVisualization = (data, flowNodes, flowEdges) => {
    // Add nodes for each agent/state in LangGraph
    const agents = data.agents || [];
    agents.forEach((agent, index) => {
      flowNodes.push({
        id: agent.agent_id || `agent-${index}`,
        data: { 
          label: agent.name || `Agent ${index + 1}`,
          description: agent.description || '',
          nodeType: 'agent',
          framework: 'langgraph'
        },
        style: nodeStyles.langgraph
      });
    });
    
    // Add edges between nodes based on state transitions
    // For LangGraph, we need to extract state transitions
    if (agents.length > 1) {
      // Create a simple chain for now - this would be enhanced with actual state transition data
      for (let i = 0; i < agents.length - 1; i++) {
        flowEdges.push({
          id: `edge-${i}-${i+1}`,
          source: agents[i].agent_id || `agent-${i}`,
          target: agents[i+1].agent_id || `agent-${i+1}`,
          style: edgeStyles.langgraph,
          animated: true,
          label: 'next',
        });
      }
    }
    
    // Add start and end nodes for clarity
    if (agents.length > 0) {
      // Start node
      flowNodes.push({
        id: 'start',
        data: { label: 'Start' },
        style: nodeStyles.start
      });
      
      // End node
      flowNodes.push({
        id: 'end',
        data: { label: 'End' },
        style: nodeStyles.end
      });
      
      // Connect start to first agent
      flowEdges.push({
        id: 'edge-start',
        source: 'start',
        target: agents[0].agent_id || 'agent-0',
        style: edgeStyles.initial,
        animated: true
      });
      
      // Connect last agent to end
      flowEdges.push({
        id: 'edge-end',
        source: agents[agents.length-1].agent_id || `agent-${agents.length-1}`,
        target: 'end',
        style: edgeStyles.final,
        animated: true
      });
    }
  };
  
  // Helper to generate CrewAI-specific visualization
  const generateCrewAIVisualization = (data, flowNodes, flowEdges) => {
    // Add nodes for each agent in CrewAI
    const agents = data.agents || [];
    
    // In CrewAI, the agents are arranged in a "crew" structure
    agents.forEach((agent, index) => {
      flowNodes.push({
        id: agent.agent_id || `agent-${index}`,
        data: { 
          label: agent.name || `Agent ${index + 1}`,
          role: agent.description || '',
          nodeType: 'agent',
          framework: 'crewai'
        },
        style: nodeStyles.crewai
      });
    });
    
    // For CrewAI, we can create a more team-oriented visualization
    // Often in CrewAI, there's a delegator agent that assigns tasks
    // We'll create a central "hub and spoke" layout for visualization
    
    // Add central coordinator if there are multiple agents
    if (agents.length > 1) {
      // Identify potential coordinator (first agent or agent with "coordinator" in the name)
      let coordinatorIndex = 0;
      for (let i = 0; i < agents.length; i++) {
        if (agents[i].name.toLowerCase().includes('coordinator') || 
            agents[i].description.toLowerCase().includes('coordinator')) {
          coordinatorIndex = i;
          break;
        }
      }
      
      // Connect coordinator to other agents
      const coordinatorId = agents[coordinatorIndex].agent_id || `agent-${coordinatorIndex}`;
      for (let i = 0; i < agents.length; i++) {
        if (i !== coordinatorIndex) {
          const agentId = agents[i].agent_id || `agent-${i}`;
          flowEdges.push({
            id: `edge-${coordinatorIndex}-${i}`,
            source: coordinatorId,
            target: agentId,
            style: edgeStyles.crewai,
            animated: true,
            label: 'delegates',
          });
          
          // Add feedback edge
          flowEdges.push({
            id: `edge-${i}-${coordinatorIndex}`,
            source: agentId,
            target: coordinatorId,
            style: {...edgeStyles.crewai, strokeDasharray: 5},
            animated: false,
            label: 'reports',
          });
        }
      }
    }
    
    // Add start and end nodes
    if (agents.length > 0) {
      // Start node
      flowNodes.push({
        id: 'start',
        data: { label: 'Start' },
        style: nodeStyles.start
      });
      
      // End node
      flowNodes.push({
        id: 'end',
        data: { label: 'End' },
        style: nodeStyles.end
      });
      
      // Connect start to first agent
      flowEdges.push({
        id: 'edge-start',
        source: 'start',
        target: agents[0].agent_id || 'agent-0',
        style: edgeStyles.initial,
        animated: true
      });
      
      // Connect last agent to end
      flowEdges.push({
        id: 'edge-end',
        source: agents[agents.length-1].agent_id || `agent-${agents.length-1}`,
        target: 'end',
        style: edgeStyles.final,
        animated: true
      });
    }
  };
  
  // Helper to generate visualization for other frameworks or generic flows
  const generateGenericVisualization = (data, flowNodes, flowEdges) => {
    const agents = data.agents || [];
    
    // Add nodes for each agent
    agents.forEach((agent, index) => {
      flowNodes.push({
        id: agent.agent_id || `agent-${index}`,
        data: { 
          label: agent.name || `Agent ${index + 1}`,
          description: agent.description || '',
          nodeType: 'agent'
        },
        style: nodeStyles.agent
      });
    });
    
    // Create simple linear flow between agents
    if (agents.length > 1) {
      for (let i = 0; i < agents.length - 1; i++) {
        flowEdges.push({
          id: `edge-${i}-${i+1}`,
          source: agents[i].agent_id || `agent-${i}`,
          target: agents[i+1].agent_id || `agent-${i+1}`,
          style: edgeStyles.default,
          animated: true
        });
      }
    }
    
    // Add start and end nodes
    if (agents.length > 0) {
      // Start node
      flowNodes.push({
        id: 'start',
        data: { label: 'Start' },
        style: nodeStyles.start
      });
      
      // End node
      flowNodes.push({
        id: 'end',
        data: { label: 'End' },
        style: nodeStyles.end
      });
      
      // Connect start to first agent
      flowEdges.push({
        id: 'edge-start',
        source: 'start',
        target: agents[0].agent_id || 'agent-0',
        style: edgeStyles.initial,
        animated: true
      });
      
      // Connect last agent to end
      flowEdges.push({
        id: 'edge-end',
        source: agents[agents.length-1].agent_id || `agent-${agents.length-1}`,
        target: 'end',
        style: edgeStyles.final,
        animated: true
      });
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
    } else if (layout === 'radial') {
      // Radial layout - good for CrewAI visualization
      const centerX = 400;
      const centerY = 300;
      const radius = 200;
      
      // Find a coordinator node if exists
      const agentNodes = nodes.filter(n => n.type === 'agent');
      let coordinatorNode = agentNodes.find(n => {
        const label = n.name || n.data?.label || '';
        return label.toLowerCase().includes('coordinator');
      });
      
      // If no explicit coordinator, use the first agent
      if (!coordinatorNode && agentNodes.length > 0) {
        coordinatorNode = agentNodes[0];
      }
      
      // Position start and end nodes
      positions['start'] = { x: centerX, y: 50 };
      positions['end'] = { x: centerX, y: 550 };
      
      if (coordinatorNode) {
        // Position coordinator in center
        positions[coordinatorNode.id] = { x: centerX, y: centerY };
        
        // Position other agents in a circle around coordinator
        const otherAgents = agentNodes.filter(n => n.id !== coordinatorNode.id);
        otherAgents.forEach((node, index) => {
          const angle = (index / otherAgents.length) * 2 * Math.PI;
          positions[node.id] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
          };
        });
      } else {
        // No coordinator, position agents in a circle
        agentNodes.forEach((node, index) => {
          const angle = (index / agentNodes.length) * 2 * Math.PI;
          positions[node.id] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
          };
        });
      }
      
      // Position tool nodes near their associated agents
      const toolNodes = nodes.filter(n => n.type === 'tool');
      toolNodes.forEach(node => {
        // Find associated agent
        const agentConn = connections.find(c => c.target === node.id);
        if (agentConn && positions[agentConn.source]) {
          const agentPos = positions[agentConn.source];
          // Position slightly offset from agent
          positions[node.id] = { 
            x: agentPos.x + 30 + Math.random() * 40, 
            y: agentPos.y + 30 + Math.random() * 40 
          };
        } else {
          // Default position if no connection found
          positions[node.id] = { x: centerX + 100, y: centerY + 100 };
        }
      });
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

  const onNodeClick = (event, node) => {
    setSelectedElement(node);
  };
  
  const onEdgeClick = (event, edge) => {
    setSelectedElement(edge);
  };
  
  const onPaneClick = () => {
    setSelectedElement(null);
  };
  
  const handleDownload = () => {
    if (onDownload) {
      onDownload(nodes, edges);
    }
  };

  return (
    <Box h="100%" w="100%">
      <HStack spacing={4} mb={4} wrap="wrap">
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
            <option value="radial">Radial</option>
          </Select>
        </FormControl>
        
        <Button
          size="sm"
          leftIcon={<FiRefreshCw />}
          onClick={() => {
            if (executionTrace && executionTrace.length > 0) {
              generateFlowFromTrace(executionTrace);
            } else if (flowData) {
              generateFlowFromData(flowData);
            }
          }}
          isLoading={isLoading}
        >
          Refresh Layout
        </Button>
        
        <Button
          size="sm"
          variant={highlightPath ? "solid" : "outline"}
          colorScheme={highlightPath ? "blue" : "gray"}
          onClick={() => setHighlightPath(!highlightPath)}
        >
          Highlight Path
        </Button>
        
        <Button
          size="sm"
          variant={showDetails ? "solid" : "outline"}
          colorScheme={showDetails ? "blue" : "gray"}
          onClick={() => setShowDetails(!showDetails)}
        >
          Show Details
        </Button>
      </HStack>
      
      {isLoading ? (
        <Flex h="400px" justify="center" align="center">
          <Spinner />
        </Flex>
      ) : nodes.length > 0 ? (
        <Box h="500px" bg={cardBg} borderRadius="md" borderWidth="1px" borderColor={borderColor}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            fitView={fitView}
            attributionPosition="bottom-right"
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
            
            <Panel position="top-right">
              <HStack spacing={2}>
                <Tooltip label="Fit view">
                  <IconButton
                    size="sm"
                    icon={<FiMaximize />}
                    onClick={() => setFitView(true)}
                  />
                </Tooltip>
                <Tooltip label="Download">
                  <IconButton
                    size="sm"
                    icon={<FiDownload />}
                    onClick={handleDownload}
                  />
                </Tooltip>
                <Menu>
                  <MenuButton
                    as={IconButton}
                    icon={<FiMoreVertical />}
                    size="sm"
                    variant="ghost"
                  />
                  <MenuList>
                    <MenuItem onClick={() => setHighlightPath(!highlightPath)}>
                      {highlightPath ? "Disable Path Highlighting" : "Enable Path Highlighting"}
                    </MenuItem>
                    <MenuItem onClick={() => setShowDetails(!showDetails)}>
                      {showDetails ? "Hide Details" : "Show Details"}
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={handleDownload}>Export Visualization</MenuItem>
                  </MenuList>
                </Menu>
              </HStack>
            </Panel>
          </ReactFlow>
        </Box>
      ) : (
        <Flex h="400px" justify="center" align="center">
          <Text color="gray.500">No visualization data available</Text>
        </Flex>
      )}
      
      {selectedElement && (
        <Box mt={4} p={4} borderWidth="1px" borderRadius="md" bg={cardBg} borderColor={borderColor}>
          <Heading size="sm" mb={2}>
            {selectedElement.data ? 'Node Details' : 'Edge Details'}
          </Heading>
          
          {selectedElement.data && (
            <Box>
              <Text fontWeight="bold">{selectedElement.data.label}</Text>
              {selectedElement.data.nodeType && (
                <Badge colorScheme={
                  selectedElement.data.nodeType === 'agent' 
                    ? 'blue' 
                    : selectedElement.data.nodeType === 'tool' 
                      ? 'yellow' 
                      : 'gray'
                }>
                  {selectedElement.data.nodeType}
                </Badge>
              )}
              {selectedElement.data.framework && (
                <Badge ml={2} colorScheme={
                  selectedElement.data.framework === 'langgraph' 
                    ? 'blue' 
                    : selectedElement.data.framework === 'crewai' 
                      ? 'purple' 
                      : 'gray'
                }>
                  {selectedElement.data.framework}
                </Badge>
              )}
              {selectedElement.data.description && <Text mt={1}>{selectedElement.data.description}</Text>}
              {selectedElement.data.role && <Text mt={1}>Role: {selectedElement.data.role}</Text>}
              {selectedElement.data.steps && <Text mt={1}>Steps: {selectedElement.data.steps}</Text>}
            </Box>
          )}
          
          {!selectedElement.data && (
            <Box>
              <Text>From: {selectedElement.source}</Text>
              <Text>To: {selectedElement.target}</Text>
              {selectedElement.label && <Text>Type: {selectedElement.label}</Text>}
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default FlowVisualization;
