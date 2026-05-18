import {
  getEvalScores,
  getMascaradeLoras,
  getModelDetail,
  getProvenance,
} from '@/lib/server-fns';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/models/$owner/$name')({
  loader: async ({ params }) => {
    const model = await getModelDetail({ data: params });
    const isMascarade = params.owner === 'ailiance' && params.name === 'mascarade';
    return {
      model,
      evalScores: await getEvalScores({ data: params }),
      loras: isMascarade ? await getMascaradeLoras() : [],
      provenance: await getProvenance({
        data: { modelId: `${params.owner}/${params.name}` },
      }),
    };
  },
});
