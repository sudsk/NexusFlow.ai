/* eslint-disable no-unused-vars */
import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Spacer,
  Button,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useColorMode,
  useColorModeValue,
} from '@chakra-ui/react';
import { HamburgerIcon, MoonIcon, SunIcon, SettingsIcon } from '@chakra-ui/icons';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const navigate = useNavigate();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      as="header"
      py={4}
      px={6}
      bg={bgColor}
      boxShadow="sm"
      borderBottom="1px"
      borderColor={borderColor}
    >
      <Flex align="center">
        <Heading size="md" color="brand.500">NexusFlow.ai</Heading>
        
        <Spacer />
        
        <Box display={{ base: 'none', md: 'flex' }}>
          <Button 
            variant="ghost" 
            mr={3}
            onClick={() => navigate('/flows/new')}
          >
            New Flow
          </Button>
          
          <Button 
            variant="ghost" 
            mr={3}
            onClick={() => navigate('/deployments')}
          >
            Deployments
          </Button>
        </Box>
        
        <IconButton
          icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          onClick={toggleColorMode}
          variant="ghost"
          aria-label="Toggle theme"
          mr={3}
        />
        
        <Menu>
          <MenuButton
            as={IconButton}
            icon={<SettingsIcon />}
            variant="ghost"
            aria-label="Settings"
          />
          <MenuList>
            <MenuItem onClick={() => navigate('/profile')}>Profile</MenuItem>
            <MenuItem onClick={() => navigate('/settings')}>Settings</MenuItem>
            <MenuItem onClick={() => navigate('/api-keys')}>API Keys</MenuItem>
            <MenuItem onClick={() => navigate('/logout')}>Logout</MenuItem>
          </MenuList>
        </Menu>
        
        <Box display={{ base: 'inline-flex', md: 'none' }}>
          <Menu>
            <MenuButton
              as={IconButton}
              icon={<HamburgerIcon />}
              variant="ghost"
              aria-label="Menu"
              ml={3}
            />
            <MenuList>
              <MenuItem onClick={() => navigate('/flows/new')}>New Flow</MenuItem>
              <MenuItem onClick={() => navigate('/deployments')}>Deployments</MenuItem>
            </MenuList>
          </Menu>
        </Box>
      </Flex>
    </Box>
  );
};

export default Header;
