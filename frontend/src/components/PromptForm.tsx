import { Box, Button, FormControl, FormLabel, Select, Textarea, VStack } from '@chakra-ui/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import type { SubmitHandler } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { createPrompt, updatePrompt, getCategories } from '../services/promptService';
import type { Prompt, Category, Tag } from '../services/promptService';

interface FormData {
  title: string;
  content: string;
  category_id?: number;
  tags?: number[];
}

interface PromptFormProps {
  prompt?: Prompt;
  isEditing?: boolean;
}

const PromptForm = ({ prompt, isEditing = false }: PromptFormProps) => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  
  const { data: categories = [] } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      title: prompt?.title || '',
      content: prompt?.content || '',
      category_id: prompt?.category_id || undefined,
      tags: prompt?.tags?.map((tag: Tag) => tag.id) || [],
    },
  });

  const mutation = useMutation<Prompt, Error, FormData>({
    mutationFn: async (data: FormData) => {
      return isEditing && prompt?.id 
        ? updatePrompt(prompt.id, data as Omit<Prompt, 'id'>) 
        : createPrompt(data as Omit<Prompt, 'id'>);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
      navigate('/prompts');
    },
  });

  const onSubmit: SubmitHandler<FormData> = (data) => {
    mutation.mutate(data);
  };

  return (
    <Box as="form" onSubmit={handleSubmit(onSubmit)}>
      <VStack spacing={6}>
        <FormControl isInvalid={!!errors.title} isRequired>
          <FormLabel>Title</FormLabel>
          <input
            {...register('title', { required: 'Title is required' })}
            className="chakra-input"
            placeholder="Enter prompt title"
          />
          {errors.title && <Box color="red.500" mt={1}>{errors.title.message}</Box>}
        </FormControl>

        <FormControl isInvalid={!!errors.content} isRequired>
          <FormLabel>Content</FormLabel>
          <Textarea
            {...register('content', { required: 'Content is required' })}
            placeholder="Enter prompt content"
            rows={8}
          />
          {errors.content && <Box color="red.500" mt={1}>{errors.content.message}</Box>}
        </FormControl>

        <FormControl>
          <FormLabel>Category</FormLabel>
          <Select
            {...register('category_id')}
            placeholder="Select category (optional)"
          >
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </Select>
        </FormControl>

        <FormControl>
          <FormLabel>Tags (coming soon)</FormLabel>
          <Select isDisabled placeholder="Tags functionality coming soon" />
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={mutation.isPending}
          loadingText={isEditing ? 'Updating...' : 'Creating...'}
        >
          {isEditing ? 'Update Prompt' : 'Create Prompt'}
        </Button>
      </VStack>
    </Box>
  );
};

export default PromptForm;
