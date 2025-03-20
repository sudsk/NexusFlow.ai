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
  FiCpu, 
  FiServer, 
  FiTool, 
  FiUsers, 
  FiSettings,
  FiPlay
} from 'react-icons/fi';
import { Link, useLocation } from 'react-router-dom';

// NavItem component for sidebar links
const NavItem = ({ icon, children, to, active }) => {
  const activeBg = useColorModeValue('brand.50', 'brand.900');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');
  const activeColor = useColorModeValue('brand.600', 'brand.200');
  const color = useColorModeValue('gray.700', 'gray.200');

  return (
    <Link to={to} style={{ width: '100%' }}>
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

const Sidebar = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
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

  // Sidebar contents
  const SidebarContent = () => (
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
      w="60"
      display={{ base: 'none', md: 'block' }}
    >
      <Flex h="20" alignItems="center" justifyContent="center">
        <Text
          fontSize="2xl"
          fontWeight="bold"
          color="brand.500"
        >
          NexusFlow.ai
        </Text>
      </Flex>
      <VStack spacing={1} align="stretch">
        <NavItem icon={FiHome} to="/" active={isActive('/')}>
          Dashboard
        </NavItem>
        <NavItem icon={FiActivity} to="/flows" active={isActive('/flows')}>
          Flows
        </NavItem>
        <NavItem icon={FiCpu} to="/agents" active={isActive('/agents')}>
          Agents
        </NavItem>
        <NavItem icon={FiTool} to="/tools" active={isActive('/tools')}>
          Tools
        </NavItem>
        <NavItem icon={FiPlay} to="/executions" active={isActive('/executions')}>
          Executions
        </NavItem>
        <Divider my={2} />
        <NavItem icon={FiServer} to="/deployments" active={isActive('/deployments')}>
          Deployments
        </NavItem>
        <NavItem icon={FiUsers} to="/capabilities" active={isActive('/capabilities')}>
          Capabilities
        </NavItem>
        <Divider my={2} />
        <NavItem icon={FiSettings} to="/settings" active={isActive('/settings')}>
          Settings
        </NavItem>
      </VStack>
    </Box>
  );

  // Mobile drawer for sidebar
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
          <VStack spacing={1} align="stretch">
            <NavItem icon={FiHome} to="/" active={isActive('/')} onClick={onClose}>
              Dashboard
            </NavItem>
            <NavItem icon={FiActivity} to="/flows" active={isActive('/flows')} onClick={onClose}>
              Flows
            </NavItem>
            <NavItem icon={FiCpu} to="/agents" active={isActive('/agents')} onClick={onClose}>
              Agents
            </NavItem>
            <NavItem icon={FiTool} to="/tools" active={isActive('/tools')} onClick={onClose}>
              Tools
            </NavItem>
            <NavItem icon={FiPlay} to="/executions" active={isActive('/executions')} onClick={onClose}>
              Executions
            </NavItem>
            <Divider my={2} />
            <NavItem icon={FiServer} to="/deployments" active={isActive('/deployments')} onClick={onClose}>
              Deployments
            </NavItem>
            <NavItem icon={FiUsers} to="/capabilities" active={isActive('/capabilities')} onClick={onClose}>
              Capabilities
            </NavItem>
            <Divider my={2} />
            <NavItem icon={FiSettings} to="/settings" active={isActive('/settings')} onClick={onClose}>
              Settings
            </NavItem>
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );

  return (
    <>
      <SidebarContent />
      <MobileDrawer />
    </>
  );
};

export default Sidebar;
