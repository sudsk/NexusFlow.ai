// File: src/pages/Settings.jsx
import React from 'react';
import { 
  Box, 
  Heading, 
  FormControl, 
  FormLabel, 
  Input, 
  VStack, 
  Button, 
  Select, 
  Divider, 
  Text,
  Tabs, 
  TabList, 
  TabPanels, 
  Tab, 
  TabPanel 
} from '@chakra-ui/react';

const Settings = () => {
  return (
    <Box>
      <Heading size="lg" mb={6}>Settings</Heading>
      
      <Tabs>
        <TabList>
          <Tab>General</Tab>
          <Tab>API Keys</Tab>
          <Tab>Providers</Tab>
          <Tab>Advanced</Tab>
        </TabList>
        
        <TabPanels>
          <TabPanel>
            <VStack spacing={6} align="stretch">
              <Heading size="md">General Settings</Heading>
              <Divider />
              
              <FormControl>
                <FormLabel>Default Flow Timeout (seconds)</FormLabel>
                <Input type="number" defaultValue={30} />
              </FormControl>
              
              <FormControl>
                <FormLabel>Default Max Steps</FormLabel>
                <Input type="number" defaultValue={10} />
              </FormControl>
              
              <FormControl>
                <FormLabel>Theme</FormLabel>
                <Select defaultValue="light">
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </Select>
              </FormControl>
              
              <Button colorScheme="blue" alignSelf="flex-start">Save Changes</Button>
            </VStack>
          </TabPanel>
          
          <TabPanel>
            <VStack spacing={6} align="stretch">
              <Heading size="md">API Keys</Heading>
              <Divider />
              
              <Text>Configure API keys for different model providers and services.</Text>
              
              <FormControl>
                <FormLabel>OpenAI API Key</FormLabel>
                <Input type="password" placeholder="sk-..." />
              </FormControl>
              
              <FormControl>
                <FormLabel>Anthropic API Key</FormLabel>
                <Input type="password" placeholder="sk-ant-..." />
              </FormControl>
              
              <FormControl>
                <FormLabel>Google API Key</FormLabel>
                <Input type="password" placeholder="AIza..." />
              </FormControl>
              
              <Button colorScheme="blue" alignSelf="flex-start">Save Keys</Button>
            </VStack>
          </TabPanel>
          
          <TabPanel>
            <Text>Provider settings would go here</Text>
          </TabPanel>
          
          <TabPanel>
            <Text>Advanced settings would go here</Text>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default Settings;
