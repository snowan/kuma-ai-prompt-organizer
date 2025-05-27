import { Box, Button, FormControl, FormLabel, Select, Textarea, VStack, FormErrorMessage, Input, HStack, Tag, TagLabel, TagCloseButton, Wrap, useToast } from '@chakra-ui/react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import type { SubmitHandler, FieldValues } from 'react-hook-form';
import { useNavigate, useParams, useOutletContext } from 'react-router-dom';
import { createPrompt, updatePrompt, getCategories } from '../services/promptService';
import type { Prompt, Category } from '../types';
import { useState, useCallback, useEffect } from 'react';

interface FormData extends FieldValues {
  title: string;
  content: string;
  category_id?: number;
  tag_names: string[];
  newTag: string;
}

interface PromptFormProps {
  prompt?: Prompt;
  isEditing?: boolean;
}

const PromptForm = ({ isEditing = false }: PromptFormProps) => {
  const { prompt: promptData } = useOutletContext<{ prompt: Prompt }>() || {};
  const { id } = useParams<{ id: string }>();
  const [initialPrompt, setInitialPrompt] = useState<Partial<Prompt>>({});

  useEffect(() => {
    if (isEditing && promptData) {
      setInitialPrompt({
        title: promptData.title,
        content: promptData.content,
        category_id: promptData.category_id,
        tags: promptData.tags || []
      });
    }
  }, [isEditing, promptData]);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const toast = useToast();
  const showToast = useCallback((title: string, status: 'success' | 'error' | 'warning' | 'info') => {
    toast({
      title,
      status,
      duration: 3000,
      isClosable: true,
    });
  }, [toast]);
  const [tagInput, setTagInput] = useState('');
  
  // Fetch categories
  const { data: categories = [] } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: getCategories as () => Promise<Category[]>,
  });

  const { 
    register, 
    handleSubmit, 
    setValue,
    watch,
    reset,
    formState: { errors } 
  } = useForm<FormData>();

  // Set form values when initialPrompt changes
  useEffect(() => {
    if (isEditing && initialPrompt) {
      reset({
        title: initialPrompt.title || '',
        content: initialPrompt.content || '',
        category_id: initialPrompt.category_id,
        tag_names: initialPrompt.tags?.map(tag => tag.name) || [],
        newTag: '',
      });
    } else {
      reset({
        title: '',
        content: '',
        category_id: undefined,
        tag_names: [],
        newTag: '',
      });
    }
  }, [initialPrompt, isEditing, reset]);

  const tagNames = watch('tag_names') || [];
  const currentCategoryId = watch('category_id');

  const handleAddTag = useCallback(() => {
    if (tagInput.trim() && !tagNames.includes(tagInput.trim())) {
      setValue('tag_names', [...tagNames, tagInput.trim()]);
      setTagInput('');
    }
  }, [tagInput, tagNames, setValue]);

  const handleRemoveTag = useCallback((tagToRemove: string) => {
    setValue('tag_names', tagNames.filter(tag => tag !== tagToRemove));
  }, [tagNames, setValue]);

  const onSubmit: SubmitHandler<FormData> = async (data) => {
    try {
      const promptData = {
        title: data.title,
        content: data.content,
        category_id: data.category_id || undefined,
        tag_names: data.tag_names || [],
      };

      if (isEditing && id) {
        await updatePrompt(Number(id), promptData);
        showToast('Prompt updated successfully', 'success');
      } else {
        await createPrompt(promptData);
        showToast('Prompt created successfully', 'success');
      }

      queryClient.invalidateQueries({ queryKey: ['prompts'] });
      navigate('/prompts');
    } catch (error) {
      showToast('Failed to save prompt', 'error');
    }
  };

  return (
    <Box maxW="container.md" mx="auto" p={4}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <VStack spacing={6} align="stretch">
          <FormControl isInvalid={!!errors.title}>
            <FormLabel>Title</FormLabel>
            <Input
              {...register('title', { required: 'Title is required' })}
              placeholder="Enter prompt title"
              size="lg"
            />
            {errors.title && (
              <FormErrorMessage>{errors.title.message as string}</FormErrorMessage>
            )}
          </FormControl>

          <FormControl isInvalid={!!errors.content}>
            <FormLabel>Content</FormLabel>
            <Textarea
              {...register('content', { required: 'Content is required' })}
              placeholder="Enter prompt content"
              rows={10}
              fontFamily="mono"
              whiteSpace="pre-wrap"
            />
            {errors.content && (
              <FormErrorMessage>{errors.content.message as string}</FormErrorMessage>
            )}
          </FormControl>

          <FormControl>
            <FormLabel>Category (optional)</FormLabel>
            <Select
              placeholder="Select a category"
              {...register('category_id')}
              value={currentCategoryId}
              onChange={(e) => setValue('category_id', e.target.value ? Number(e.target.value) : undefined)}
            >
              {categories.map((category: Category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </Select>
          </FormControl>

          <FormControl>
            <FormLabel>Tags (press Enter to add)</FormLabel>
            <HStack spacing={2} mb={2}>
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTag();
                  }
                }}
                placeholder="Add a tag and press Enter"
              />
              <Button onClick={handleAddTag} type="button">
                Add
              </Button>
            </HStack>
            <Wrap spacing={2}>
              {tagNames.map((tag: string) => (
                <Tag key={tag} colorScheme="blue" borderRadius="full">
                  <TagLabel>{tag}</TagLabel>
                  <TagCloseButton onClick={() => handleRemoveTag(tag)} />
                </Tag>
              ))}
            </Wrap>
          </FormControl>

          <HStack spacing={4} justify="flex-end" pt={4}>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate(-1)}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              colorScheme="blue"
            >
              {isEditing ? 'Update' : 'Create'} Prompt
            </Button>
          </HStack>
        </VStack>
      </form>
    </Box>
  );
};

export default PromptForm;
