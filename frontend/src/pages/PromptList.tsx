import { Box, Card, Flex, Heading, Spinner, Text, VStack, HStack, useToast, Button } from '@chakra-ui/react';
import { AddIcon } from '@chakra-ui/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link as RouterLink, useSearchParams, useNavigate } from 'react-router-dom';
import { getPrompts, getCategories, likePrompt } from '../services/promptService';
import type { Prompt, Category } from '../types';
import { useMemo, useState } from 'react';

const PromptList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryId = searchParams.get('category_id') ? Number(searchParams.get('category_id')) : undefined;
  const tagName = searchParams.get('tag') || undefined;
  const likedParam = searchParams.get('liked') || '';
  
  // Initialize liked prompts from URL or create a new Set
  const [likedPrompts, setLikedPrompts] = useState<Set<number>>(
    () => new Set(likedParam ? likedParam.split(',').map(Number) : [])
  );
  
  // Update URL when likedPrompts changes
  const updateLikedInUrl = (newLiked: Set<number>) => {
    const params = new URLSearchParams(searchParams);
    const likedString = Array.from(newLiked).join(',');
    if (likedString) {
      params.set('liked', likedString);
    } else {
      params.delete('liked');
    }
    setSearchParams(params, { replace: true });
  };
  const queryClient = useQueryClient();
  const toast = useToast();
  const navigate = useNavigate();
  
  // Fetch prompts
  const { data: prompts = [], isLoading: isLoadingPrompts, error: promptsError } = useQuery<Prompt[]>({
    queryKey: ['prompts', { category_id: categoryId, tag: tagName }],
    queryFn: () => getPrompts({ category_id: categoryId, tag: tagName }),
  });

  // Fetch categories
  const { data: categories = [], isLoading: isLoadingCategories } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  // Like mutation with optimistic updates
  const likeMutation = useMutation({
    mutationFn: likePrompt,
    onMutate: async (promptId: number) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['prompts', { category_id: categoryId, tag: tagName }] });

      // Snapshot the previous value
      const previousPrompts = queryClient.getQueryData<Prompt[]>(['prompts', { category_id: categoryId, tag: tagName }]) || [];

      // Optimistically update to the new value
      queryClient.setQueryData<Prompt[]>(['prompts', { category_id: categoryId, tag: tagName }], (oldData = []) =>
        oldData.map(prompt => 
          prompt.id === promptId 
            ? { 
                ...prompt, 
                likes: (prompt.likes || 0) + 1
              } 
            : prompt
        )
      );

      // Return a context object with the snapshotted value
      return { previousPrompts };
    },
    onError: (_err, _promptId, context) => {
      // Rollback to the previous value on error
      if (context?.previousPrompts) {
        queryClient.setQueryData(['prompts', { category_id: categoryId, tag: tagName }], context.previousPrompts);
      }
      toast({
        title: 'Error',
        description: 'Failed to like the prompt',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    },
    onSettled: () => {
      // Refetch the prompts to ensure we have the latest data
      queryClient.invalidateQueries({ queryKey: ['prompts', { category_id: categoryId, tag: tagName }] });
    },
  });

  // Handle like button click
  const handleLikeClick = (e: React.MouseEvent<HTMLDivElement>, prompt: Prompt) => {
    // Prevent default and stop propagation to avoid navigation
    e.preventDefault();
    e.stopPropagation();
    
    // Toggle like state locally for immediate UI feedback
    const newLikedPrompts = new Set(likedPrompts);
    const isLiked = newLikedPrompts.has(prompt.id);
    
    if (isLiked) {
      newLikedPrompts.delete(prompt.id);
    } else {
      newLikedPrompts.add(prompt.id);
    }
    setLikedPrompts(newLikedPrompts);
    updateLikedInUrl(newLikedPrompts);
    
    // Call the mutation to update the server
    likeMutation.mutate(prompt.id);
  };

  // Filter prompts by category if categoryId is provided
  const filteredPrompts = useMemo(() => {
    if (!categoryId) return prompts;
    return prompts.filter(prompt => prompt.category_id === categoryId);
  }, [prompts, categoryId]);

  // Get category name by ID
  const getCategoryName = (id: number) => {
    return categories.find(cat => cat.id === id)?.name || 'Uncategorized';
  };

  if (isLoadingPrompts || isLoadingCategories) {
    return (
      <Flex justify="center" align="center" minH="200px">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (promptsError) {
    return (
      <Box p={4} color="red.500">
        Error loading prompts: {promptsError instanceof Error ? promptsError.message : 'Unknown error'}
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Text fontSize="sm" color="gray.500" mb={1}>
            {categoryId 
              ? `Category: ${getCategoryName(categoryId)}`
              : tagName 
                ? `Tag: ${tagName}`
                : ''}
          </Text>
          <Heading as="h1" size="lg" fontWeight="semibold">
            {categoryId 
              ? getCategoryName(categoryId)
              : tagName 
                ? tagName
                : 'All Prompts'}
          </Heading>
        </Box>
        <Button 
          as={RouterLink}
          to="/prompts/new"
          colorScheme="blue"
          size="sm"
          leftIcon={<AddIcon />}
        >
          Create New Prompt
        </Button>
      </Flex>

      {filteredPrompts.length === 0 ? (
        <Box p={6} textAlign="center" bg="gray.50" borderRadius="md">
          <Text fontSize="lg" color="gray.600">
            No prompts found{categoryId ? ' in this category' : tagName ? ' with this tag' : ''}. Create one to get started!
          </Text>
        </Box>
      ) : (
        <VStack spacing={4} align="stretch">
          {filteredPrompts.map((prompt) => (
            <Card 
              key={prompt.id} 
              as={RouterLink} 
              to={`/prompts/${prompt.id}`} 
              _hover={{ transform: 'translateY(-2px)', shadow: 'md' }} 
              transition="all 0.2s" 
              p={4}
              variant="outline"
            >
              <VStack align="stretch" spacing={3}>
                <Box>
                  <Flex justify="space-between" align="center" mb={2}>
                    <Text fontSize="sm" color="gray.500">
                      {new Date(prompt.created_at).toLocaleDateString()}
                    </Text>
                    {prompt.category_id && (
                      <Flex align="center" gap={1}>
                        <Text fontSize="sm" color="gray.500">Category:</Text>
                        <Text 
                          fontSize="sm" 
                          fontWeight="medium"
                          color="blue.600"
                          _dark={{ color: 'blue.300' }}
                        >
                          {getCategoryName(prompt.category_id)}
                        </Text>
                      </Flex>
                    )}
                  </Flex>
                  <Heading size="md" mb={2} fontWeight="semibold">{prompt.title}</Heading>
                  <Text noOfLines={2} color="gray.700" mb={3}>
                    {prompt.content}
                  </Text>
                </Box>
                
                <HStack spacing={2} wrap="wrap">
                  {prompt.tags?.map((tag) => (
                    <Box
                      key={tag.id}
                      as="button"
                      px={3}
                      py={1}
                      bg="teal.100"
                      borderRadius="full"
                      fontSize="xs"
                      color="teal.800"
                      _hover={{ bg: 'teal.200' }}
                      transition="background-color 0.2s"
                      onClick={(e: React.MouseEvent) => {
                        e.preventDefault();
                        e.stopPropagation();
                        // Navigate to prompt list with tag filter
                        navigate(`/prompts?tag=${encodeURIComponent(tag.name)}`);
                      }}
                    >
                      {tag.name}
                    </Box>
                  ))}
                </HStack>
                
                <HStack spacing={4} mt={2}>
                  <HStack spacing={1} align="center">
                    <Box
                      as="button"
                      display="flex"
                      alignItems="center"
                      onClick={(e: React.MouseEvent<HTMLDivElement>) => {
                        e.stopPropagation();
                        e.preventDefault();
                        handleLikeClick(e, prompt);
                      }}
                      _hover={{
                        color: 'red.500',
                        '& > *': {
                          transform: 'scale(1.1)'
                        }
                      }}
                      opacity={likeMutation.isPending ? 0.7 : 1}
                      cursor={likeMutation.isPending ? 'not-allowed' : 'pointer'}
                      transition="all 0.2s"
                      title="Like this prompt"
                      aria-label={`Like this prompt (${prompt.likes || 0} likes)`}
                    >
                      <Box as="span" mr={1} color={likedPrompts.has(prompt.id) ? 'red.500' : 'gray.400'}>
                        {likedPrompts.has(prompt.id) ? '❤️' : '🤍'}
                      </Box>
                      <Text 
                        color={likedPrompts.has(prompt.id) ? 'red.500' : 'gray.600'}
                        fontSize="sm"
                        fontWeight="medium"
                      >
                        {likedPrompts.has(prompt.id) ? (prompt.likes || 0) + 1 : prompt.likes || 0}
                      </Text>
                    </Box>
                  </HStack>
                </HStack>
              </VStack>
            </Card>
          ))}
        </VStack>
      )}
    </VStack>
  );
};

export default PromptList;
