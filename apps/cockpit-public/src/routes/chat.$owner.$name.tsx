import { ChatPlayground } from '@/components/ChatPlayground/ChatPlayground';
import { useModelDetail } from '@/hooks/useModelDetail';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/chat/$owner/$name')({
  component: ChatPage,
});

function ChatPage() {
  const { owner, name } = Route.useParams();
  const detail = useModelDetail(owner, name);

  if (detail.isLoading) return <p>Chargement…</p>;
  if (!detail.data) return <p>Modèle introuvable.</p>;
  if (!detail.data.chat_eligible) {
    return (
      <p>
        Ce modèle n'est pas activé pour le chat. Voir{' '}
        <a className="underline" href={detail.data.hf_url}>
          HuggingFace
        </a>
        .
      </p>
    );
  }
  return <ChatPlayground modelId={detail.data.id} modelDisplayName={detail.data.display_name} />;
}
