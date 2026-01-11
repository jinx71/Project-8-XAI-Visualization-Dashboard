import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface ClassProbability {
  label: string;
  probability: number;
}

export interface PredictionData {
  predicted_label: string;
  confidence: number;
  probabilities: ClassProbability[];
  original_image: string;
  gradcam_overlay: string;
  explanation: string;
  demo_mode: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  message: string;
}

const api = axios.create({ baseURL: BASE_URL, timeout: 60000 });

export async function predictImage(file: File): Promise<PredictionData> {
  const form = new FormData();
  form.append('file', file);

  try {
    const { data } = await api.post<ApiResponse<PredictionData>>(
      '/api/predict',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    );
    if (!data.success || !data.data) {
      throw new Error(data.message || 'Prediction failed.');
    }
    return data.data;
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const detail = err.response?.data?.detail;
      throw new Error(detail ?? err.message);
    }
    throw err;
  }
}

export interface HealthData {
  status: string;
  demo_mode: boolean;
  classes: string[];
  input_size: number;
}

export async function fetchHealth(): Promise<HealthData> {
  const { data } = await api.get<ApiResponse<HealthData>>('/api/health');
  if (!data.data) throw new Error('Health check failed.');
  return data.data;
}
