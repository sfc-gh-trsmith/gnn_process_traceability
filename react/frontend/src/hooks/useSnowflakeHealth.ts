import { useQuery } from '@tanstack/react-query';
import { useAppStore } from '../stores/appStore';
import { useEffect } from 'react';

interface HealthResponse {
  status: string;
  error?: string;
}

export function useSnowflakeHealth() {
  const { setConnectionStatus } = useAppStore();

  const query = useQuery<HealthResponse>({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await fetch('/api/health');
      const data = await response.json();
      return data;
    },
    refetchInterval: 30000,
    retry: false,
  });

  useEffect(() => {
    if (query.isLoading) {
      setConnectionStatus('checking');
    } else if (query.isError || query.data?.status === 'disconnected') {
      setConnectionStatus('disconnected', query.data?.error || 'Unable to connect to Snowflake');
    } else {
      setConnectionStatus('connected');
    }
  }, [query.isLoading, query.isError, query.data, setConnectionStatus]);

  return query;
}
