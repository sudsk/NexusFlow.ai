import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';

// Define theme
const theme = extendTheme({
  colors: {
    brand: {
      50: '#e0f2ff',
      100: '#b9deff',
      200: '#90caff',
      300: '#64b5ff',
      400: '#3aa0ff',
      500: '#1a91ff', // Primary brand color
      600: '#0077e6',
      700: '#005bb3',
      800: '#003f80',
      900: '#00254d',
    },
  },
  fonts: {
    heading: '"Inter", sans-serif',
    body: '"Inter", sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
      },
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>
);
