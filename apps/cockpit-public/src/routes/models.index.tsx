import { createFileRoute } from '@tanstack/react-router';
import { ModelCard } from '@/components/ModelCard';
import { useModels } from '@/hooks/useModels';

export const Route = createFileRoute('/models/')({
  component: ModelsPage,
});

function ModelsPage() {
  const { data, isLoading, error } = useModels();

  if (isLoading) return <p className="text-slate-500">Loading models…</p>;
  if (error) return <p className="text-rose-700">Failed to load models</p>;
  if (!data || data.length === 0) return <p>No models found.</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Models ({data.length})</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {data.map((card) => (
          <ModelCard key={card.id} card={card} />
        ))}
      </div>
    </div>
  );
}
