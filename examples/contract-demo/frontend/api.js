const API_BASE = import.meta.env.VITE_API_BASE;

export async function loadUser(id) {
  const res = await fetch(`${API_BASE}/api/users/${id}`);
  return res.json();
}

export async function saveUser(user) {
  const res = await fetch(`${API_BASE}/api/users`, {
    method: "POST",
    body: JSON.stringify(user),
  });
  return res.json();
}

export function deleteUser(id) {
  return fetch(`${API_BASE}/api/users/${id}`, { method: "DELETE" });
}
