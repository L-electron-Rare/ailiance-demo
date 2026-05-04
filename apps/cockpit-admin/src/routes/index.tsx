import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <p className="text-slate-600 mt-2">
        Widgets land here in Task 2.13. Use the nav above to drill into Training, Workers, Eval.
      </p>
    </div>
  );
}
