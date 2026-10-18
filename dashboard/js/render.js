// DOM rendering. Each function owns one region of index.html and reads only the state it is given.

import { allTags, computeKpis, escapeHtml, filterTasks, formatBody, isOverdue, uniqueOwners } from "./logic.js";

const $ = (id) => document.getElementById(id);

export function renderKpis(state) {
  const k = computeKpis(state.tasks, state.notes);
  $("kpi-open").textContent = k.open;
  $("kpi-done").textContent = k.done;
  $("kpi-overdue").textContent = k.overdue;
  $("kpi-notes").textContent = k.notes;
}

export function renderOwnerFilter(state) {
  const select = $("owner-filter");
  const current = select.value;
  select.innerHTML = '<option value="">All owners</option>' +
    uniqueOwners(state.tasks).map((o) => `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`).join("");
  select.value = current;
}

export function renderTasks(state) {
  const rows = filterTasks(state.tasks, state);
  $("tasks-body").innerHTML = rows.map((t) => `
    <tr class="${isOverdue(t) ? "overdue" : ""}">
      <td>${escapeHtml(t.title)}</td>
      <td>${escapeHtml(t.owner || "–")}</td>
      <td>${escapeHtml(t.due || "–")}</td>
      <td><span class="status status-${t.status}">${t.status}</span></td>
    </tr>`).join("");
  $("tasks-empty").hidden = rows.length > 0;
}

export function renderTags(state, onToggle) {
  const box = $("tag-chips");
  box.innerHTML = allTags(state.notes).map((tag) =>
    `<button class="chip ${tag === state.tag ? "active" : ""}" data-tag="${escapeHtml(tag)}">#${escapeHtml(tag)}</button>`).join("");
  box.querySelectorAll(".chip").forEach((chip) => chip.addEventListener("click", () => onToggle(chip.dataset.tag)));
}

export function renderNotes(state) {
  $("notes-list").innerHTML = state.notes.map((n) => `
    <li>
      <h3>${escapeHtml(n.title)}</h3>
      <p>${formatBody(n.body)}</p>
      <div class="note-tags">${(n.tags || []).map((t) => `<span>#${escapeHtml(t)}</span>`).join("")}</div>
    </li>`).join("");
  $("notes-empty").hidden = state.notes.length > 0;
}

export function renderUpdated() {
  $("last-updated").textContent = `updated ${new Date().toLocaleTimeString()}`;
}
