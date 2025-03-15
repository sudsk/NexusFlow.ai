// File: src/pages/AgentList.jsx
import React from 'react';
import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react';
import { FiPlus } from 'react-icons/fi';

const AgentList = () => {
  return (
    <Box>
      <Heading size="lg" mb={6}>Agents</Heading>
      <VStack spacing={4} align="start" p={6} borderWidth="1px" borderRadius="lg">
        <Text>This is a placeholder for the Agents page.</Text>
        <Text>Here you would see a list of available agents in your NexusFlow system.</Text>
        <Button leftIcon={<FiPlus />} colorScheme="blue">Add New Agent</Button>
      </VStack>
    </Box>
  );
};

export default AgentList;
