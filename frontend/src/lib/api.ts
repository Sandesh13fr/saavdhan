// Fetch wrapper: /api base, same-origin cookies, CSRF header on mutations when signed in.
let csrf = '';
export const setCsrf = (token: string) => { csrf = token || ''; };

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export async function api<T = unknown>(path: string, body?: unknown, method?: string): Promise<T> {
  const headers = new Headers();
  let payload: BodyInit | undefined;
  if (body instanceof FormData) payload = body;
  else if (body !== undefined) { headers.set('Content-Type', 'application/json'); payload = JSON.stringify(body); }
  const verb = method ?? (body !== undefined ? 'POST' : 'GET');
  if (csrf && verb !== 'GET') headers.set('X-CSRF-Token', csrf);
  let res: Response;
  try { res = await fetch(`/api${path}`, { method: verb, headers, body: payload, credentials: 'same-origin' }); }
  catch { throw new ApiError('network', 0); }
  if (!res.ok) {
    let msg = '';
    try {
      const d = (await res.json())?.detail;
      msg = typeof d === 'string' ? d : Array.isArray(d) ? d.map((x: { msg?: string }) => x.msg).join('; ') : d?.message ?? '';
    } catch { /* non-JSON error body */ }
    throw new ApiError(msg, res.status);
  }
  return res.json() as Promise<T>;
}

export const packetUrl = (id: string) => `/api/offers/${encodeURIComponent(id)}/packet`;
