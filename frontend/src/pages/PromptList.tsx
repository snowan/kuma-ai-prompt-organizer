import { Box, Button, Card, CardBody, CardHeader, Flex, Heading, Spinner, Text, VStack, Badge, HStack } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import { getPrompts, getCategories } from '../services/promptService';
import type { Prompt, Category } from '../types';
import { useMemo } from 'react';

const PromptList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryId = searchParams.get('category_id') ? Number(searchParams.get('category_id')) : undefined;
  const tagName = searchParams.get('tag') || undefined;
  const { data: prompts, isLoading: isLoadingPrompts, error: promptsError } = useQuery<Prompt[]>({
    queryKey: ['prompts', { category_id: categoryId, tag: tagName }],
    queryFn: () => getPrompts({ category_id: categoryId, tag: tagName }),
  });

  const { data: categories, isLoading: isLoadingCategories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => getCategories(),
  });

  const categoryMap = useMemo(() => {
    return categories?.reduce((acc: Record<number, string>, category: Category) => {
      acc[category.id] = category.name;
      return acc;
    }, {}) || {};
  }, [categories]);

  if (isLoadingPrompts || isLoadingCategories) {
    return (
      <Flex justify="center" mt={8}>
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (promptsError) {
    return (
      <Box color="red.500" textAlign="center" mt={8}>
        Error loading prompts: {promptsError.message}
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Flex justify="space-between" align="center" mb={4}>
        <Box>
          <Heading size="lg" display="inline" mr={4}>All Prompts</Heading>
          {categoryId && categoryMap[categoryId] && (
            <Badge colorScheme="blue" fontSize="md" px={2} py={1} borderRadius="md" mr={2}>
              Category: {categoryMap[categoryId]}
              <Button 
                size="xs" 
                variant="ghost" 
                ml={2} 
                onClick={() => {
                  searchParams.delete('category_id');
                  setSearchParams(searchParams);
                }}
              >
                ✕
              </Button>
            </Badge>
          )}
          {tagName && (
            <Badge colorScheme="teal" fontSize="md" px={2} py={1} borderRadius="md" display="inline-flex" alignItems="center">
              Tag: {tagName}
              <Button 
                size="xs" 
                variant="ghost" 
                ml={2} 
                onClick={() => {
                  searchParams.delete('tag');
                  setSearchParams(searchParams);
                }}
              >
                ✕
              </Button>
            </Badge>
          )}
        </Box>
        <Button as={RouterLink} to="/prompts/new" colorScheme="blue">
          Create New Prompt
        </Button>
      </Flex>

      {!prompts || prompts.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text fontSize="lg" color="gray.500">
            No prompts found. Create your first prompt to get started!
          </Text>
        </Box>
      ) : (
        <VStack spacing={4} align="stretch">
          {prompts.map((prompt: Prompt) => (
            <Card key={prompt.id} as={RouterLink} to={`/prompts/${prompt.id}`} _hover={{ transform: 'translateY(-2px)', shadow: 'md' }} transition="all 0.2s">
              <CardHeader pb={0}>
                <Heading size="md">{prompt.title}</Heading>
                {prompt.category_id && categoryMap[prompt.category_id] && (
                  <HStack spacing={2} mt={1}>
                    <Text fontSize="sm" color="gray.500">Category:</Text>
                    <Text 
                      as="button"
                      fontSize="sm" 
                      color="blue.500"
                      _hover={{ textDecoration: 'underline' }}
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        searchParams.set('category_id', prompt.category_id!.toString());
                        setSearchParams(searchParams);
                      }}
                    >
                      {categoryMap[prompt.category_id]}
                    </Text>
                  </HStack>
                )}
              </CardHeader>
              <CardBody>
                <Text noOfLines={2} color="gray.600">
                  {prompt.content}
                </Text>
                {prompt.tags && prompt.tags.length > 0 && (
                  <Flex mt={3} gap={2} flexWrap="wrap">
                    {prompt.tags.map((tag) => (
                      <Box 
                        key={tag.id} 
                        as="button"
                        px={2} 
                        py={1} 
                        bg="teal.100" 
                        borderRadius="full" 
                        fontSize="xs"
                        _hover={{ bg: 'teal.200' }}
                        transition="background-color 0.2s"
                        onClick={(e: React.MouseEvent) => {
                          e.preventDefault();
                          e.stopPropagation();
                          searchParams.set('tag', tag.name);
                          // Remove category filter when filtering by tag
                          searchParams.delete('category_id');
                          setSearchParams(searchParams);
                        }}
                      >
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
