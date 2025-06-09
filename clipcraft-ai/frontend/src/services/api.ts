// File: src/services/api.ts
// Copy paste semua code ini ke file src/services/api.ts

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface ProcessVideoResponse {
  success: boolean;
  job_id: string;
  message: string;
  status: string;
}

export interface JobStatus {
  job_id: string;
  status: string;
  progress: number;
  current_step: string;
  youtube_url: string;
  clip_count: number;
  created_at: string;
  error?: string;
}

export interface ClipResult {
  clip_id: string;
  title: string;
  duration: number;
  confidence: number;
  type: string;
}

export interface ProcessingResult {
  job_id: string;
  video_title: string;
  clips: ClipResult[];
}

// API functions
export const videoAPI = {
  // Test connection to backend
  testConnection: async (): Promise<any> => {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Connection test failed:', error);
      throw error;
    }
  },

  // Start video processing
  processVideo: async (youtubeUrl: string, clipCount: number = 5): Promise<ProcessVideoResponse> => {
    try {
      const response = await api.post('/api/process-video', null, {
        params: {
          youtube_url: youtubeUrl,
          clip_count: clipCount
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Process video failed:', error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Failed to start video processing');
    }
  },

  // Get job status
  getJobStatus: async (jobId: string): Promise<JobStatus> => {
    try {
      const response = await api.get(`/api/status/${jobId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get status failed:', error);
      if (error.response?.status === 404) {
        throw new Error('Job not found');
      }
      throw error;
    }
  },

  // Get final results
  getResult: async (jobId: string): Promise<ProcessingResult> => {
    try {
      const response = await api.get(`/api/result/${jobId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get result failed:', error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  },
};

// Helper function to validate YouTube URL
export const isValidYouTubeUrl = (url: string): boolean => {
  const youtubePatterns = [
    /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
    /^https?:\/\/(www\.)?youtu\.be\/[\w-]+/,
    /^https?:\/\/(www\.)?youtube\.com\/embed\/[\w-]+/,
    /^https?:\/\/(m\.)?youtube\.com\/watch\?v=[\w-]+/
  ];
  
  return youtubePatterns.some(pattern => pattern.test(url));
};