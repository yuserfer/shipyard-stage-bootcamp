// Entry point: owns the state object and wires events to data loading and rendering.

import { fetchNotes, fetchTasks } from "./api.js";
import { mountReleaseNotes } from "./release-notes.js";
import { renderKpis, renderNotes, renderOwnerFilter, renderTags, renderTasks, renderUpdated } from "./render.js";

const RELEASE_VERSION = "v1.4";
const state = { tasks: [], notes: [], owner: "", status: "pending", q: "", tag: "" };

async function refreshNotes() {
  state.notes = await fetchNotes(state);
  renderNotes(state);
  renderTags(state, toggleTag);
  renderKpis(state);
}

function toggleTag(tag) {
  state.tag = state.tag === tag ? "" : tag;
  return refreshNotes();
}

async function init() {
  document.getElementById("owner-filter").addEventListener("change", (e) => {
    state.owner = e.target.value;
    renderTasks(state);
  });
  document.getElementById("status-filter").addEventListener("change", (e) => {
    state.status = e.target.value;
    renderTasks(state);
  });
  let timer;
  document.getElementById("notes-search").addEventListener("input", (e) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      state.q = e.target.value.trim();
      refreshNotes();
    }, 200);
  });
  [state.tasks, state.notes] = await Promise.all([fetchTasks(), fetchNotes(state)]);
  renderKpis(state);
  renderOwnerFilter(state);
  renderTasks(state);
  renderTags(state, toggleTag);
  renderNotes(state);
  renderUpdated();
  mountReleaseNotes(RELEASE_VERSION);
}

init();
