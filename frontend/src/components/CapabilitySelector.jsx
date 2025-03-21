// frontend/src/components/CapabilitySelector.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  CheckboxGroup,
  Checkbox,
  Text,
  Badge,
  Input,
  InputGroup,
  InputLeftElement,
  Spinner,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiSearch } from 'react-icons/fi';

// Simple capability selector that can be used within the NodePropertiesPanel
// This does not connect to any backend API as we're removing the standalone capability management
const CapabilitySelector = ({ selectedCapabilities = [], onChange }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredCapabilities, setFilteredCapabilities] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const bg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Static list of common capabilities 
  const capabilities = [
    { type: 'reasoning', name: 'General Reasoning' },
    { type: 'information_retrieval', name: 'Information Retrieval' },
    { type: 'code_generation', name: 'Code Generation' },
    { type: 'data_analysis', name: 'Data Analysis' },
    { type: 'summarization', name: 'Summarization' },
    { type: 'creative_writing', name: 'Creative Writing' },
    { type: 'translation', name: 'Translation' },
    { type: 'question_answering', name: 'Question Answering' },
  ];

  // Filter capabilities based on search query
  useEffect(() => {
    if (!searchQuery) {
      setFilteredCapabilities(capabilities);
      return;
    }
    
    const query = searchQuery.toLowerCase();
    const filtered = capabilities.filter(
      capability => capability.name.toLowerCase().includes(query)
    );
    
    setFilteredCapabilities(filtered);
  }, [searchQuery]);

  // Initialize filteredCapabilities on mount
  useEffect(() => {
    setFilteredCapabilities(capabilities);
  }, []);
  
  // Handle capability selection
  const handleChange = (values) => {
    if (onChange) {
      onChange(values);
    }
  };
  
  return (
    <Box p={3} bg={bg} borderWidth="1px" borderColor={borderColor} borderRadius="md">
      <InputGroup mb={4} size="sm">
        <InputLeftElement pointerEvents="none">
          <FiSearch color="gray.300" />
        </InputLeftElement>
        <Input
          placeholder="Search capabilities..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </InputGroup>
      
      <CheckboxGroup
        colorScheme="green"
        value={selectedCapabilities}
        onChange={handleChange}
      >
        <VStack align="start" spacing={2}>
          {filteredCapabilities.map(capability => (
            <Checkbox key={capability.type} value={capability.type}>
              <HStack>
                <Text>{capability.name}</Text>
                <Badge colorScheme="blue" variant="subtle" fontSize="xs">
                  {capability.type}
                </Badge>
              </HStack>
            </Checkbox>
          ))}
        </VStack>
      </CheckboxGroup>
      
      {filteredCapabilities.length === 0 && (
        <Text fontSize="sm" color="gray.500" textAlign="center" mt={2}>
          No capabilities found matching your search
        </Text>
      )}
    </Box>
  );
};

export default CapabilitySelector;
