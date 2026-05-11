import { useStatus } from '@/hooks/useStatus';
import { createFileRoute } from '@tanstack/react-router';
import { Activity, AlertCircle, CheckCircle2 } from 'lucide-react';

export const Route = createFileRoute('/status')({
  component: StatusPage,
});

function StatusPage() {
  const { data, isLoading, isError } = useStatus();

  if (isLoading) return <p>Chargement…</p>;
  if (isError || !data) return <p className="text-rose-700">Échec du chargement du statut.</p>;

  return (
    <article className="max-w-3xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Statut en direct</h1>
          <p className="text-sm text-slate-500">
            {data.healthy_count} sur {data.total_count} workers sains ·
            rafraîchi toutes les 15 s
          </p>
        </div>
        <Activity className="text-emerald-600" size={32} />
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {data.workers.map((w) => (
          <div
            key={w.id}
            className={`rounded border p-3 ${
              w.healthy
                ? 'border-emerald-200 bg-emerald-50'
                : 'border-rose-200 bg-rose-50'
            }`}
          >
            <header className="flex items-center justify-between">
              <h3 className="font-semibold">{w.label}</h3>
              {w.healthy ? (
                <CheckCircle2 className="text-emerald-600" size={18} />
              ) : (
                <AlertCircle className="text-rose-600" size={18} />
              )}
            </header>
            <p className="text-xs text-slate-600">{w.host}</p>
            <dl className="mt-2 grid grid-cols-2 gap-x-2 text-xs text-slate-700">
              <dt>latence</dt>
              <dd>{w.latency_ms ? `${w.latency_ms} ms` : '—'}</dd>
              <dt>modèle chargé</dt>
              <dd>{w.model_loaded ? 'oui' : 'non'}</dd>
              <dt>uptime</dt>
              <dd>{w.uptime_s ? `${Math.floor(w.uptime_s / 60)} min` : '—'}</dd>
            </dl>
            {w.error && (
              <p className="mt-2 text-xs font-monon text-rose-700 truncate" title={w.error}>
                {w.error}
              </p>
            )}
          </div>
        ))}
      </div>

      <p className="mt-6 text-xs text-slate-500">
        Dernière mise à jour : {new Date(data.timestamp).toLocaleString()}
      </p>
    </article>
  );
}
