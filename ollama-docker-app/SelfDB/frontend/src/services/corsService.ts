import api from './api';

export interface CorsOrigin {
  id: string;
  origin: string;
  description?: string;
  is_active: boolean;
  extra_metadata?: Record<string, any>;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

export interface CorsOriginCreate {
  origin: string;
  description?: string;
  extra_metadata?: Record<string, any>;
}

export interface CorsOriginUpdate {
  origin?: string;
  description?: string;
  is_active?: boolean;
  extra_metadata?: Record<string, any>;
}

export interface CorsOriginsList {
  origins: CorsOrigin[];
  total_count: number;
}

export interface CorsOriginValidation {
  origin: string;
  is_valid: boolean;
  error_message?: string;
}

export const corsService = {
  // List all CORS origins
  async list(activeOnly: boolean = true): Promise<CorsOriginsList> {
    const response = await api.get<CorsOriginsList>('/cors/origins/', {
      params: { active_only: activeOnly }
    });
    return response.data;
  },

  // Create a new CORS origin
  async create(data: CorsOriginCreate): Promise<CorsOrigin> {
    const response = await api.post<CorsOrigin>('/cors/origins/', data);
    return response.data;
  },

  // Get a specific CORS origin by ID
  async getById(id: string): Promise<CorsOrigin> {
    const response = await api.get<CorsOrigin>(`/cors/origins/${id}`);
    return response.data;
  },

  // Update a CORS origin
  async update(id: string, data: CorsOriginUpdate): Promise<CorsOrigin> {
    const response = await api.put<CorsOrigin>(`/cors/origins/${id}`, data);
    return response.data;
  },

  // Delete a CORS origin (soft delete by default)
  async delete(id: string, hardDelete: boolean = false): Promise<void> {
    await api.delete(`/cors/origins/${id}`, {
      params: { hard_delete: hardDelete }
    });
  },

  // Validate a CORS origin URL
  async validate(origin: string): Promise<CorsOriginValidation> {
    const response = await api.post<CorsOriginValidation>('/cors/origins/validate', null, {
      params: { origin }
    });
    return response.data;
  },

  // Refresh CORS cache
  async refreshCache(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/cors/origins/refresh-cache');
    return response.data;
  }
};

export default corsService;