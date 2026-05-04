import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 2, staleTime: 5_000, refetchInterval: 5_000, refetchOnWindowFocus: true },
  },
});
