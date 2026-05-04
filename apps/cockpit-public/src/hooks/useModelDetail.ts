import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { components } from '@cockpit/shared';

type ModelCard = components['schemas']['ModelCard'];

export function useModelDetail(owner: string, name: string) {
  return useQuery<ModelCard>({
    queryKey: ['model', owner, name],
    queryFn: ({ signal }) =>
      api.get<ModelCard>(`/api/public/models/${owner}/${name}`, { signal }),
  });
}
