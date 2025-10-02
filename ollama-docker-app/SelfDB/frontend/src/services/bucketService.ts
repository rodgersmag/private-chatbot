import api from './api';
import { deleteFile } from './fileService'; // Added import

// Define types
export interface Bucket {
  id: string;
  name: string;
  description?: string;
  is_public: boolean;
  file_count: number;
  total_size: number;
  created_at: string;
  updated_at: string;
}

export interface CreateBucketData {
  name: string;
  description?: string;
  is_public?: boolean;
}

export interface BucketFile {
  id: string;
  filename: string;
  size: number;
  content_type: string;
  created_at: string;
  updated_at: string;
}

// Get all buckets for the current user
export const getUserBuckets = async (): Promise<Bucket[]> => {
  const response = await api.get('/buckets');
  return response.data;
};

// Get a specific bucket by ID
export const getBucket = async (bucketId: string): Promise<Bucket> => {
  const response = await api.get(`/buckets/${bucketId}`);
  return response.data;
};

// Create a new bucket
export const createBucket = async (bucketData: CreateBucketData): Promise<Bucket> => {
  const response = await api.post('/buckets', bucketData);
  return response.data;
};

// Update a bucket
export const updateBucket = async (bucketId: string, bucketData: Partial<CreateBucketData>): Promise<Bucket> => {
  const response = await api.put(`/buckets/${bucketId}`, bucketData);
  return response.data;
};

// Delete a bucket
export const deleteBucket = async (bucketId: string): Promise<void> => {
  await api.delete(`/buckets/${bucketId}`);
};

// Get files in a bucket
export interface FileListParams {
  skip?: number;
  limit?: number;
}

export const getBucketFiles = async (bucketId: string, params: FileListParams = {}): Promise<BucketFile[]> => {
  const { skip = 0, limit = 100 } = params;
  const response = await api.get(`/buckets/${bucketId}/files`, {
    params: { skip, limit }
  });
  return response.data;
};

// New function to delete a bucket and all its contents
export const deleteBucketAndContents = async (bucketId: string): Promise<void> => {
  // First, get the bucket details to know how many files to fetch
  const bucket = await getBucket(bucketId);
  
  if (bucket.file_count > 0) {
    // Fetch all files in the bucket
    // We use bucket.file_count as the limit to ensure all files are fetched.
    // If an API has a maximum limit per request, this might need pagination.
    const files = await getBucketFiles(bucketId, { limit: bucket.file_count });
    
    // Delete all files in parallel
    await Promise.all(files.map(file => deleteFile(file.id)));
  }
  
  // After all files are deleted (or if there were no files), delete the bucket itself
  await deleteBucket(bucketId);
};