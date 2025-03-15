import React, { useState, useEffect } from 'react';
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

const FlowVisualization = ({ executionTrace, flowId }) => {
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
