// The only module that talks to the Shipyard HTTP API.

async function getJson(url, label) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Could not load ${label}`, err);
    return [];
  }
}

export function fetchTasks() {
  return getJson("/api/tasks", "tasks");
}

export function fetchNotes({ q = "", tag = "" } = {}) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (tag) params.set("tag", tag);
  return getJson(`/api/notes?${params}`, "notes");
}
