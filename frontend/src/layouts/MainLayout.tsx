import { Box, Container, Stack, VStack } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';

const MainLayout = () => {
  return (
    <VStack minH="100vh" spacing={0} align="stretch">
      <Navbar />
      <Box as="main" flex={1} py={8}>
        <Container maxW="container.xl">
          <Stack spacing={6}>
            <Outlet />
          </Stack>
        </Container>
      </Box>
      <Box as="footer" py={4} bg="gray.100" w="full">
        <Container maxW="container.xl" textAlign="center">
          © {new Date().getFullYear()} Kuma AI Prompt Manager
        </Container>
      </Box>
    </VStack>
  );
};

export default MainLayout;
