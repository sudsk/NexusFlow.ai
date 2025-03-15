import React from 'react';
import {
  Box,
  Flex,
  Text,
  VStack,
  Icon,
  Divider,
  useColorModeValue,
  Tooltip,
} from '@chakra-ui/react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  FiHome,
  FiActivity,
  FiGrid,
  FiServer,
  FiSettings,
  FiTool,
  FiUsers,
} from 'react-icons/fi';

const Sidebar = () => {
  const location = useLocation();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const activeColor = useColorModeValue('brand.500', 'brand.300');
  const hoverColor = useColorModeValue('gray.100', 'gray.700');

  const menuItems = [
    { name: 'Dashboard', icon: FiHome, path: '/' },
    { name: 'Flows', icon: FiActivity, path: '/flows' },
    { name: 'Agents', icon: FiUsers, path: '/agents' },
    { name: 'Tools', icon: FiTool, path: '/tools' },
    { name: 'Capabilities', icon: FiGrid, path: '/capabilities' },
    { name: 'Deployments', icon: FiServer, path: '/deployments' },
    { name: 'Settings', icon: FiSettings, path: '/settings' },
  ];

  return (
    <Box
      as="nav"
      width="64px"
      bg={bgColor}
      borderRight="1px"
      borderColor={borderColor}
      py={6}
      position="sticky"
      top="0"
      h="100vh"
    >
      <VStack spacing={6}>
        <Box p={2}>
          <svg
            width="36"
            height="36"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2L2 7L12 12L22 7L12 2Z"
              fill="currentColor"
              fillOpacity="0.8"
            />
            <path
              d="M2 17L12 22L22 17"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M2 12L12 17L22 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Box>

        <Divider />

        <VStack spacing={4} align="center" width="full">
          {menuItems.map((item) => (
            <Tooltip key={item.name} label={item.name} placement="right">
              <Box width="full" textAlign="center">
                <NavLink to={item.path} end={item.path === '/'}>
                  {({ isActive }) => (
                    <Flex
                      py={3}
                      justifyContent="center"
                      align="center"
                      color={isActive ? activeColor : 'inherit'}
                      _hover={{ bg: hoverColor, color: activeColor }}
                      borderLeft={isActive ? '3px solid' : '3px solid transparent'}
                      borderColor={isActive ? activeColor : 'transparent'}
                    >
                      <Icon as={item.icon} boxSize={5} />
                    </Flex>
                  )}
                </NavLink>
              </Box>
            </Tooltip>
          ))}
        </VStack>
      </VStack>
    </Box>
  );
};

export default Sidebar;
