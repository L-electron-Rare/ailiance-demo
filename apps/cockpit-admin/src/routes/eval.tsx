import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/eval')({
  component: EvalPage,
});

function EvalPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold">Eval</h2>
      <p className="text-slate-600 mt-2">Coming in Task 2.12...</p>
    </div>
  );
}
