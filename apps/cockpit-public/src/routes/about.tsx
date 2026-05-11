import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/about")({
  component: AboutPage,
});

function AboutPage() {
  return (
    <article className="max-w-3xl mx-auto prose">
      <h1>À propos de la flotte</h1>
      <p>
        La flotte LLM de L'Électron Rare est fine-tunée sur Apple Silicon (Mac Studio M3 Ultra,
        512 Go de mémoire unifiée) avec MLX. Nous distillons les traces de raisonnement de
        Claude Opus dans des modèles open-source, et publions des adaptateurs traçables sous
        Apache-2.0.
      </p>
      <h2>Transparence EU AI Act Art. 52/53</h2>
      <p>
        Chaque modèle publié est accompagné de sa provenance complète : modèle de base, méthode
        d'entraînement (LoRA / SFT), hyperparamètres, jeux de données (HF-traçables, licences
        Apache/MIT/CC-BY), matériel et SHA d'exécution. Voir{" "}
        <a href="https://github.com/L-electron-Rare/ailiance/blob/main/docs/eu-ai-act-transparency.md">
          le document de transparence AILIANCE
        </a>
        .
      </p>
      <h2>Stack</h2>
      <ul>
        <li>
          Entraînement : MLX bf16 LoRA sur Mistral Large 123B, Qwen3.5-122B/35B, Apertus 70B,
          Devstral 24B, EuroLLM 22B
        </li>
        <li>
          Routage : embeddings Jina v3 + classifieur MLP (40 domaines prédits, 5 fallback) avec
          cache deux niveaux (L1 hash + L2 sémantique)
        </li>
        <li>
          Orchestration : <strong>router v0.3 chaîne Deliberation</strong> — activée
          automatiquement sur <code>model: "ailiance"</code> pour les domaines hardware/code,
          passe la sortie LLM dans un validator iact-bench sandboxé, réessaie avec feedback
          stderr en cas d'échec, émet un audit NDJSON par chaîne. Voir la{" "}
          <a href="/transparency">page transparence</a> pour le détail.
        </li>
        <li>Serving : gateway FastAPI multi-worker, BF16, pool mémoire partagé</li>
        <li>
          Évaluation : Lighteval + EvalPlus + MT-Bench + iact-bench v0.2.0 (31 domaines × 23
          modèles, 25 validators Docker sandboxés)
        </li>
      </ul>
      <h2>Backend portable</h2>
      <p>
        La gateway ailiance et la stack worker <strong>ne sont pas liées à Apple Silicon</strong>.
        Notre déploiement de référence tourne sur Mac Studio M3 Ultra (MLX) et macOS via MLX-LM
        et llama.cpp, mais le même contrat HTTP compatible OpenAI peut être servi depuis
        n'importe quel runtime exposant <code>/v1/chat/completions</code>. Backends confirmés :
      </p>
      <ul>
        <li>
          <strong>Apple Silicon (arm64)</strong> — MLX / MLX-LM (référence), llama.cpp Metal
        </li>
        <li>
          <strong>NVIDIA CUDA (x86_64 / arm64)</strong> — vLLM, TGI, llama.cpp CUDA, Ollama
        </li>
        <li>
          <strong>AMD ROCm (x86_64)</strong> — vLLM ROCm, llama.cpp HIP
        </li>
        <li>
          <strong>Intel / x86_64 générique</strong> — llama.cpp CPU/AVX2/AVX-512, OpenVINO
        </li>
        <li>
          <strong>ARM CPU (Linux arm64, Graviton, Ampere)</strong> — llama.cpp NEON
        </li>
      </ul>
      <p>
        Les modèles publiés sur{" "}
        <a href="https://huggingface.co/clemsail">notre organisation HuggingFace</a> sont
        distribués dans des formats qui couvrent cette matrice : safetensors MLX (Apple Silicon),
        quantizations GGUF (llama.cpp, toutes plateformes), et safetensors bf16 (vLLM / TGI). La
        gateway, le routeur et le pipeline de provenance sont pure Python / FastAPI et tournent
        partout où Python 3.12+ est disponible.
      </p>
    </article>
  );
}
