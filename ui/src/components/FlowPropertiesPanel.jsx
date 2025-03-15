/* eslint-disable no-unused-vars */
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

const FlowPropertiesPanel = ({ name, description, onNameChange, onDescriptionChange, maxSteps = 10, onMaxStepsChange }) => {
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
        
        <Box p={4} borderWidth="1px" borderRadius="md" bg="gray.50">
          <Heading size="xs" mb={2}>Flow Structure</Heading>
          <Box fontSize="sm" color="gray.600">
            Drag agent nodes from the left panel to the canvas, then connect them to create your flow.
          </Box>
        </Box>
      </VStack>
    </Box>
  );
};

export default FlowPropertiesPanel;
