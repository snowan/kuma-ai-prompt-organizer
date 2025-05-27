import apiClient from './api';

export interface Prompt {
  id?: number;
  title: string;
  content: string;
  category_id?: number | null;
  created_at?: string;
  updated_at?: string | null;
  tags?: Tag[];
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Tag {
  id: number;
  name: string;
  created_at: string;
}

// Prompts
export const getPrompts = async (): Promise<Prompt[]> => {
  const response = await apiClient.get<Prompt[]>('/prompts');
  return response.data;
};

export const getPrompt = async (id: number): Promise<Prompt> => {
  const response = await apiClient.get<Prompt>(`/prompts/${id}`);
  return response.data;
};

export const createPrompt = async (prompt: Omit<Prompt, 'id'>): Promise<Prompt> => {
  const response = await apiClient.post<Prompt>('/prompts', prompt);
  return response.data;
};

export const updatePrompt = async (id: number, prompt: Partial<Prompt>): Promise<Prompt> => {
  const response = await apiClient.put<Prompt>(`/prompts/${id}`, prompt);
  return response.data;
};

export const deletePrompt = async (id: number): Promise<void> => {
  await apiClient.delete(`/prompts/${id}`);
};

// Categories
export const getCategories = async (): Promise<Category[]> => {
  const response = await apiClient.get<Category[]>('/categories');
  return response.data;
};

export const createCategory = async (category: Omit<Category, 'id' | 'created_at'>): Promise<Category> => {
  const response = await apiClient.post<Category>('/categories', category);
  return response.data;
};

// Tags
export const getTags = async (): Promise<Tag[]> => {
  const response = await apiClient.get<Tag[]>('/tags');
  return response.data;
};

export const createTag = async (tag: Omit<Tag, 'id' | 'created_at'>): Promise<Tag> => {
  const response = await apiClient.post<Tag>('/tags', tag);
  return response.data;
};
