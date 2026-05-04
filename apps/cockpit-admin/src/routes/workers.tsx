import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/workers')({
  component: WorkersPage,
});

function WorkersPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold">Workers</h2>
      <p className="text-slate-600 mt-2">Coming in Task 2.11...</p>
    </div>
  );
}
