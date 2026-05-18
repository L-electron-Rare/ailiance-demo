import { createApiClient } from '@cockpit/shared';

// Server-side base URL: in Docker the api service is reachable by name.
// Locally it is the dev API on 127.0.0.1:9100.
// `process` is not in the DOM lib; read via globalThis to avoid pulling
// @types/node into a DOM-typed app.
const SERVER_API_BASE =
  (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env
    ?.INTERNAL_API_URL ?? 'http://127.0.0.1:9100';

export const serverApi = createApiClient({ baseUrl: SERVER_API_BASE });
