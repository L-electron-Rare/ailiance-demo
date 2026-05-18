import { getModelDetail } from '@/lib/server-fns';
import { ApiError } from '@cockpit/shared';
import { createFileRoute, notFound } from '@tanstack/react-router';

export const Route = createFileRoute('/chat/$owner/$name')({
  notFoundComponent: () => (
    <main className="wrap" style={{ padding: '64px 0' }}>
      <h1 className="display">Modèle introuvable.</h1>
    </main>
  ),
  loader: async ({ params }) => {
    const model = await getModelDetail({ data: params }).catch((err) => {
      if (err instanceof ApiError && err.status === 404) throw notFound();
      throw err;
    });
    return { model };
  },
});
