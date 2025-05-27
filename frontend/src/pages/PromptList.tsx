import { Box, Button, Card, CardBody, CardHeader, Flex, Heading, Spinner, Text, VStack } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router-dom';
import { getPrompts } from '../services/promptService';

const PromptList = () => {
  const { data: prompts, isLoading, error } = useQuery({
    queryKey: ['prompts'],
    queryFn: getPrompts,
  });

  if (isLoading) {
    return (
      <Flex justify="center" mt={8}>
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Box color="red.500" textAlign="center" mt={8}>
        Error loading prompts: {error.message}
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Flex justify="space-between" align="center">
        <Heading size="lg">All Prompts</Heading>
        <Button as={RouterLink} to="/prompts/new" colorScheme="blue">
          Create New Prompt
        </Button>
      </Flex>

      {prompts?.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text fontSize="lg" color="gray.500">
            No prompts found. Create your first prompt to get started!
          </Text>
        </Box>
      ) : (
        <VStack spacing={4} align="stretch">
          {prompts?.map((prompt) => (
            <Card key={prompt.id} as={RouterLink} to={`/prompts/${prompt.id}`} _hover={{ transform: 'translateY(-2px)', shadow: 'md' }} transition="all 0.2s">
              <CardHeader pb={0}>
                <Heading size="md">{prompt.title}</Heading>
                {prompt.category_id && (
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    Category: {prompt.category_id}
                  </Text>
                )}
              </CardHeader>
              <CardBody>
                <Text noOfLines={2} color="gray.600">
                  {prompt.content}
                </Text>
                {prompt.tags && prompt.tags.length > 0 && (
                  <Flex mt={3} gap={2} flexWrap="wrap">
                    {prompt.tags.map((tag) => (
                      <Box key={tag.id} px={2} py={1} bg="teal.100" borderRadius="full" fontSize="xs">
                        {tag.name}
                      </Box>
                    ))}
                  </Flex>
                )}
              </CardBody>
            </Card>
          ))}
        </VStack>
      )}
    </VStack>
  );
};

export default PromptList;
