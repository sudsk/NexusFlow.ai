// frontend/src/components/FrameworkUsageWidget.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Flex,
  Spinner,
  useColorModeValue,
} from '@chakra-ui/react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import apiService from '../services/api';

// Framework colors
const FRAMEWORK_COLORS = {
  langgraph: '#3182CE', // blue.500
  crewai: '#805AD5',    // purple.500
  autogen: '#38A169',   // green.500
  dspy: '#DD6B20',      // orange.500
  other: '#718096',     // gray.500
};

const FrameworkUsageWidget = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'white');

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // In a real implementation, this would fetch data from the API
        // For now, we'll use mock data
        
        // Mock API call
        // const response = await apiService.flows.getFrameworkUsage();
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data
        const mockData = [
          { name: 'LangGraph', value: 65, id: 'langgraph' },
          { name: 'CrewAI', value: 25, id: 'crewai' },
          { name: 'AutoGen', value: 10, id: 'autogen' },
        ];
        
        setData(mockData);
      } catch (error) {
        console.error('Error fetching framework usage data:', error);
        setError('Failed to load framework usage data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <Box 
          p={2} 
          bg={cardBg} 
          borderWidth="1px" 
          borderColor={borderColor}
          borderRadius="md"
          boxShadow="sm"
        >
          <Text fontWeight="bold" color={payload[0].payload.fill}>
            {payload[0].name}: {payload[0].value}%
          </Text>
        </Box>
      );
    }
    
    return null;
  };

  if (isLoading) {
    return (
      <Box
        p={5}
        bg={cardBg}
        borderWidth="1px"
        borderColor={borderColor}
        borderRadius="lg"
        boxShadow="sm"
        height="300px"
      >
        <Heading size="md" mb={4}>Framework Usage</Heading>
        <Flex justify="center" align="center" height="85%">
          <Spinner color="blue.500" />
        </Flex>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        p={5}
        bg={cardBg}
        borderWidth="1px"
        borderColor={borderColor}
        borderRadius="lg"
        boxShadow="sm"
      >
        <Heading size="md" mb={4}>Framework Usage</Heading>
        <Flex justify="center" align="center" height="200px">
          <Text color="red.500">{error}</Text>
        </Flex>
      </Box>
    );
  }

  return (
    <Box
      p={5}
      bg={cardBg}
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="lg"
      boxShadow="sm"
      height="300px"
    >
      <Heading size="md" mb={2}>Framework Usage</Heading>
      <Text fontSize="sm" color="gray.500" mb={4}>
        Distribution of AI frameworks across all flows
      </Text>
      
      <ResponsiveContainer width="100%" height="80%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry) => (
              <Cell 
                key={`cell-${entry.id}`} 
                fill={FRAMEWORK_COLORS[entry.id] || FRAMEWORK_COLORS.other} 
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default FrameworkUsageWidget;
