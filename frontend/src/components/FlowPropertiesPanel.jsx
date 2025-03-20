// frontend/src/components/FlowPropertiesPanel.jsx
import React from 'react';
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
} from '@chakra-ui/react';

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
          <FormLabel>Framework</FormLabel>
          <Select
            value={framework}
            onChange={(e) => onFrameworkChange && onFrameworkChange(e.target.value)}
          >
            <option value="langgraph">LangGraph</option>
            <option value="crewai">CrewAI</option>
            <option value="autogen">AutoGen</option>
            <option value="dspy">DSPy</option>
          </Select>
          <FormHelperText>
            Select the framework to use for executing this flow
          </FormHelperText>
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
