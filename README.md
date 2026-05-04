# kiki-cockpit

Frontend for training, evaluation, and testing of L'Électron Rare's LLM fleet.

- **Public showcase**: gallery + provenance + chat playground for the 3 EU-KIKI Live models, HF deep-link for the 24 published HF models
- **Admin (Tailscale-only)**: monitoring training runs, worker health, eval results, and (future sprints) eval/train orchestration

See [`docs/superpowers/specs/`](docs/superpowers/specs/) for design specs.

## Stack

Monorepo (pnpm + uv) with:
- `apps/api` — FastAPI service (`kiki-cockpit` on studio:9100)
- `apps/cockpit-public` — Vite + React 19 (public vitrine)
- `apps/cockpit-admin` — Vite + React 19 (Tailscale-only admin)
- `packages/shared` — `@cockpit/shared` (types, UI primitives, hooks)

## Development

```bash
pnpm install
uv sync
pnpm dev        # boots all apps in parallel
```
