/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Checkbox,
  CheckboxGroup,
  SimpleGrid,
  VStack,
  Text,
  Badge,
  useColorModeValue,
  Skeleton,
  Input,
  InputGroup,
  InputLeftElement,
  Icon,
} from '@chakra-ui/react';
import { FiSearch } from 'react-icons/fi';
import axios from 'axios';

const CapabilitySelector = ({ selectedCapabilities = [], onChange }) => {
  const [capabilities, setCapabilities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const badgeBg = useColorModeValue('brand.100', 'brand.800');
  const cardBg = useColorModeValue('white', 'gray.700');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');

  // Fetch available capabilities
  useEffect(() => {
    const fetchCapabilities = async () => {
      setIsLoading(true);
      try {
        // In a real implementation, this would be an API call
        // Mock capabilities for now
        const mockCapabilities = [
          {
            type: 'reasoning',
            name: 'General Reasoning',
            description: 'Ability to reason about general topics and answer questions',
          },
          {
            type: 'information_retrieval',
            name: 'Information Retrieval',
            description: 'Ability to retrieve relevant information from external sources',
          },
          {
            type: 'code_generation',
            name: 'Code Generation',
            description: 'Ability to generate code based on requirements',
          },
          {
            type: 'data_analysis',
            name: 'Data Analysis',
            description: 'Ability to analyze data and generate insights',
          },
          {
            type: 'summarization',
            name: 'Summarization',
            description: 'Ability to summarize text content',
          },
          {
            type: 'planning',
            name: 'Planning',
            description: 'Ability to create plans and break down tasks',
          },
          {
            type: 'coordination',
            name: 'Coordination',
            description: 'Ability to coordinate multiple agents and synthesize their outputs',
          },
        ];
        setCapabilities(mockCapabilities);
      } catch (error) {
        console.error('Error fetching capabilities:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCapabilities();
  }, []);

  // Handle selection changes
  const handleSelectionChange = (values) => {
    if (onChange) {
      onChange(values);
    }
  };

  // Filter capabilities based on search term
  const filteredCapabilities = capabilities.filter((capability) =>
    capability.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    capability.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <VStack align="stretch" spacing={4} w="100%">
      <InputGroup>
        <InputLeftElement pointerEvents="none">
          <Icon as={FiSearch} color="gray.300" />
        </InputLeftElement>
        <Input
          placeholder="Search capabilities..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </InputGroup>

      {isLoading ? (
        <VStack align="stretch" spacing={2}>
          <Skeleton height="80px" />
          <Skeleton height="80px" />
          <Skeleton height="80px" />
        </VStack>
      ) : (
        <CheckboxGroup
          colorScheme="blue"
          value={selectedCapabilities}
          onChange={handleSelectionChange}
        >
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
            {filteredCapabilities.map((capability) => (
              <Box
                key={capability.type}
                p={3}
                borderWidth="1px"
                borderRadius="md"
                borderColor={cardBorder}
                bg={cardBg}
                _hover={{ borderColor: 'brand.500' }}
              >
                <Checkbox value={capability.type}>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">{capability.name}</Text>
                    <Badge bg={badgeBg} fontSize="xs">
                      {capability.type}
                    </Badge>
                    <Text fontSize="sm" color="gray.500">
                      {capability.description}
                    </Text>
                  </VStack>
                </Checkbox>
              </Box>
            ))}
          </SimpleGrid>
        </CheckboxGroup>
      )}
    </VStack>
  );
};

export default CapabilitySelector;
