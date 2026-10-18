// Release notes panel: GET /api/releases/<version>/notes, grouped by section.

import { escapeHtml } from "./logic.js";

export function releaseNotesHtml(release) {
  return (release.sections || []).map((section) => `
    <div class="rn-section">
      <h3>${escapeHtml(section.title)} <span class="rn-count">${section.notes.length}</span></h3>
      <ul>${section.notes.map((n) => `<li><strong>${escapeHtml(n.title)}</strong>${n.body ? ` <span>${escapeHtml(n.body.split("\n")[0])}</span>` : ""}</li>`).join("")}</ul>
    </div>`).join("");
}

export async function mountReleaseNotes(version) {
  const box = document.getElementById("release-notes");
  const empty = document.getElementById("rn-empty");
  const button = document.getElementById("rn-copy");
  document.getElementById("rn-version").textContent = version;
  try {
    const res = await fetch(`/api/releases/${encodeURIComponent(version)}/notes`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const release = await res.json();
    box.innerHTML = releaseNotesHtml(release);
    empty.hidden = release.count > 0;
  } catch (err) {
    console.error("Could not load release notes", err);
    box.innerHTML = "";
    empty.hidden = false;
  }
  button.addEventListener("click", async () => {
    const res = await fetch(`/api/releases/${encodeURIComponent(version)}/notes?format=markdown`);
    const text = await res.text();
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = "Copied";
    } catch {
      button.textContent = "Copy failed";
    }
    setTimeout(() => { button.textContent = "Copy as Markdown"; }, 1500);
  });
}
