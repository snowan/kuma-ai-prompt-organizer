import { Box, Button, Card, CardBody, CardHeader, Flex, Heading, Spinner, Text, VStack, useDisclosure, useToast } from '@chakra-ui/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link as RouterLink } from 'react-router-dom';
import { getCategories, deleteCategory } from '../services/categoryService';
import { Category } from '../types';
import { useState } from 'react';
import ConfirmationDialog from '../components/ConfirmationDialog';
import { FiEdit, FiTrash2 } from 'react-icons/fi';

const CategoryList = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [categoryToDelete, setCategoryToDelete] = useState<number | null>(null);
  const toast = useToast();
  const queryClient = useQueryClient();

  const { data: categories, isLoading, error } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteCategory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast({
        title: 'Category deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
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

  const handleDeleteClick = (id: number) => {
    setCategoryToDelete(id);
    onOpen();
  };

  const confirmDelete = () => {
    if (categoryToDelete) {
      deleteMutation.mutate(categoryToDelete);
      onClose();
    }
  };

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
        Error loading categories: {error.message}
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Flex justify="space-between" align="center">
        <Heading size="lg">Categories</Heading>
        <Button as={RouterLink} to="/categories/new" colorScheme="blue">
          Create New Category
        </Button>
      </Flex>

      {categories?.length === 0 ? (
        <Box textAlign="center" py={10}>
          <Text fontSize="lg" color="gray.500">
            No categories found. Create your first category to get started!
          </Text>
        </Box>
      ) : (
        <VStack spacing={4} align="stretch">
          {categories?.map((category: Category) => (
            <Card key={category.id}>
              <CardHeader pb={0}>
                <Flex justify="space-between" align="center">
                  <Heading size="md">{category.name}</Heading>
                  <Flex gap={2}>
                    <Button
                      as={RouterLink}
                      to={`/categories/${category.id}/edit`}
                      size="sm"
                      leftIcon={<FiEdit />}
                      variant="outline"
                    >
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      leftIcon={<FiTrash2 />}
                      colorScheme="red"
                      variant="outline"
                      onClick={() => handleDeleteClick(category.id)}
                      isLoading={deleteMutation.isPending && categoryToDelete === category.id}
                    >
                      Delete
                    </Button>
                  </Flex>
                </Flex>
              </CardHeader>
              <CardBody>
                {category.description && (
                  <Text color="gray.600">{category.description}</Text>
                )}
                <Text fontSize="sm" color="gray.500" mt={2}>
                  Created: {new Date(category.created_at).toLocaleDateString()}
                </Text>
              </CardBody>
            </Card>
          ))}
        </VStack>
      )}

      <ConfirmationDialog
        isOpen={isOpen}
        onClose={onClose}
        onConfirm={confirmDelete}
        title="Delete Category"
        message="Are you sure you want to delete this category? This action cannot be undone."
        confirmButtonText="Delete"
        cancelButtonText="Cancel"
        confirmButtonColorScheme="red"
      />
    </VStack>
  );
};

export default CategoryList;
