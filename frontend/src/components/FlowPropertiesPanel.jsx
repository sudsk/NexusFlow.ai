// frontend/src/components/FlowPropertiesPanel.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  VStack,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  FormHelperText,
  Spinner,
  Tag,
  HStack,
  Tooltip,
  IconButton,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiInfo } from 'react-icons/fi';
import apiService from '../services/api';

const FlowPropertiesPanel = ({ 
  name, 
  description, 
  framework = 'langgraph',
  maxSteps = 10, 
  onNameChange, 
  onDescriptionChange, 
  onFrameworkChange,
  onMaxStepsChange 
}) => {
  const [frameworks, setFrameworks] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  
  // Fetch available frameworks
  useEffect(() => {
    const fetchFrameworks = async () => {
      setIsLoading(true);
      try {
        const response = await apiService.frameworks.getAll();
        setFrameworks(response.data || {});
      } catch (error) {
        console.error('Error fetching frameworks:', error);
        // Set default frameworks in case of error
        setFrameworks({
          langgraph: {
            multi_agent: true,
            parallel_execution: true,
            tools: true,
            streaming: true,
            visualization: true
          },
          crewai: {
            multi_agent: true,
            parallel_execution: false,
            tools: true,
            streaming: false,
            visualization: true
          }
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchFrameworks();
  }, []);
  
  // Helper to render feature tags for a framework
  const renderFeatureTags = (features) => {
    return (
      <HStack spacing={1} mt={1} flexWrap="wrap">
        {Object.entries(features).map(([feature, supported]) => (
          <Tag 
            key={feature}
            size="sm" 
            colorScheme={supported ? "green" : "red"}
            variant={supported ? "solid" : "outline"}
          >
            {feature.replace(/_/g, ' ')}
          </Tag>
        ))}
      </HStack>
    );
  };
  
  const borderColor = useColorModeValue("gray.200", "gray.600");
  
  return (
    <Box>
      <Heading size="sm" mb={4}>Flow Properties</Heading>
      <VStack spacing={4} align="stretch">
        <FormControl isRequired>
          <FormLabel>Flow Name</FormLabel>
          <Input
            value={name}
            onChange={(e) => onNameChange(e.target.value)}
            placeholder="Enter flow name"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Description</FormLabel>
          <Textarea
            value={description}
            onChange={(e) => onDescriptionChange(e.target.value)}
            placeholder="Enter flow description"
            rows={4}
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>
            Framework
            <Tooltip label="The AI orchestration framework that will execute this flow">
              <IconButton
                aria-label="Framework info"
                icon={<FiInfo />}
                size="xs"
                variant="ghost"
                ml={1}
              />
            </Tooltip>
          </FormLabel>
          
          {isLoading ? (
            <Spinner size="sm" ml={2} />
          ) : (
            <>
              <Select
                value={framework}
                onChange={(e) => onFrameworkChange && onFrameworkChange(e.target.value)}
              >
                {Object.keys(frameworks).map((key) => (
                  <option key={key} value={key}>
                    {key.charAt(0).toUpperCase() + key.slice(1)}
                  </option>
                ))}
              </Select>
              
              {/* Show features for selected framework */}
              {framework && frameworks[framework] && (
                <Box mt={2} p={2} borderWidth="1px" borderRadius="md" borderColor={borderColor}>
                  <FormHelperText mb={1}>Framework Features:</FormHelperText>
                  {renderFeatureTags(frameworks[framework])}
                </Box>
              )}
            </>
          )}
        </FormControl>
        
        <FormControl>
          <FormLabel>Max Execution Steps</FormLabel>
          <NumberInput
            value={maxSteps}
            onChange={(valueString, valueNumber) => 
              onMaxStepsChange && onMaxStepsChange(valueNumber)
            }
            min={1}
            max={50}
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
          <FormHelperText>
            Maximum number of steps before execution stops
          </FormHelperText>
        </FormControl>
      </VStack>
    </Box>
  );
};

export default FlowPropertiesPanel;
