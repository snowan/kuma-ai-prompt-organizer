import { Box, Heading, useToast } from '@chakra-ui/react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { createCategory } from '../services/categoryService';
import CategoryForm from '../components/CategoryForm';
import type { CategoryCreate } from '../types';

const CategoryNew = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: CategoryCreate) => createCategory(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast({
        title: 'Category created',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate(`/categories/${data.id}`);
    },
    onError: (error: any) => {
      toast({
        title: 'Error creating category',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const handleSubmit = async (data: CategoryCreate) => {
    await createMutation.mutateAsync(data);
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Create New Category
      </Heading>
      <CategoryForm
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending}
        submitButtonText="Create Category"
      />
    </Box>
  );
};

export default CategoryNew;
