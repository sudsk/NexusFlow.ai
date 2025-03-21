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
  DrawerBody
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

  // Function to check if a nav item is active
  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') {
      return true;
    }
    return path !== '/' && location.pathname.startsWith(path);
  };

  // For mobile: use a Drawer component
  const MobileDrawer = () => (
    <Drawer
      autoFocus={false}
      isOpen={isOpen}
      placement="left"
      onClose={onClose}
      returnFocusOnClose={false}
      onOverlayClick={onClose}
      size="full"
    >
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader borderBottomWidth="1px">
          NexusFlow.ai
        </DrawerHeader>
        <DrawerBody p={0}>
          <SidebarContent isMobile={true} />
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );

  // Sidebar contents
  const SidebarContent = ({ isMobile = false }) => (
    <VStack spacing={1} align="stretch">
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
        onClick={isMobile ? onClose : undefined}
      >
        Dashboard
      </NavItem>
      
      <NavItem 
        icon={FiActivity} 
        to="/flows" 
        active={isActive('/flows')}
        onClick={isMobile ? onClose : undefined}
      >
        Flow Designer
      </NavItem>
      
      <NavItem 
        icon={FiPlay} 
        to="/executions" 
        active={isActive('/executions')}
        onClick={isMobile ? onClose : undefined}
      >
        Flow Testing
      </NavItem>
      
      <NavItem 
        icon={FiTool} 
        to="/tools" 
        active={isActive('/tools')}
        onClick={isMobile ? onClose : undefined}
      >
        Tools
      </NavItem>
      
      <Divider my={2} />
      
      <NavItem 
        icon={FiServer} 
        to="/deployments" 
        active={isActive('/deployments')}
        onClick={isMobile ? onClose : undefined}
      >
        Deployments
      </NavItem>
      
      <Divider my={2} />
      
      <NavItem 
        icon={FiSettings} 
        to="/settings" 
        active={isActive('/settings')}
        onClick={isMobile ? onClose : undefined}
      >
        Settings
      </NavItem>
    </VStack>
  );

  return (
    <>
      {/* Desktop sidebar - fixed position */}
      <Box
        as="nav"
        pos="fixed"
        top="0"
        left="0"
        zIndex="sticky"
        h="full"
        pb="10"
        overflowX="hidden"
        overflowY="auto"
        bg={bgColor}
        borderRight="1px"
        borderRightColor={borderColor}
        width={width}
        display={{ base: 'none', md: 'block' }}
        transition="width 0.3s ease-in-out"
      >
        <SidebarContent />
      </Box>

      {/* Mobile sidebar - drawer */}
      <MobileDrawer />
    </>
  );
};

export default Sidebar;
