import { getModels, getStatus } from '@/lib/server-fns';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/models/')({
  loader: async () => {
    const [modelsResult, statusResult] = await Promise.allSettled([getModels(), getStatus()]);
    if (modelsResult.status === 'rejected') throw modelsResult.reason;
    return {
      models: modelsResult.value,
      status: statusResult.status === 'fulfilled' ? statusResult.value : null,
    };
  },
});
