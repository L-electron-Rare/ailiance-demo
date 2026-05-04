import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/chat/$owner/$name')({
  component: ChatPage,
});

function ChatPage() {
  return <div>Chat - Placeholder for Task 1.16</div>;
}
