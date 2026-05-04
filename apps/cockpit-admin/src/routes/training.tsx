import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/training')({
  component: TrainingPage,
});

function TrainingPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold">Training</h2>
      <p className="text-slate-600 mt-2">Coming in Task 2.10...</p>
    </div>
  );
}
