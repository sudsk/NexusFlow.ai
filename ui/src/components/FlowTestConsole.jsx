// frontend/src/components/FlowTestConsole.jsx
/* eslint-disable no-unused-vars */
import React, { useState } from 'react';
import { Button, Textarea, Spinner, Box } from '@chakra-ui/react';
import FlowExecutionVisualizer from './FlowExecutionVisualizer';

const FlowTestConsole = ({ flowConfig }) => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState(null);
  const [executionTrace, setExecutionTrace] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const testFlow = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/nexusflow/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          flow_config: flowConfig,
          input: { query: input }
        })
      });
      
      const result = await response.json();
      setOutput(result.output);
      setExecutionTrace(result.execution_trace);
    } catch (error) {
      console.error('Error testing flow:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Box className="flow-test-console">
      <Textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter your test query here..."
        mb={4}
      />
      <Button 
        onClick={testFlow}
        isLoading={isLoading}
        colorScheme="blue"
        mb={4}
      >
        Test Flow
      </Button>
      
      {output && (
        <Box className="output-section" mt={4}>
          <h3>Output:</h3>
          <pre>{output.content}</pre>
        </Box>
      )}
      
      {executionTrace.length > 0 && (
        <FlowExecutionVisualizer trace={executionTrace} />
      )}
    </Box>
  );
};
