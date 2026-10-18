// Pure, DOM-free rules for the release dashboard. Covered by dashboard/tests/logic.test.mjs.

export function todayIso(now = new Date()) {
  return now.toISOString().slice(0, 10);
}

export function isOverdue(task, today = todayIso()) {
  return task.status !== "done" && Boolean(task.due) && task.due < today;
}

export function filterTasks(tasks, { owner = "", status = "pending" } = {}) {
  return tasks
    .filter((t) => (status === "all" ? true : t.status === status))
    .filter((t) => (owner ? t.owner === owner : true))
    .sort((a, b) => (a.due || "9999-12-31").localeCompare(b.due || "9999-12-31") || a.id - b.id);
}

export function computeKpis(tasks, notes, today = todayIso()) {
  return {
    open: tasks.filter((t) => t.status !== "done").length,
    done: tasks.filter((t) => t.status === "done").length,
    overdue: tasks.filter((t) => isOverdue(t, today)).length,
    notes: notes.length,
  };
}

export function uniqueOwners(tasks) {
  return [...new Set(tasks.map((t) => t.owner).filter(Boolean))].sort();
}

export function allTags(notes) {
  return [...new Set(notes.flatMap((n) => n.tags || []))].sort();
}

export function escapeHtml(text) {
  return String(text ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function formatBody(body) {
  return String(body ?? "").replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}
