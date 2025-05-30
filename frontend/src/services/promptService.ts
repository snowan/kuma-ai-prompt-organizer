import api from './api';
import type { Category, Prompt, Tag } from '../types';

export interface PromptCreate {
  title: string;
  content: string;
  category_id?: number;
  tag_names?: string[];
}

export interface PromptUpdate extends Partial<PromptCreate> {}

export interface DashboardStats {
  total_prompts: number;
  total_categories: number;
  total_tags: number;
  prompts_by_category: Record<string, number>;
}

interface GetPromptsParams {
  search?: string;
  category_id?: number;
  tag?: string;
}

// Prompts
export const getPrompts = async (params?: GetPromptsParams): Promise<Prompt[]> => {
  // Filter out undefined values from params
  const filteredParams = params 
    ? Object.fromEntries(
        Object.entries(params).filter(([_, value]) => value !== undefined)
      )
    : undefined;
    
  const response = await api.get<Prompt[]>('/prompts', { 
    params: filteredParams 
  });
  return response.data;
};

export const getPrompt = async (id: number): Promise<Prompt> => {
  const response = await api.get<Prompt>(`/prompts/${id}`);
  return response.data;
};

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get<DashboardStats>('/prompts/stats');
  return response.data;
};

export const createPrompt = async (prompt: PromptCreate): Promise<Prompt> => {
  const response = await api.post<Prompt>('/prompts', prompt);
  return response.data;
};

export const updatePrompt = async (id: number, prompt: PromptUpdate): Promise<Prompt> => {
  const response = await api.put<Prompt>(`/prompts/${id}`, prompt);
  return response.data;
};

export const deletePrompt = async (id: number): Promise<void> => {
  await api.delete(`/prompts/${id}`);
};

export const likePrompt = async (id: number): Promise<Prompt> => {
  try {
    console.log(`Sending like request for prompt ${id} to /prompts/${id}/like`);
    const response = await api.post<Prompt>(`/prompts/${id}/like`);
    console.log('Like response:', response);
    return response.data;
  } catch (error: any) {
    console.error('Error in likePrompt:', error);
    if (error.response?.status === 401) {
      const error = new Error('Authentication required to like a prompt');
      error.name = 'AuthError';
      throw error;
    }
    throw error;
  }
};

// Categories
export const getCategories = async (): Promise<Category[]> => {
  const response = await api.get<Category[]>('/categories');
  return response.data;
};

export const createCategory = async (category: Omit<Category, 'id' | 'created_at'>): Promise<Category> => {
  const response = await api.post<Category>('/categories', category);
  return response.data;
};

export const updateCategory = async (id: number, category: Partial<Category>): Promise<Category> => {
  const response = await api.put<Category>(`/categories/${id}`, category);
  return response.data;
};

export const deleteCategory = async (id: number): Promise<void> => {
  await api.delete(`/categories/${id}`);
};

// Tags
export const getTags = async (): Promise<Tag[]> => {
  const response = await api.get<Tag[]>('/tags');
  return response.data;
};

export const createTag = async (tag: Omit<Tag, 'id' | 'created_at'>): Promise<Tag> => {
  const response = await api.post<Tag>('/tags', tag);
  return response.data;
};
