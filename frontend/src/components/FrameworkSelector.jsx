// frontend/src/components/FrameworkSelector.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Card,
  CardBody,
  Heading,
  Text,
  Tag,
  HStack,
  VStack,
  Flex,
  Icon,
  Spinner,
  useRadioGroup,
  useColorModeValue,
  useToast,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import { FiCheck, FiCpu, FiUsers, FiCodepen, FiZap, FiTool, FiActivity, FiInfo } from 'react-icons/fi';
import apiService from '../services/api';

// Custom radio card component
const RadioCard = ({ children, isChecked, framework, onSelect, ...rest }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const activeColor = useColorModeValue('blue.50', 'blue.900');
  const activeBorderColor = useColorModeValue('blue.500', 'blue.400');

  // Framework-specific color and icon
  const getFrameworkColor = (name) => {
    switch (name) {
      case 'langgraph':
        return 'blue';
      case 'crewai':
        return 'purple';
      case 'autogen':
        return 'green';
      case 'dspy':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const getFrameworkIcon = (name) => {
    switch (name) {
      case 'langgraph':
        return FiActivity;
      case 'crewai':
        return FiUsers;
      case 'autogen':
        return FiCpu;
      case 'dspy':
        return FiCodepen;
      default:
        return FiZap;
    }
  };

  const color = getFrameworkColor(framework);
  const FrameworkIcon = getFrameworkIcon(framework);

  return (
    <Box
      as="label"
      cursor="pointer"
      onClick={() => onSelect(framework)}
      data-checked={isChecked}
      w="100%"
      h="100%"
      {...rest}
    >
      <Card
        bg={isChecked ? activeColor : bgColor}
        borderWidth="2px"
        borderColor={isChecked ? activeBorderColor : borderColor}
        borderRadius="lg"
        _hover={{ borderColor: isChecked ? activeBorderColor : `${color}.400` }}
        h="100%"
        boxShadow={isChecked ? "md" : "sm"}
        transition="all 0.2s"
      >
        <CardBody>
          <Flex direction="column" h="100%">
            <Flex justify="space-between" mb={2}>
              <HStack>
                <Icon 
                  as={FrameworkIcon} 
                  color={`${color}.500`} 
                  boxSize={5} 
                />
                <Heading size="md" fontWeight="bold" color={`${color}.600`}>
                  {framework.charAt(0).toUpperCase() + framework.slice(1)}
                </Heading>
              </HStack>
              {isChecked && (
                <Box bg={`${color}.500`} borderRadius="full" p={1} color="white">
                  <FiCheck size={14} />
                </Box>
              )}
            </Flex>
            
            {children}
          </Flex>
        </CardBody>
      </Card>
    </Box>
  );
};

const FrameworkSelector = ({ value, onChange }) => {
  const [frameworks, setFrameworks] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [expandedFramework, setExpandedFramework] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchFrameworks = async () => {
      setIsLoading(true);
      try {
        const response = await apiService.frameworks.getAll();
        setFrameworks(response.data || {});
      } catch (error) {
        console.error('Error fetching frameworks:', error);
        toast({
          title: 'Failed to load frameworks',
          description: error.response?.data?.detail || error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        
        // Set some default frameworks
        setFrameworks({
          langgraph: {
            multi_agent: true,
            parallel_execution: true,
            tools: true,
            streaming: true,
            visualization: true
          },
          crewai: {
            multi_agent: true,
            parallel_execution: false,
            tools: true,
            streaming: false,
            visualization: true
          }
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchFrameworks();
  }, [toast]);

  // React-chakra radio group hook
  const { getRootProps, getRadioProps } = useRadioGroup({
    name: 'framework',
    value,
    onChange,
  });

  const group = getRootProps();

  // Helper to render feature tags
  const renderFeatureTags = (features) => {
    return (
      <HStack spacing={1} mt={2} flexWrap="wrap">
        {Object.entries(features).map(([feature, supported]) => (
          <Tag 
            key={feature}
            size="sm" 
            colorScheme={supported ? "green" : "gray"}
            variant={supported ? "solid" : "outline"}
          >
            {feature.replace(/_/g, ' ')}
          </Tag>
        ))}
      </HStack>
    );
  };

  // Framework descriptions
  const descriptions = {
    langgraph: "State-of-the-art graph-based framework for agents with complex state management",
    crewai: "Multi-agent framework focused on team-based collaboration and role assignment",
    autogen: "Versatile framework for multi-agent conversations with autonomous execution",
    dspy: "DSPy provides a more programmatic approach to multi-stage reasoning"
  };

  // Framework detailed information
  const frameworkDetails = {
    langgraph: {
      pros: [
        "Strong state management capabilities",
        "Support for complex agent interactions",
        "Parallel execution of agent tasks",
        "Stream responses in real-time",
        "Detailed execution tracing",
      ],
      cons: [
        "More complex setup for simple scenarios",
        "Steeper learning curve"
      ],
      bestFor: [
        "Complex multi-step reasoning",
        "State-dependent agent workflows",
        "Applications requiring traceability",
        "Parallel processing of tasks"
      ]
    },
    crewai: {
      pros: [
        "Intuitive agent role definitions",
        "Simple collaboration patterns",
        "Human-like delegation between agents",
        "Easy to understand agent relationships"
      ],
      cons: [
        "Limited parallel processing",
        "Less granular control over execution",
        "No streaming support"
      ],
      bestFor: [
        "Team-based agent collaboration",
        "Role-specialized workflows",
        "Human-like delegation patterns",
        "Simpler, sequential workflows"
      ]
    }
  };

  // Toggle expanded framework details
  const toggleDetails = (framework) => {
    if (expandedFramework === framework) {
      setExpandedFramework(null);
    } else {
      setExpandedFramework(framework);
    }
  };

  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="200px">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }

  return (
    <Box>
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mt={4} {...group}>
        {Object.keys(frameworks).map((framework) => {
          const radio = getRadioProps({ value: framework });
          
          return (
            <RadioCard
              key={framework}
              {...radio}
              isChecked={value === framework}
              framework={framework}
              onSelect={onChange}
            >
              <VStack align="start" spacing={1}>
                <Text color="gray.600" fontSize="sm">
                  {descriptions[framework] || `${framework} framework`}
                </Text>
                
                {renderFeatureTags(frameworks[framework])}
                
                {frameworkDetails[framework] && (
                  <Box w="100%" mt={2}>
                    <Box 
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleDetails(framework);
                      }}
                      cursor="pointer"
                      color="blue.500"
                      fontSize="sm"
                      fontWeight="medium"
                      mt={1}
                    >
                      <HStack>
                        <Icon as={FiInfo} />
                        <Text>{expandedFramework === framework ? "Hide details" : "Show details"}</Text>
                      </HStack>
                    </Box>
                    
                    {expandedFramework === framework && (
                      <Accordion allowToggle mt={2} onClick={(e) => e.stopPropagation()}>
                        <AccordionItem border="none">
                          <AccordionButton px={0} _hover={{ bg: 'transparent' }}>
                            <Box as="span" flex='1' textAlign='left' fontWeight="medium">
                              Best For
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={2} pt={0}>
                            <VStack align="start" spacing={1}>
                              {frameworkDetails[framework].bestFor.map((item, idx) => (
                                <Text key={idx} fontSize="sm">• {item}</Text>
                              ))}
                            </VStack>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem border="none">
                          <AccordionButton px={0} _hover={{ bg: 'transparent' }}>
                            <Box as="span" flex='1' textAlign='left' fontWeight="medium">
                              Pros & Cons
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={2} pt={0}>
                            <VStack align="start" spacing={2} width="100%">
                              <Box width="100%">
                                <Text fontSize="sm" fontWeight="medium" color="green.500">Pros:</Text>
                                <VStack align="start" spacing={1}>
                                  {frameworkDetails[framework].pros.map((item, idx) => (
                                    <Text key={idx} fontSize="sm">• {item}</Text>
                                  ))}
                                </VStack>
                              </Box>
                              
                              <Box width="100%">
                                <Text fontSize="sm" fontWeight="medium" color="red.500">Cons:</Text>
                                <VStack align="start" spacing={1}>
                                  {frameworkDetails[framework].cons.map((item, idx) => (
                                    <Text key={idx} fontSize="sm">• {item}</Text>
                                  ))}
                                </VStack>
                              </Box>
                            </VStack>
                          </AccordionPanel>
                        </AccordionItem>
                      </Accordion>
                    )}
                  </Box>
                )}
              </VStack>
            </RadioCard>
          );
        })}
      </SimpleGrid>
    </Box>
  );
};

export default FrameworkSelector;
