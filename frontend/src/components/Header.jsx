// frontend/src/components/Header.jsx
import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Spacer,
  IconButton,
  Button,
  HStack,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useColorMode,
  useColorModeValue
} from '@chakra-ui/react';
import { FiMenu, FiMoon, FiSun, FiUser, FiLogOut, FiSettings, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const Header = ({ onToggleSidebar, isSidebarOpen }) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const navigate = useNavigate();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleLogout = () => {
    apiService.auth.logout();
    navigate('/login');
  };
  
  const isAuthenticated = apiService.auth.isAuthenticated();
  const isMockMode = apiService.mock.isEnabled();

  return (
    <Box 
      as="header" 
      bg={bgColor} 
      borderBottomWidth="1px" 
      borderColor={borderColor} 
      py={2} 
      px={4}
      position="sticky"
      top="0"
      zIndex="10"
    >
      <Flex alignItems="center">
        {/* Sidebar toggle button - visible on all screen sizes */}
        <IconButton
          icon={isSidebarOpen ? <FiChevronLeft /> : <FiChevronRight />}
          variant="ghost"
          onClick={onToggleSidebar}
          aria-label={isSidebarOpen ? "Close sidebar" : "Open sidebar"}
          mr={2}
        />
        
        <Heading size="md" color="brand.500" ml={2}>
          NexusFlow.ai
        </Heading>
        
        {isMockMode && (
          <Box ml={4} px={2} py={1} bg="yellow.100" color="yellow.800" borderRadius="md" fontSize="xs">
            Mock API Mode
          </Box>
        )}
        
        <Spacer />
        
        <HStack spacing={2}>
          <IconButton
            icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
            variant="ghost"
            onClick={toggleColorMode}
            aria-label={colorMode === 'light' ? 'Dark mode' : 'Light mode'}
          />
          
          {isAuthenticated && (
            <Menu>
              <MenuButton
                as={Button}
                rightIcon={<FiUser />}
                variant="ghost"
              >
                Profile
              </MenuButton>
              <MenuList>
                <MenuItem icon={<FiSettings />} onClick={() => navigate('/settings')}>
                  Settings
                </MenuItem>
                <MenuItem icon={<FiLogOut />} onClick={handleLogout}>
                  Logout
                </MenuItem>
              </MenuList>
            </Menu>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default Header;
