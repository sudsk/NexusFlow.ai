import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import {
  Box,
  VStack,
  Heading,
  Text,
  Tag,
  HStack,
  Icon,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiCpu, FiDatabase, FiCode, FiSearch, FiFileText, FiLayers, FiUsers } from 'react-icons/fi';

const getCapabilityIcon = (capability) => {
  switch (capability) {
    case 'reasoning':
      return FiCpu;
    case 'information_retrieval':
      return FiSearch;
    case 'code_generation':
      return FiCode;
    case 'data_analysis':
      return FiDatabase;
    case 'summarization':
      return FiFileText;
    case 'planning':
      return FiLayers;
    case 'coordination':
      return FiUsers;
    default:
      return FiCpu;
  }
};

const AgentNode = ({ data, isConnectable, selected }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = selected 
    ? 'brand.500' 
    : useColorModeValue('gray.200', 'gray.600');
  const shadowColor = useColorModeValue('rgba(0, 0, 0, 0.1)', 'rgba(0, 0, 0, 0.4)');
  
  // Determine primary capability (first in the list or reasoning as default)
  const primaryCapability = data.capabilities && data.capabilities.length > 0 
    ? data.capabilities[0] 
    : 'reasoning';
  
  // Get icon for primary capability
  const PrimaryIcon = getCapabilityIcon(primaryCapability);
  
  return (
    <Box
      padding={3}
      borderWidth="2px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      boxShadow={`0 4px 6px ${shadowColor}`}
      minWidth="200px"
      maxWidth="250px"
      position="relative"
      transition="all 0.2s"
      _hover={{ borderColor: 'brand.400' }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: '#555', width: '8px', height: '8px' }}
        isConnectable={isConnectable}
      />
      
      <VStack spacing={2} align="stretch">
        <HStack>
          <Icon as={PrimaryIcon} boxSize={5} color="brand.500" />
          <Heading size="sm" isTruncated title={data.label}>
            {data.label}
          </Heading>
        </HStack>
        
        <Text fontSize="xs" color="gray.500">
          {data.model || 'No model selected'}
        </Text>
        
        {data.capabilities && data.capabilities.length > 0 && (
          <HStack spacing={1} flexWrap="wrap">
            {data.capabilities.map((capability) => (
              <Tag key={capability} size="sm" variant="subtle" colorScheme="blue" mt={1}>
                {capability}
              </Tag>
            ))}
          </HStack>
        )}
        
        {data.toolNames && data.toolNames.length > 0 && (
          <VStack align="start" spacing={1}>
            <Text fontSize="xs" fontWeight="bold">
              Tools:
            </Text>
            {data.toolNames.map((tool) => (
              <Text key={tool} fontSize="xs" color="gray.600">
                • {tool}
              </Text>
            ))}
          </VStack>
        )}
      </VStack>
      
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: '#555', width: '8px', height: '8px' }}
        isConnectable={isConnectable}
      />
    </Box>
  );
};

export default memo(AgentNode);
