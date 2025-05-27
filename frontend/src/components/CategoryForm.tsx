import { Box, Button, FormControl, FormErrorMessage, FormLabel, Input, Textarea, VStack } from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { Category, CategoryCreate } from '../types';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@chakra-ui/react';

interface CategoryFormProps {
  initialData?: Category;
  onSubmit: (data: CategoryCreate) => Promise<void>;
  isSubmitting: boolean;
  submitButtonText?: string;
}

const CategoryForm = ({
  initialData,
  onSubmit,
  isSubmitting,
  submitButtonText = 'Submit',
}: CategoryFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CategoryCreate>({
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
    },
  });

  const navigate = useNavigate();
  const toast = useToast();

  const handleFormSubmit = async (data: CategoryCreate) => {
    try {
      await onSubmit(data);
      toast({
        title: initialData ? 'Category updated' : 'Category created',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate('/categories');
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit(handleFormSubmit)}>
      <VStack spacing={4} align="stretch">
        <FormControl isInvalid={!!errors.name} isRequired>
          <FormLabel htmlFor="name">Name</FormLabel>
          <Input
            id="name"
            placeholder="Enter category name"
            {...register('name', {
              required: 'Name is required',
              minLength: { value: 2, message: 'Name must be at least 2 characters' },
              maxLength: { value: 100, message: 'Name cannot exceed 100 characters' },
            })}
          />
          <FormErrorMessage>{errors.name?.message}</FormErrorMessage>
        </FormControl>

        <FormControl isInvalid={!!errors.description}>
          <FormLabel htmlFor="description">Description</FormLabel>
          <Textarea
            id="description"
            placeholder="Enter category description (optional)"
            rows={4}
            {...register('description', {
              maxLength: { value: 500, message: 'Description cannot exceed 500 characters' },
            })}
          />
          <FormErrorMessage>{errors.description?.message}</FormErrorMessage>
        </FormControl>

        <Box pt={4}>
          <Button
            type="submit"
            colorScheme="blue"
            isLoading={isSubmitting}
            loadingText="Submitting..."
          >
            {submitButtonText}
          </Button>
          <Button
            variant="outline"
            ml={3}
            onClick={() => navigate('/categories')}
            isDisabled={isSubmitting}
          >
            Cancel
          </Button>
        </Box>
      </VStack>
    </Box>
  );
};

export default CategoryForm;
