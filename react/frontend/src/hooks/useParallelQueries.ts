import { useQueries } from '@tanstack/react-query';

interface QueryConfig {
  key: string;
  endpoint: string;
}

export function useParallelQueries<T>(queries: QueryConfig[]) {
  return useQueries({
    queries: queries.map(({ key, endpoint }) => ({
      queryKey: [key],
      queryFn: async (): Promise<T> => {
        const response = await fetch(`/api${endpoint}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch ${endpoint}`);
        }
        return response.json();
      },
      staleTime: 5 * 60 * 1000,
    })),
  });
}
