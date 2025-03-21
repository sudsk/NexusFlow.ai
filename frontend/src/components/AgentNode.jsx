// frontend/src/components/AgentNode.jsx
import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import {
  Box,
  Text,
  Tag,
  HStack,
  VStack,
  Badge,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiCpu, FiInfo, FiTool } from 'react-icons/fi';

// Custom node component for flow builder
const AgentNode = ({ data, selected }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue(
    selected ? 'brand.500' : 'gray.200',
    selected ? 'brand.400' : 'gray.600'
  );
  const shadowColor = useColorModeValue(
    'rgba(0, 0, 0, 0.1)',
    'rgba(0, 0, 0, 0.4)'
  );

  // Get icon based on agent type
  const getAgentIcon = () => {
    switch (data.agentType) {
      case 'reasoner':
        return <FiCpu />;
      case 'tool':
        return <FiTool />;
      default:
        return <FiInfo />;
    }
  };

  return (
    <Box
      bg={bgColor}
      borderWidth="2px"
      borderRadius="md"
      borderColor={borderColor}
      p={3}
      minWidth="180px"
      boxShadow={selected ? `0 0 0 2px ${borderColor}, 0 4px 10px ${shadowColor}` : `0 2px 5px ${shadowColor}`}
      position="relative"
      transition="all 0.2s"
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555', width: 10, height: 10 }}
      />

      <VStack align="stretch" spacing={2}>
        <HStack>
          <Box color="brand.500">{getAgentIcon()}</Box>
          <Text fontWeight="bold" isTruncated>
            {data.label}
          </Text>
        </HStack>

        {data.model && (
          <Badge colorScheme="blue" alignSelf="start">
            {data.model}
          </Badge>
        )}

        {data.capabilities && data.capabilities.length > 0 && (
          <HStack flexWrap="wrap" spacing={1} mt={1}>
            {data.capabilities.slice(0, 3).map((capability, idx) => (
              <Tag size="sm" key={idx} colorScheme="green" variant="subtle">
                {capability}
              </Tag>
            ))}
            {data.capabilities.length > 3 && (
              <Tag size="sm" colorScheme="gray" variant="subtle">
                +{data.capabilities.length - 3}
              </Tag>
            )}
          </HStack>
        )}

        {data.toolNames && data.toolNames.length > 0 && (
          <HStack flexWrap="wrap" spacing={1} mt={1}>
            {data.toolNames.slice(0, 2).map((tool, idx) => (
              <Tag size="sm" key={idx} colorScheme="purple" variant="subtle">
                {tool}
              </Tag>
            ))}
            {data.toolNames.length > 2 && (
              <Tag size="sm" colorScheme="gray" variant="subtle">
                +{data.toolNames.length - 2}
              </Tag>
            )}
          </HStack>
        )}
      </VStack>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555', width: 10, height: 10 }}
      />
    </Box>
  );
};

export default memo(AgentNode);
