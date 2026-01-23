/**
 * API client for fetching visualization data from FastAPI backend
 */

import { VisualizationResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchLevel1Data(): Promise<VisualizationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/visualizations/level1`);

  if (!response.ok) {
    throw new Error(`Failed to fetch Level 1 data: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchLevel2Data(): Promise<VisualizationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/visualizations/level2`);

  if (!response.ok) {
    throw new Error(`Failed to fetch Level 2 data: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchLevel3Data(): Promise<VisualizationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/visualizations/level3`);

  if (!response.ok) {
    throw new Error(`Failed to fetch Level 3 data: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchLevel4Data(): Promise<VisualizationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/visualizations/level4`);

  if (!response.ok) {
    throw new Error(`Failed to fetch Level 4 data: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchLevel5Data() {
  const response = await fetch(`${API_BASE_URL}/api/v1/visualizations/level5`);

  if (!response.ok) {
    throw new Error(`Failed to fetch Level 5 data: ${response.statusText}`);
  }

  return response.json();
}
