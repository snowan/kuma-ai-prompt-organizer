import { Box, Button, Card, CardBody, CardHeader, Flex, Grid, Heading, Spinner, Text, VStack, useToast } from '@chakra-ui/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useParams, Link as RouterLink, useNavigate } from 'react-router-dom';
import { getCategory, deleteCategory } from '../services/categoryService';
import { getPrompts } from '../services/promptService';
import { FiEdit, FiTrash2, FiArrowLeft } from 'react-icons/fi';
import ConfirmationDialog from '../components/ConfirmationDialog';
import { useState } from 'react';

const CategoryDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Fetch category details
  const { data: category, isLoading: isCategoryLoading, error: categoryError } = useQuery({
    queryKey: ['category', id],
    queryFn: () => getCategory(Number(id)),
    enabled: !!id,
  });

  // Fetch prompts for this category
  const { data: prompts, isLoading: isPromptsLoading } = useQuery({
    queryKey: ['prompts', { categoryId: id }],
    queryFn: () => getPrompts(),
    enabled: !!id,
    select: (prompts) => {
      if (!id) return [];
      return prompts.filter(prompt => prompt.category_id === Number(id));
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => deleteCategory(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast({
        title: 'Category deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate('/categories');
    },
    onError: (error: any) => {
      toast({
        title: 'Error deleting category',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  if (isCategoryLoading) {
    return (
      <Flex justify="center" mt={8}>
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (categoryError) {
    return (
      <Box color="red.500" textAlign="center" mt={8}>
        Error loading category: {categoryError.message}
      </Box>
    );
  }

  if (!category) {
    return (
      <Box textAlign="center" mt={8}>
        <Text>Category not found</Text>
        <Button as={RouterLink} to="/categories" mt={4}>
          Back to Categories
        </Button>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Flex justify="space-between" align="center">
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          as={RouterLink}
          to="/categories"
          mb={4}
        >
          Back to Categories
        </Button>
        <Flex gap={2}>
          <Button
            as={RouterLink}
            to={`/categories/${id}/edit`}
            leftIcon={<FiEdit />}
            colorScheme="blue"
          >
            Edit
          </Button>
          <Button
            leftIcon={<FiTrash2 />}
            colorScheme="red"
            variant="outline"
            onClick={() => setIsDeleteDialogOpen(true)}
            isLoading={deleteMutation.isPending}
          >
            Delete
          </Button>
        </Flex>
      </Flex>

      <Card>
        <CardHeader>
          <Heading size="lg">{category.name}</Heading>
          {category.description && (
            <Text mt={2} color="gray.600">
              {category.description}
            </Text>
          )}
          <Text fontSize="sm" color="gray.500" mt={2}>
            Created: {new Date(category.created_at).toLocaleDateString()}
          </Text>
        </CardHeader>
      </Card>

      <Box mt={8}>
        <Heading size="md" mb={4}>
          Prompts in this category ({prompts?.length || 0})
        </Heading>
        
        {isPromptsLoading ? (
          <Flex justify="center" mt={8}>
            <Spinner size="xl" />
          </Flex>
        ) : prompts?.length === 0 ? (
          <Box textAlign="center" py={10} borderWidth={1} borderRadius="md" p={4}>
            <Text color="gray.500">No prompts found in this category.</Text>
            <Button as={RouterLink} to="/prompts/new" colorScheme="blue" mt={4}>
              Create New Prompt
            </Button>
          </Box>
        ) : (
          <Grid templateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={4}>
            {prompts?.map((prompt) => (
              <Card key={prompt.id} as={RouterLink} to={`/prompts/${prompt.id}`} _hover={{ shadow: 'md' }}>
                <CardHeader>
                  <Heading size="md">{prompt.title}</Heading>
                </CardHeader>
                <CardBody>
                  <Text noOfLines={2} color="gray.600">
                    {prompt.content}
                  </Text>
                  {prompt.tags && prompt.tags.length > 0 && (
                    <Flex mt={2} gap={1} flexWrap="wrap">
                      {prompt.tags.map((tag) => (
                        <Box key={tag.id} px={2} py={0.5} bg="teal.100" borderRadius="full" fontSize="xs">
                          {tag.name}
                        </Box>
                      ))}
                    </Flex>
                  )}
                </CardBody>
              </Card>
            ))}
          </Grid>
        )}
      </Box>

      <ConfirmationDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete Category"
        message="Are you sure you want to delete this category? This action cannot be undone."
        confirmButtonText="Delete"
        cancelButtonText="Cancel"
        confirmButtonColorScheme="red"
        isLoading={deleteMutation.isPending}
      />
    </VStack>
  );
};

export default CategoryDetail;
