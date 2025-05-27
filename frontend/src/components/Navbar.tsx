import { Box, Button, Flex, Heading, Image, HStack } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <Box as="header" bg="white" color="gray.800" boxShadow="sm" position="sticky" top={0} zIndex={10}>
      <Box maxW="container.xl" mx="auto" px={4}>
        <Flex h={16} alignItems="center" justifyContent="space-between">
          <HStack spacing={4}>
            <RouterLink to="/">
              <Image 
                src="/images/logo.png" 
                alt="Kuma AI Logo" 
                h="40px" 
                w="auto" 
                objectFit="contain"
              />
            </RouterLink>
            <RouterLink to="/" style={{ textDecoration: 'none' }}>
              <Heading
                size="lg"
                bgGradient="linear(to-r, blue.400, teal.500)"
                bgClip="text"
                fontSize="xl"
              >
                Kuma AI Prompt Manager
              </Heading>
            </RouterLink>
          </HStack>

          <Flex gap={4}>
            <Button as={RouterLink} to="/prompts" variant="ghost">
              Prompts
            </Button>
            <Button as={RouterLink} to="/categories" variant="ghost">
              Categories
            </Button>
          </Flex>
        </Flex>
      </Box>
    </Box>
  );
};

export default Navbar;
