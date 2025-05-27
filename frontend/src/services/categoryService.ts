import type { Category, CategoryCreate } from '@/types';
import api from './api';

export const getCategories = async (): Promise<Category[]> => {
  const response = await api.get('/api/categories/');
  return response.data;
};

export const getCategory = async (id: number): Promise<Category> => {
  const response = await api.get(`/api/categories/${id}`);
  return response.data;
};

export const createCategory = async (category: CategoryCreate): Promise<Category> => {
  const response = await api.post('/api/categories/', category);
  return response.data;
};

export const updateCategory = async (id: number, category: Partial<CategoryCreate>): Promise<Category> => {
  const response = await api.put(`/api/categories/${id}`, category);
  return response.data;
};

export const deleteCategory = async (id: number): Promise<void> => {
  await api.delete(`/api/categories/${id}`);
};
