/**
 * API Client Module
 * Handles the communication contract between Frontend and Backend.
 */

export interface AnalysisResult {
  situation: string;
  predicted_action: string;
  risk: string;
  recommended_action: string;
  urgency: string;
  confidence: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const analyzeSituation = async (file: File, context: string): Promise<AnalysisResult> => {
const formData = new FormData();
// FIX: Changed 'image' to 'file' to match the backend requirement
formData.append('file', file); 
if (context) {
formData.append('text_context', context);
}

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(response.status === 400 ? `Bad Request: ${errorText}` : 'Failed to connect to backend');
  }

  try {
    return await response.json() as AnalysisResult;
  } catch (err) {
    throw new Error('Malformed response received from server');
  }
};