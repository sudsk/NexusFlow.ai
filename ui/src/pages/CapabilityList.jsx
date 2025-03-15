// File: src/pages/CapabilityList.jsx
import React from 'react';
import { Box, Heading, Text, SimpleGrid, Card, CardBody, Badge, VStack } from '@chakra-ui/react';

const CapabilityList = () => {
  const capabilities = [
    { type: 'reasoning', name: 'General Reasoning', description: 'Ability to reason about general topics and answer questions' },
    { type: 'information_retrieval', name: 'Information Retrieval', description: 'Ability to retrieve relevant information from external sources' },
    { type: 'code_generation', name: 'Code Generation', description: 'Ability to generate code based on requirements' },
    { type: 'data_analysis', name: 'Data Analysis', description: 'Ability to analyze data and generate insights' },
  ];

  return (
    <Box>
      <Heading size="lg" mb={6}>Capabilities</Heading>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
        {capabilities.map((capability) => (
          <Card key={capability.type}>
            <CardBody>
              <VStack align="start" spacing={2}>
                <Heading size="md">{capability.name}</Heading>
                <Badge>{capability.type}</Badge>
                <Text>{capability.description}</Text>
              </VStack>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default CapabilityList;
