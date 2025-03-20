// frontend/src/components/NodePropertiesPanel.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  FormHelperText,
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
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Switch,
  Text,
  Divider,
  Badge,
  useDisclosure,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import CapabilitySelector from './CapabilitySelector';

const NodePropertiesPanel = ({ 
  node, 
  onChange, 
  capabilities = [], 
  tools = [],
  framework = 'langgraph' 
}) => {
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

  // Models based on framework
  const getAvailableModels = () => {
    const baseModels = [
      { label: 'OpenAI GPT-4', value: 'openai/gpt-4' },
      { label: 'OpenAI GPT-3.5 Turbo', value: 'openai/gpt-3.5-turbo' },
      { label: 'Anthropic Claude 3 Opus', value: 'anthropic/claude-3-opus' },
      { label: 'Anthropic Claude 3 Sonnet', value: 'anthropic/claude-3-sonnet' },
      { label: 'Google Gemini Pro', value: 'vertex_ai/gemini-1.5-pro' }
    ];
    
    // Framework-specific models or restrictions
    switch(framework) {
      case 'langgraph':
        return baseModels;
      case 'crewai':
        return baseModels;
      case 'autogen':
        return baseModels.filter(model => 
          model.value.startsWith('openai/') || model.value.startsWith('anthropic/')
        );
      case 'dspy':
        return baseModels.filter(model => 
          model.value.startsWith('openai/')
        );
      default:
        return baseModels;
    }
  };

  const handleAddTool = (e) => {
    const toolName = e.target.value;
    if (toolName && !formData.toolNames.includes(toolName)) {
      const newTools = [...formData.toolNames, toolName];
      handleChange('toolNames', newTools);
    }
    e.target.value = '';  // Reset select
  };

  // Framework-specific agent configurations
  const renderFrameworkSpecificConfig = () => {
    switch(framework) {
      case 'langgraph':
        return (
          <FormControl>
            <FormLabel>State Access</FormLabel>
            <Select defaultValue="read_write">
              <option value="read_write">Read & Write</option>
              <option value="read_only">Read Only</option>
              <option value="write_only">Write Only</option>
            </Select>
            <FormHelperText>
              Defines how this agent can interact with the graph state
            </FormHelperText>
          </FormControl>
        );
      case 'crewai':
        return (
          <>
            <FormControl>
              <FormLabel>Agent Role</FormLabel>
              <Input 
                placeholder="e.g., Researcher, Analyst, Writer"
                value={formData.role || ''}
                onChange={(e) => handleChange('role', e.target.value)}
              />
              <FormHelperText>
                The role this agent plays in the crew
              </FormHelperText>
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>Delegation</FormLabel>
              <Switch 
                isChecked={formData.canDelegate !== false}
                onChange={(e) => handleChange('canDelegate', e.target.checked)}
              />
              <FormHelperText>
                Can this agent delegate tasks to other agents?
              </FormHelperText>
            </FormControl>
          </>
        );
      case 'autogen':
        return (
          <>
            <FormControl>
              <FormLabel>Conversation Start</FormLabel>
              <Switch 
                isChecked={formData.isInitiator || false}
                onChange={(e) => handleChange('isInitiator', e.target.checked)}
              />
              <FormHelperText>
                This agent starts the conversation
              </FormHelperText>
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>Human Feedback</FormLabel>
              <Switch 
                isChecked={formData.humanFeedback || false}
                onChange={(e) => handleChange('humanFeedback', e.target.checked)}
              />
              <FormHelperText>
                Allow human feedback for this agent
              </FormHelperText>
            </FormControl>
          </>
        );
      default:
        return null;
    }
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
            {getAvailableModels().map((model) => (
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
          <FormHelperText>
            Higher values make the output more random, lower values make it more deterministic
          </FormHelperText>
        </FormControl>
        
        <FormControl>
          <FormLabel>System Message</FormLabel>
          <Textarea
            value={formData.systemMessage}
            onChange={(e) => handleChange('systemMessage', e.target.value)}
            placeholder="Instructions for the agent..."
            rows={4}
          />
          <FormHelperText>
            Instructions that define the agent's behavior and capabilities
          </FormHelperText>
        </FormControl>
        
        <Accordion allowToggle>
          <AccordionItem border="none">
            <AccordionButton px={0}>
              <Box flex="1" textAlign="left">
                <FormLabel mb={0}>Capabilities</FormLabel>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel pb={4} px={0}>
              <CapabilitySelector
                selectedCapabilities={formData.capabilities}
                onChange={handleCapabilityChange}
              />
            </AccordionPanel>
          </AccordionItem>
          
          <AccordionItem border="none">
            <AccordionButton px={0}>
              <Box flex="1" textAlign="left">
                <FormLabel mb={0}>Tools</FormLabel>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel pb={4} px={0}>
              <FormControl>
                <Select
                  placeholder="Add a tool..."
                  onChange={handleAddTool}
                  defaultValue=""
                >
                  <option value="" disabled>Select a tool to add</option>
                  {tools
                    .filter(tool => !formData.toolNames.includes(tool.name))
                    .map((tool) => (
                      <option key={tool.name} value={tool.name}>
                        {tool.name} - {tool.description}
                      </option>
                    ))}
                </Select>
                
                {formData.toolNames.length > 0 ? (
                  <VStack align="stretch" mt={2}>
                    {formData.toolNames.map((toolName) => {
                      const tool = tools.find(t => t.name === toolName);
                      return (
                        <HStack key={toolName} p={2} borderWidth="1px" borderRadius="md">
                          <Badge colorScheme="green">{toolName}</Badge>
                          <Text fontSize="sm" flex="1">
                            {tool ? tool.description : 'Tool not available in this framework'}
                          </Text>
                          <TagCloseButton onClick={() => handleRemoveTool(toolName)} />
                        </HStack>
                      );
                    })}
                  </VStack>
                ) : (
                  <Text fontSize="sm" color="gray.500" mt={2}>
                    No tools assigned to this agent.
                  </Text>
                )}
                
                <FormHelperText>
                  Select the tools this agent can use
                </FormHelperText>
              </FormControl>
            </AccordionPanel>
          </AccordionItem>
          
          <AccordionItem border="none">
            <AccordionButton px={0}>
              <Box flex="1" textAlign="left">
                <FormLabel mb={0}>Framework Settings</FormLabel>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel pb={4} px={0}>
              <Box mb={2}>
                <Badge colorScheme="blue">{framework}</Badge>
              </Box>
              
              {renderFrameworkSpecificConfig()}
              
              {!renderFrameworkSpecificConfig() && (
                <Alert status="info" mt={2}>
                  <AlertIcon />
                  No specific settings for this framework.
                </Alert>
              )}
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      </VStack>
    </Box>
  );
};

export default NodePropertiesPanel;
