import { Box, Button, Flex, Heading, Image, HStack, Input, InputGroup, InputLeftElement } from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { SearchIcon } from '@chakra-ui/icons';
import { useState } from 'react';

const Navbar = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/prompts?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };
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

          <Flex gap={4} flex={1} maxW="2xl" mx={8}>
            <form onSubmit={handleSearch} style={{ width: '100%' }}>
              <InputGroup>
                <InputLeftElement pointerEvents="none">
                  <SearchIcon color="gray.400" />
                </InputLeftElement>
                <Input
                  type="text"
                  placeholder="Search prompts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  bg="white"
                  borderRadius="md"
                  _focus={{
                    borderColor: 'blue.400',
                    boxShadow: '0 0 0 1px var(--chakra-colors-blue-400)',
                  }}
                />
              </InputGroup>
            </form>
          </Flex>
          
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
