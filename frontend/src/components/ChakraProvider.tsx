import { ChakraProvider as BaseChakraProvider, extendTheme } from '@chakra-ui/react';
import type { ReactNode } from 'react';

interface ChakraProviderProps {
  children: ReactNode;
}

// Create a theme instance
const theme = extendTheme({
  colors: {
    brand: {
      50: '#e6f7ff',
      100: '#b3e0ff',
      200: '#80c9ff',
      300: '#4db2ff',
      400: '#1a9bff',
      500: '#0080ff',
      600: '#0066cc',
      700: '#004d99',
      800: '#003366',
      900: '#001a33',
    },
  },
  fonts: {
    heading: `'Inter', sans-serif`,
    body: `'Inter', sans-serif`,
  },
});

export const ChakraProvider = ({ children }: ChakraProviderProps) => {
  return (
    <BaseChakraProvider theme={theme}>
      {children}
    </BaseChakraProvider>
  );
};
