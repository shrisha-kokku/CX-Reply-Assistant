// All calls to the backend live here, so the components never build URLs themselves.
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : "Invalid input");
  }
  return data;
}

const post = (path, body) => request(path, { method: "POST", body: JSON.stringify(body) });

export const api = {
  // conversations
  listConversations: () => request("/conversations"),
  getConversation: (id) => request(`/conversations/${id}`),
  sendMessage: (id, sender, body) => post(`/conversations/${id}/messages`, { sender, body }),

  // AI reply
  generateReply: (id) => post(`/conversations/${id}/generate`),
  approveReply: (generationId, finalReply) =>
    post(`/generations/${generationId}/approve`, { final_reply: finalReply }),
  listLogs: () => request("/generations"),

  // knowledge base
  listBrands: () => request("/brands"),
  listKB: (brandId) => request(`/brands/${brandId}/kb`),
  createKB: (brandId, entry) => post(`/brands/${brandId}/kb`, entry),
  updateKB: (brandId, id, entry) =>
    request(`/brands/${brandId}/kb/${id}`, { method: "PUT", body: JSON.stringify(entry) }),
  deleteKB: (brandId, id) => request(`/brands/${brandId}/kb/${id}`, { method: "DELETE" }),
};
