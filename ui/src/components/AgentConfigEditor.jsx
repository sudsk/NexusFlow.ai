import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  Button,
  FormControl,
  FormLabel,
  Input,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Select,
  Textarea,
  VStack,
  Divider,
  Text,
  useToast,
} from '@chakra-ui/react';
import CapabilitySelector from './CapabilitySelector';
import axios from 'axios';

const AgentConfigEditor = ({ isOpen, onClose, agent, onSave }) => {
  const toast = useToast();
  const [availableModels, setAvailableModels] = useState([]);
  const [availableTools, setAvailableTools] = useState([]);
  const [formData, setFormData] = useState({
    label: '',
    capabilities: [],
    modelProvider: 'openai',
    modelName: 'gpt-4',
    systemMessage: '',
    temperature: 0.7,
    toolNames: [],
  });
  const [isLoading, setIsLoading] = useState(false);

  // Initialize form data from agent props
  useEffect(() => {
    if (agent) {
      setFormData({
        label: agent.label || '',
        capabilities: agent.capabilities || [],
        modelProvider: agent.model?.split('/')[0] || 'openai',
        modelName: agent.model?.split('/')[1] || 'gpt-4',
        systemMessage: agent.systemMessage || '',
        temperature: agent.temperature || 0.7,
        toolNames: agent.toolNames || [],
      });
    }
  }, [agent]);

  // Fetch available models and tools
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // In a real app, these would be API calls
        // For now, we'll use mock data
        setAvailableModels([
          { provider: 'openai', models: ['gpt-4', 'gpt-3.5-turbo'] },
          { provider: 'anthropic', models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'] },
          { provider: 'vertex_ai', models: ['gemini-1.5-pro', 'gemini-1.5-flash'] },
        ]);

        setAvailableTools([
          { name: 'web_search', description: 'Search the web for information' },
          { name: 'data_analysis', description: 'Analyze data and generate insights' },
          { name: 'code_execution', description: 'Execute code in a secure sandbox' },
          { name: 'image_generation', description: 'Generate images from text descriptions' },
        ]);
      } catch (error) {
        toast({
          title: 'Error fetching data',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [toast]);

  // Handle form changes
  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Handle capabilities change from the CapabilitySelector
  const handleCapabilitiesChange = (selectedCapabilities) => {
    setFormData((prev) => ({
      ...prev,
      capabilities: selectedCapabilities,
    }));
  };

  // Handle tool selection
  const handleToolSelect = (e) => {
    const value = e.target.value;
    if (value && !formData.toolNames.includes(value)) {
      setFormData((prev) => ({
        ...prev,
        toolNames: [...prev.toolNames, value],
      }));
    }
  };

  // Remove a tool from selection
  const handleRemoveTool = (tool) => {
    setFormData((prev) => ({
      ...prev,
      toolNames: prev.toolNames.filter((t) => t !== tool),
    }));
  };

  // Handle form submission
  const handleSubmit = () => {
    // Format the data for the parent component
    const formattedData = {
      label: formData.label,
      capabilities: formData.capabilities,
      model: `${formData.modelProvider}/${formData.modelName}`,
      systemMessage: formData.systemMessage,
      temperature: formData.temperature,
      toolNames: formData.toolNames,
    };

    onSave(formattedData);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Configure Agent</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <FormControl isRequired>
              <FormLabel>Agent Name</FormLabel>
              <Input
                value={formData.label}
                onChange={(e) => handleChange('label', e.target.value)}
                placeholder="Enter agent name"
              />
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Capabilities</FormLabel>
              <CapabilitySelector
                selectedCapabilities={formData.capabilities}
                onChange={handleCapabilitiesChange}
              />
            </FormControl>

            <Divider />

            <FormControl isRequired>
              <FormLabel>Model Provider</FormLabel>
              <Select
                value={formData.modelProvider}
                onChange={(e) => handleChange('modelProvider', e.target.value)}
              >
                {availableModels.map((provider) => (
                  <option key={provider.provider} value={provider.provider}>
                    {provider.provider.charAt(0).toUpperCase() + provider.provider.slice(1)}
                  </option>
                ))}
              </Select>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Model</FormLabel>
              <Select
                value={formData.modelName}
                onChange={(e) => handleChange('modelName', e.target.value)}
              >
                {availableModels
                  .find((p) => p.provider === formData.modelProvider)
                  ?.models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>Temperature</FormLabel>
              <NumberInput
                min={0}
                max={1}
                step={0.1}
                value={formData.temperature}
                onChange={(valueString, valueNumber) => 
                  handleChange('temperature', valueNumber)
                }
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
                placeholder="Enter system message for the agent"
                rows={5}
              />
            </FormControl>

            <Divider />

            <FormControl>
              <FormLabel>Tools</FormLabel>
              <Select
                placeholder="Select tools for this agent"
                onChange={handleToolSelect}
                value=""
              >
                {availableTools.map((tool) => (
                  <option key={tool.name} value={tool.name}>
                    {tool.name} - {tool.description}
                  </option>
                ))}
              </Select>
              {formData.toolNames.length > 0 && (
                <VStack mt={2} align="stretch">
                  {formData.toolNames.map((tool) => (
                    <Text key={tool} fontSize="sm">
                      {tool}{' '}
                      <Button
                        size="xs"
                        ml={2}
                        colorScheme="red"
                        onClick={() => handleRemoveTool(tool)}
                      >
                        Remove
                      </Button>
                    </Text>
                  ))}
                </VStack>
              )}
            </FormControl>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="blue" onClick={handleSubmit} isLoading={isLoading}>
            Save
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default AgentConfigEditor;
