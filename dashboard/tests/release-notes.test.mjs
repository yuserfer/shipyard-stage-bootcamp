import test from "node:test";
import assert from "node:assert/strict";
import { releaseNotesHtml } from "../js/release-notes.js";

const release = {
  version: "v1.4",
  count: 2,
  sections: [
    { key: "backend", title: "Backend", notes: [{ id: 1, title: "Search <fast>", body: "LIKE escaped\nsecond line", tags: [] }] },
    { key: "ops", title: "Operations", notes: [{ id: 2, title: "Rollback plan", body: "", tags: [] }] },
  ],
};

test("renders one block per section with a count", () => {
  const html = releaseNotesHtml(release);
  assert.equal((html.match(/class="rn-section"/g) || []).length, 2);
  assert.match(html, /Backend <span class="rn-count">1<\/span>/);
});

test("escapes titles and shows only the first body line", () => {
  const html = releaseNotesHtml(release);
  assert.match(html, /Search &lt;fast&gt;/);
  assert.match(html, /LIKE escaped/);
  assert.doesNotMatch(html, /second line/);
});

test("empty release renders nothing", () => {
  assert.equal(releaseNotesHtml({ version: "v9.9", count: 0, sections: [] }), "");
});
