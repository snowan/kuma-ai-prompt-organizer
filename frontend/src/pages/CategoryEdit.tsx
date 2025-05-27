import { Box, Heading, useToast } from '@chakra-ui/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { getCategory, updateCategory } from '../services/categoryService';
import CategoryForm from '../components/CategoryForm';
import type { CategoryCreate } from '../types';

const CategoryEdit = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();

  // Fetch category data
  const { data: category, isLoading, error } = useQuery({
    queryKey: ['category', id],
    queryFn: () => getCategory(Number(id)),
    enabled: !!id,
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: CategoryCreate) => updateCategory(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      queryClient.invalidateQueries({ queryKey: ['category', id] });
      toast({
        title: 'Category updated',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate(`/categories/${id}`);
    },
    onError: (error: any) => {
      toast({
        title: 'Error updating category',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  if (isLoading) {
    return <Box>Loading...</Box>;
  }

  if (error) {
    return <Box>Error loading category: {error.message}</Box>;
  }

  if (!category) {
    return <Box>Category not found</Box>;
  }

  const handleSubmit = async (data: CategoryCreate) => {
    await updateMutation.mutateAsync(data);
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>
        Edit Category
      </Heading>
      <CategoryForm
        initialData={category}
        onSubmit={handleSubmit}
        isSubmitting={updateMutation.isPending}
        submitButtonText="Update Category"
      />
    </Box>
  );
};

export default CategoryEdit;
