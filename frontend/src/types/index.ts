export interface Category {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface CategoryCreate {
  name: string;
  description?: string;
}

export interface Prompt {
  id: number;
  title: string;
  content: string;
  category_id?: number;
  category?: Category;
  tags?: Tag[];
  likes: number;
  created_at: string;
  updated_at?: string;
}

export interface Tag {
  id: number;
  name: string;
  created_at: string;
}

export interface PromptCreate {
  title: string;
  content: string;
  category_id?: number;
  tag_names?: string[];
}

export interface PromptUpdate extends Partial<PromptCreate> {}

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}
