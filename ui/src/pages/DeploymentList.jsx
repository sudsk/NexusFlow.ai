// File: src/pages/DeploymentList.jsx
/* eslint-disable no-unused-vars */
import React from 'react';
import { Box, Heading, Text, Button, Table, Thead, Tbody, Tr, Th, Td, Badge, HStack } from '@chakra-ui/react';
import { FiPlus, FiPlay } from 'react-icons/fi';

const DeploymentList = () => {
  const deployments = [
    { id: 'deploy-1', flow_name: 'Research Assistant', version: 'v1', status: 'active', created_at: '2025-03-10T14:25:00Z' },
    { id: 'deploy-2', flow_name: 'Code Generator', version: 'v1', status: 'active', created_at: '2025-03-08T09:17:32Z' }
  ];

  return (
    <Box>
      <Heading size="lg" mb={6}>Deployments</Heading>
      <Box mb={4}>
        <Button leftIcon={<FiPlus />} colorScheme="blue">Deploy Flow</Button>
      </Box>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Flow</Th>
            <Th>Version</Th>
            <Th>Status</Th>
            <Th>Created</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {deployments.map((deployment) => (
            <Tr key={deployment.id}>
              <Td>{deployment.flow_name}</Td>
              <Td>{deployment.version}</Td>
              <Td><Badge colorScheme="green">{deployment.status}</Badge></Td>
              <Td>{new Date(deployment.created_at).toLocaleDateString()}</Td>
              <Td>
                <HStack>
                  <Button size="sm" leftIcon={<FiPlay />} colorScheme="green">Test</Button>
                </HStack>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default DeploymentList;
