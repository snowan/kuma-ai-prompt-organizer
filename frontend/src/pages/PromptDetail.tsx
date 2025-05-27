import { Box, Button, Card, CardBody, CardHeader, Flex, Heading, IconButton, Spinner, Text, VStack, useToast, HStack } from '@chakra-ui/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Outlet, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { DeleteIcon, EditIcon } from '@chakra-ui/icons';
import { deletePrompt, getPrompt, getCategories } from '../services/promptService';
import type { Prompt, Category } from '../types';
import { useMemo } from 'react';

const PromptDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();

  const { data: prompt, isLoading: isLoadingPrompt, error: promptError } = useQuery<Prompt>({
    queryKey: ['prompt', id],
    queryFn: () => getPrompt(Number(id)),
    enabled: !!id,
  });

  const { data: categories, isLoading: isLoadingCategories } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: () => getCategories(),
  });

  const categoryName = useMemo(() => {
    if (!categories || !prompt?.category_id) return null;
    const category = categories.find(cat => cat.id === prompt.category_id);
    return category ? category.name : null;
  }, [categories, prompt?.category_id]);

  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: () => deletePrompt(Number(id)),
    onSuccess: () => {
      // Invalidate the prompts query to refetch the updated list
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
      
      toast({
        title: 'Prompt deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate('/prompts');
    },
    onError: (error) => {
      toast({
        title: 'Error deleting prompt',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  if (isLoadingPrompt || isLoadingCategories) {
    return (
      <Flex justify="center" mt={8}>
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (promptError || !prompt) {
    return (
      <Box color="red.500" textAlign="center" mt={8}>
        {promptError ? promptError.message : 'Prompt not found'}
      </Box>
    );
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      deleteMutation.mutate();
    }
  };

  // If there's an outlet (like the edit form), render it
  if (window.location.pathname.endsWith('/edit')) {
    return <Outlet context={{ prompt }} />;
  }

  return (
    <VStack spacing={6} align="stretch">
      <Flex justify="space-between" align="center">
        <Heading>{prompt.title}</Heading>
        <Flex gap={2}>
          <IconButton
            aria-label="Edit prompt"
            icon={<EditIcon />}
            onClick={() => navigate(`/prompts/${id}/edit`)}
          />
          <IconButton
            aria-label="Delete prompt"
            icon={<DeleteIcon />}
            colorScheme="red"
            variant="outline"
            onClick={handleDelete}
            isLoading={deleteMutation.isPending}
          />
        </Flex>
      </Flex>

      <Card>
        <CardHeader pb={0}>
          {categoryName && (
            <Text color="gray.500" mb={2}>
              Category: {categoryName}
            </Text>
          )}
        </CardHeader>
        <CardBody>
          <Box
            whiteSpace="pre-wrap"
            p={4}
            bg="gray.50"
            borderRadius="md"
            fontFamily="mono"
            fontSize="sm"
          >
            {prompt.content}
          </Box>

          {prompt.tags && prompt.tags.length > 0 && (
            <Box mt={4}>
              <Text fontSize="sm" color="gray.500" mb={2}>Tags:</Text>
              <Flex gap={2} flexWrap="wrap">
                {prompt.tags.map((tag) => (
                  <Box
                    key={tag.id}
                    as="button"
                    px={3}
                    py={1}
                    bg="teal.100"
                    borderRadius="full"
                    fontSize="sm"
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
              </Flex>
            </Box>
          )}
        </CardBody>
      </Card>

      <Box>
        <Button as="a" href="/prompts" variant="outline" mr={2}>
          Back to Prompts
        </Button>
        <Button
          colorScheme="blue"
          onClick={() => navigate(`/prompts/${id}/edit`)}
        >
          Edit Prompt
        </Button>
      </Box>
    </VStack>
  );
};

export default PromptDetail;
