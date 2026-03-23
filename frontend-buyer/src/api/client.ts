const API = "/api/v1";
let accessToken: string | null = localStorage.getItem("ecommerce_token");
let refreshToken: string | null = localStorage.getItem("ecommerce_refresh");

export function setTokens(a: string, r: string) { accessToken = a; refreshToken = r; localStorage.setItem("ecommerce_token", a); localStorage.setItem("ecommerce_refresh", r); }
export function clearTokens() { accessToken = refreshToken = null; localStorage.removeItem("ecommerce_token"); localStorage.removeItem("ecommerce_refresh"); }
export function getToken() { return accessToken; }
export function getSessionId() { let s = localStorage.getItem("ecommerce_session"); if (!s) { s = crypto.randomUUID(); localStorage.setItem("ecommerce_session", s); } return s; }

export async function apiFetch<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const h: Record<string, string> = { ...(opts.headers as Record<string, string> || {}) };
  if (accessToken) h["Authorization"] = `Bearer ${accessToken}`;
  h["X-Session-Id"] = getSessionId();
  if (!(opts.body instanceof FormData) && !h["Content-Type"]) h["Content-Type"] = "application/json";
  let res = await fetch(`${API}${path}`, { ...opts, headers: h });
  if (res.status === 401 && refreshToken) {
    const r = await fetch(`${API}/auth/refresh`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh_token: refreshToken }) });
    if (r.ok) { const d = await r.json(); setTokens(d.access_token, d.refresh_token); h["Authorization"] = `Bearer ${d.access_token}`; res = await fetch(`${API}${path}`, { ...opts, headers: h }); }
  }
  if (!res.ok) { const e = await res.json().catch(() => ({ detail: res.statusText })); throw new Error(e.detail || "Request failed"); }
  if (res.status === 204) return undefined as T;
  return res.json();
}
