/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Button,
  VStack,
  Select,
  Textarea,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Tag,
  TagLabel,
  TagCloseButton,
  HStack,
  useDisclosure,
} from '@chakra-ui/react';
import CapabilitySelector from './CapabilitySelector';

const NodePropertiesPanel = ({ node, onChange }) => {
  const [formData, setFormData] = useState({
    label: '',
    model: '',
    temperature: 0.7,
    systemMessage: '',
    capabilities: [],
    toolNames: []
  });
  
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    if (node && node.data) {
      setFormData({
        label: node.data.label || '',
        model: node.data.model || 'openai/gpt-4',
        temperature: node.data.temperature || 0.7,
        systemMessage: node.data.systemMessage || '',
        capabilities: node.data.capabilities || [],
        toolNames: node.data.toolNames || []
      });
    }
  }, [node]);

  const handleChange = (field, value) => {
    const newFormData = {
      ...formData,
      [field]: value
    };
    setFormData(newFormData);
    
    // Propagate changes to parent
    if (onChange) {
      onChange(newFormData);
    }
  };

  const handleCapabilityChange = (selectedCapabilities) => {
    handleChange('capabilities', selectedCapabilities);
  };

  const handleRemoveTool = (tool) => {
    const newTools = formData.toolNames.filter(t => t !== tool);
    handleChange('toolNames', newTools);
  };

  const availableModels = [
    { label: 'OpenAI GPT-4', value: 'openai/gpt-4' },
    { label: 'OpenAI GPT-3.5 Turbo', value: 'openai/gpt-3.5-turbo' },
    { label: 'Anthropic Claude 3 Opus', value: 'anthropic/claude-3-opus' },
    { label: 'Anthropic Claude 3 Sonnet', value: 'anthropic/claude-3-sonnet' },
    { label: 'Google Gemini Pro', value: 'vertex_ai/gemini-1.5-pro' }
  ];

  const availableTools = [
    { name: 'web_search', description: 'Search the web for information' },
    { name: 'data_analysis', description: 'Analyze data and generate insights' },
    { name: 'code_execution', description: 'Execute code in a sandbox environment' },
    { name: 'retrieve_information', description: 'Retrieve information from the knowledge base' }
  ];

  const handleAddTool = (e) => {
    const toolName = e.target.value;
    if (toolName && !formData.toolNames.includes(toolName)) {
      const newTools = [...formData.toolNames, toolName];
      handleChange('toolNames', newTools);
    }
    e.target.value = '';  // Reset select
  };

  return (
    <Box>
      <Heading size="sm" mb={4}>Agent Properties</Heading>
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>Name</FormLabel>
          <Input
            value={formData.label}
            onChange={(e) => handleChange('label', e.target.value)}
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Model</FormLabel>
          <Select
            value={formData.model}
            onChange={(e) => handleChange('model', e.target.value)}
          >
            {availableModels.map((model) => (
              <option key={model.value} value={model.value}>
                {model.label}
              </option>
            ))}
          </Select>
        </FormControl>
        
        <FormControl>
          <FormLabel>Temperature</FormLabel>
          <NumberInput
            value={formData.temperature}
            onChange={(valueString, valueNumber) => handleChange('temperature', valueNumber)}
            step={0.1}
            min={0}
            max={1}
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>
        
        <FormControl>
          <FormLabel>System Message</FormLabel>
          <Textarea
            value={formData.systemMessage}
            onChange={(e) => handleChange('systemMessage', e.target.value)}
            placeholder="Instructions for the agent..."
            rows={4}
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Capabilities</FormLabel>
          <CapabilitySelector
            selectedCapabilities={formData.capabilities}
            onChange={handleCapabilityChange}
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Tools</FormLabel>
          <Select
            placeholder="Add a tool..."
            onChange={handleAddTool}
            defaultValue=""
          >
            {availableTools.map((tool) => (
              <option key={tool.name} value={tool.name}>
                {tool.name}
              </option>
            ))}
          </Select>
          
          <HStack spacing={2} mt={2} flexWrap="wrap">
            {formData.toolNames.map((tool) => (
              <Tag
                key={tool}
                size="md"
                borderRadius="full"
                variant="solid"
                colorScheme="blue"
                m={1}
              >
                <TagLabel>{tool}</TagLabel>
                <TagCloseButton onClick={() => handleRemoveTool(tool)} />
              </Tag>
            ))}
          </HStack>
        </FormControl>
      </VStack>
    </Box>
  );
};

export default NodePropertiesPanel;
