import type { EpisodeResult } from './models';

export const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const search = async (query: string): Promise<EpisodeResult[]> => {
  const response = await fetch(`${BASE_URL}/search?q=${encodeURIComponent(query)}`);

  if (!response.ok) {
    throw new Error(`${response.status} when fetching`);
  }

  return (await response.json()).episodes;
};
