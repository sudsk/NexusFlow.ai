// frontend/src/components/AgentConfigEditor.jsx
import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  VStack,
  HStack,
  Checkbox,
  CheckboxGroup,
  Divider,
  Text,
  useToast,
  Box,
} from '@chakra-ui/react';
import apiService from '../services/api';

const AgentConfigEditor = ({ isOpen, onClose, agent, onSave }) => {
  const [formData, setFormData] = useState({
    label: '',
    model: '',
    temperature: 0.7,
    systemMessage: '',
    capabilities: [],
    toolNames: [],
  });
  const [availableCapabilities, setAvailableCapabilities] = useState([]);
  const [availableTools, setAvailableTools] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  // Initialize form with agent data
  useEffect(() => {
    if (agent) {
      setFormData({
        label: agent.label || '',
        model: agent.model || 'openai/gpt-4',
        temperature: agent.temperature || 0.7,
        systemMessage: agent.systemMessage || '',
        capabilities: agent.capabilities || [],
        toolNames: agent.toolNames || [],
      });
    }
  }, [agent]);

  // Fetch capabilities and tools on mount
  useEffect(() => {
    const fetchCapabilitiesAndTools = async () => {
      setIsLoading(true);
      try {
        // Fetch capabilities
        const capabilitiesResponse = await apiService.capabilities.getAll();
        setAvailableCapabilities(capabilitiesResponse?.data || []);

        // Fetch tools
        const toolsResponse = await apiService.tools.getAll();
        setAvailableTools(toolsResponse?.data?.items || []);
      } catch (error) {
        console.error('Error fetching data:', error);
        toast({
          title: 'Error fetching data',
          description: 'Could not load capabilities and tools',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });

        // Set mock data in case of error
        setAvailableCapabilities([
          { type: 'reasoning', name: 'General Reasoning' },
          { type: 'information_retrieval', name: 'Information Retrieval' },
          { type: 'code_generation', name: 'Code Generation' },
          { type: 'data_analysis', name: 'Data Analysis' },
        ]);

        setAvailableTools([
          { id: '1', name: 'web_search', description: 'Search the web for information' },
          { id: '2', name: 'code_execution', description: 'Execute code in a sandbox' },
          { id: '3', name: 'data_analysis', description: 'Analyze data and generate insights' },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCapabilitiesAndTools();
  }, [toast]);

  // Handle form field changes
  const handleChange = (field, value) => {
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  // Handle capabilities selection
  const handleCapabilityChange = (selectedCapabilities) => {
    setFormData({
      ...formData,
      capabilities: selectedCapabilities,
    });
  };

  // Handle tools selection
  const handleToolChange = (e) => {
    const toolName = e.target.value;
    if (!toolName) return;

    if (!formData.toolNames.includes(toolName)) {
      setFormData({
        ...formData,
        toolNames: [...formData.toolNames, toolName],
      });
    }
  };

  // Handle tool removal
  const handleRemoveTool = (toolName) => {
    setFormData({
      ...formData,
      toolNames: formData.toolNames.filter((t) => t !== toolName),
    });
  };

  // Handle form submission
  const handleSubmit = () => {
    if (onSave) {
      onSave(formData);
    }
    onClose();
  };

  // Available models for selection
  const models = [
    { value: 'openai/gpt-4', label: 'OpenAI GPT-4' },
    { value: 'openai/gpt-3.5-turbo', label: 'OpenAI GPT-3.5 Turbo' },
    { value: 'anthropic/claude-3-opus', label: 'Anthropic Claude 3 Opus' },
    { value: 'anthropic/claude-3-sonnet', label: 'Anthropic Claude 3 Sonnet' },
    { value: 'anthropic/claude-3-haiku', label: 'Anthropic Claude 3 Haiku' },
    { value: 'google/gemini-pro', label: 'Google Gemini Pro' },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Configure Agent</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Tabs variant="enclosed">
            <TabList>
              <Tab>Basic Settings</Tab>
              <Tab>Capabilities</Tab>
              <Tab>Tools</Tab>
              <Tab>Advanced</Tab>
            </TabList>

            <TabPanels>
              {/* Basic Settings Tab */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <FormControl isRequired>
                    <FormLabel>Agent Name</FormLabel>
                    <Input
                      value={formData.label}
                      onChange={(e) => handleChange('label', e.target.value)}
                      placeholder="Research Agent"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>Model</FormLabel>
                    <Select
                      value={formData.model}
                      onChange={(e) => handleChange('model', e.target.value)}
                    >
                      {models.map((model) => (
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
                      onChange={(value) => handleChange('temperature', parseFloat(value))}
                      min={0}
                      max={1}
                      step={0.1}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </FormControl>
                </VStack>
              </TabPanel>

              {/* Capabilities Tab */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <Text fontSize="sm" color="gray.500">
                    Select the capabilities that this agent should have:
                  </Text>

                  <CheckboxGroup
                    colorScheme="green"
                    value={formData.capabilities}
                    onChange={handleCapabilityChange}
                  >
                    <VStack align="start" spacing={3}>
                      {availableCapabilities.map((capability) => (
                        <Checkbox key={capability.type} value={capability.type}>
                          {capability.name}
                        </Checkbox>
                      ))}
                    </VStack>
                  </CheckboxGroup>
                </VStack>
              </TabPanel>

              {/* Tools Tab */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <FormControl>
                    <FormLabel>Add Tool</FormLabel>
                    <Select placeholder="Select a tool to add" onChange={handleToolChange}>
                      <option value="">Select a tool</option>
                      {availableTools
                        .filter((tool) => !formData.toolNames.includes(tool.name))
                        .map((tool) => (
                          <option key={tool.id} value={tool.name}>
                            {tool.name} - {tool.description}
                          </option>
                        ))}
                    </Select>
                  </FormControl>

                  <Divider />

                  <Text fontWeight="medium">Selected Tools:</Text>
                  {formData.toolNames.length > 0 ? (
                    <VStack align="stretch" spacing={2}>
                      {formData.toolNames.map((toolName) => {
                        const tool = availableTools.find((t) => t.name === toolName);
                        return (
                          <HStack key={toolName} p={2} borderWidth="1px" borderRadius="md">
                            <Box flex="1">
                              <Text fontWeight="bold">{toolName}</Text>
                              {tool && <Text fontSize="sm">{tool.description}</Text>}
                            </Box>
                            <Button
                              size="xs"
                              colorScheme="red"
                              onClick={() => handleRemoveTool(toolName)}
                            >
                              Remove
                            </Button>
                          </HStack>
                        );
                      })}
                    </VStack>
                  ) : (
                    <Text color="gray.500">No tools selected</Text>
                  )}
                </VStack>
              </TabPanel>

              {/* Advanced Tab */}
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  <FormControl>
                    <FormLabel>System Message</FormLabel>
                    <Textarea
                      value={formData.systemMessage}
                      onChange={(e) => handleChange('systemMessage', e.target.value)}
                      placeholder="You are a helpful AI assistant specialized in research and data analysis..."
                      rows={6}
                    />
                  </FormControl>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="blue" onClick={handleSubmit}>
            Save
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default AgentConfigEditor;
