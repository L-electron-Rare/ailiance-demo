import { getStatus } from '@/lib/server-fns';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/status')({
  loader: async () => {
    const [statusResult] = await Promise.allSettled([getStatus()]);
    return {
      status: statusResult.status === 'fulfilled' ? statusResult.value : null,
    };
  },
});
