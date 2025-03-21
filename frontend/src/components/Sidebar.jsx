// frontend/src/components/Sidebar.jsx
import React from 'react';
import {
  Box,
  VStack,
  Flex,
  Text,
  Icon,
  Divider,
  useColorModeValue,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  DrawerBody,
  useDisclosure
} from '@chakra-ui/react';
import { 
  FiHome, 
  FiActivity, 
  FiServer, 
  FiTool, 
  FiSettings,
  FiPlay
} from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';

// NavItem component for sidebar links
const NavItem = ({ icon, children, to, active, onClick }) => {
  const activeBg = useColorModeValue('brand.50', 'brand.900');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  const activeColor = useColorModeValue('brand.600', 'brand.200');
  const color = useColorModeValue('gray.700', 'gray.200');

  return (
    <Link to={to} style={{ width: '100%' }} onClick={onClick}>
      <Flex
        align="center"
        p="3"
        mx="2"
        borderRadius="md"
        role="group"
        cursor="pointer"
        _hover={{ bg: hoverBg }}
        bg={active ? activeBg : 'transparent'}
        color={active ? activeColor : color}
        fontWeight={active ? 'bold' : 'normal'}
      >
        <Icon
          mr="3"
          fontSize="16"
          as={icon}
        />
        {children}
      </Flex>
    </Link>
  );
};

const Sidebar = ({ isOpen, onClose, width = "240px" }) => {
  const location = useLocation();
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const bgColor = useColorModeValue('white', 'gray.800');
  const { isOpen: drawerIsOpen, onOpen, onClose: onDrawerClose } = useDisclosure();

  // Function to check if a nav item is active
  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') {
      return true;
    }
    return path !== '/' && location.pathname.startsWith(path);
  };

  // Sidebar content (shared between desktop and mobile)
  const SidebarContent = ({ onClickLink }) => (
    <VStack spacing={1} align="stretch" width="100%">
      <Flex h="20" alignItems="center" justifyContent="center">
        <Text
          fontSize="2xl"
          fontWeight="bold"
          color="brand.500"
        >
          NexusFlow.ai
        </Text>
      </Flex>
      
      <NavItem 
        icon={FiHome} 
        to="/" 
        active={isActive('/')}
        onClick={onClickLink}
      >
        Dashboard
      </NavItem>
      
      <NavItem 
        icon={FiActivity} 
        to="/flows" 
        active={isActive('/flows')}
        onClick={onClickLink}
      >
        Flow Designer
      </NavItem>
      
      <NavItem 
        icon={FiPlay} 
        to="/executions" 
        active={isActive('/executions')}
        onClick={onClickLink}
      >
        Flow Testing
      </NavItem>
      
      <NavItem 
        icon={FiTool} 
        to="/tools" 
        active={isActive('/tools')}
        onClick={onClickLink}
      >
        Tools
      </NavItem>
      
      <Divider my={2} />
      
      <NavItem 
        icon={FiServer} 
        to="/deployments" 
        active={isActive('/deployments')}
        onClick={onClickLink}
      >
        Deployments
      </NavItem>
      
      <Divider my={2} />
      
      <NavItem 
        icon={FiSettings} 
        to="/settings" 
        active={isActive('/settings')}
        onClick={onClickLink}
      >
        Settings
      </NavItem>
    </VStack>
  );

  // Mobile drawer view
  const MobileDrawer = () => (
    <Drawer
      isOpen={!isOpen ? false : drawerIsOpen}
      placement="left"
      onClose={onDrawerClose}
      returnFocusOnClose={false}
    >
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>Navigation</DrawerHeader>
        <DrawerBody padding={0}>
          <SidebarContent onClickLink={onDrawerClose} />
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );

  return (
    <>
      {/* Desktop sidebar - Using position absolute/fixed causes z-index issues */}
      {/* Instead, we'll use a normal div that's part of the flex layout */}
      <Box
        width={width}
        height="100vh"
        overflow="hidden"
        bg={bgColor}
        borderRight="1px"
        borderRightColor={borderColor}
        position="fixed"
        left={0}
        top={0}
        zIndex={10}
        display={{ base: 'none', md: isOpen ? 'block' : 'none' }}
      >
        <Box overflowY="auto" height="100%">
          <SidebarContent />
        </Box>
      </Box>

      {/* Mobile drawer */}
      <MobileDrawer />
    </>
  );
};

export default Sidebar;
