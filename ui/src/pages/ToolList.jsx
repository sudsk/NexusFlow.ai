// File: src/pages/ToolList.jsx
import React from 'react';
import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react';
import { FiPlus } from 'react-icons/fi';

const ToolList = () => {
  return (
    <Box>
      <Heading size="lg" mb={6}>Tools</Heading>
      <VStack spacing={4} align="start" p={6} borderWidth="1px" borderRadius="lg">
        <Text>This is a placeholder for the Tools page.</Text>
        <Text>Here you would see the available tools that agents can use, such as web_search, data_analysis, and code_execution.</Text>
        <Button leftIcon={<FiPlus />} colorScheme="blue">Register New Tool</Button>
      </VStack>
    </Box>
  );
};

export default ToolList;
