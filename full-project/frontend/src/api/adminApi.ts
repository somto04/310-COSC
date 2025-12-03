import { getToken } from "../utils/auth";

const API_BASE = import.meta.env.VITE_API_URL;

function getAuthHeaders(extra: HeadersInit = {}) {
  const token = getToken();
  if (!token) {
    throw new Error("Missing auth token");
  }

  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    ...extra,
  };
}

export async function authGet(path: string) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`GET failed: ${res.status}`);
  return res.json();
}

export async function authPost(path: string, body?: unknown) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`POST failed: ${res.status}`);
  return res.json();
}

export async function authDelete(path: string) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  // 204 = success, but no body to parse
  if (res.status === 204) {
    return null;
  }

  if (!res.ok) {
    throw new Error(`DELETE failed: ${res.status}`);
  }

  return res.json();
}
// add authDelete, authPatch, etc if needed
