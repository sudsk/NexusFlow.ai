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
  useColorModeValue,
  Text
} from '@chakra-ui/react';
import { 
  FiMenu, 
  FiMoon, 
  FiSun, 
  FiUser, 
  FiLogOut, 
  FiSettings, 
  FiChevronLeft, 
  FiChevronRight 
} from 'react-icons/fi';
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
      zIndex="15"
      width="100%"
    >
      <Flex alignItems="center">
        {/* Toggle sidebar button */}
        <IconButton
          icon={isSidebarOpen ? <FiChevronLeft /> : <FiChevronRight />}
          variant="ghost"
          onClick={onToggleSidebar}
          aria-label={isSidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          mr={2}
        />
        
        <Heading size="md" color="brand.500">
          NexusFlow.ai
        </Heading>
  
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
