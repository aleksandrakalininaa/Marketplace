import api from './client';

export interface CategoryNode {
  id: string;
  name: string;
  slug: string;
  image_url: string | null;
  children: CategoryNode[] | null;
}

export interface CategoryShort {
  id: string;
  name: string;
  slug: string;
}

export interface ProductShort {
  id: string;
  name: string;
  price: number;
  quantity: number;
  image_urls: string[];
  category: CategoryShort | null;
}

export interface ProductDetail {
  id: string;
  name: string;
  description: string;
  price: number;
  quantity: number;
  image_urls: string[];
  attributes: Record<string, string>;
  category: CategoryShort | null;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  items: ProductShort[];
  total: number;
  page: number;
  limit: number;
}

export interface ProductFilters {
  search: string;
  category_id?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  sort?: string;
  page?: number;
  limit?: number;
}

export const catalogApi = {
  getCategories(): Promise<{ data: CategoryNode[] }> {
    return api.get('/api/v1/categories');
  },

  getProduct(id: string): Promise<{ data: ProductDetail }> {
    return api.get(`/api/v1/products/${id}`);
  },

  getProducts(filters: ProductFilters): Promise<{ data: ProductListResponse }> {
    const params: Record<string, string | number | boolean> = {
      search: filters.search,
    };
    if (filters.category_id) params.category_id = filters.category_id;
    if (filters.min_price !== undefined) params.min_price = filters.min_price;
    if (filters.max_price !== undefined) params.max_price = filters.max_price;
    if (filters.in_stock !== undefined) params.in_stock = filters.in_stock;
    if (filters.sort) params.sort = filters.sort;
    if (filters.page) params.page = filters.page;
    if (filters.limit) params.limit = filters.limit;
    return api.get('/api/v1/products', { params });
  },
};