import test from "node:test";
import assert from "node:assert/strict";
import { allTags, computeKpis, escapeHtml, filterTasks, formatBody, isOverdue, uniqueOwners } from "../js/logic.js";

const TODAY = "2026-11-05";
const tasks = [
  { id: 1, title: "Freeze API", owner: "maya", due: "2026-11-01", status: "pending" },
  { id: 2, title: "Write notes", owner: "omar", due: "2026-11-09", status: "pending" },
  { id: 3, title: "Tag build", owner: "maya", due: "2026-11-02", status: "done" },
  { id: 4, title: "Smoke test", owner: null, due: null, status: "pending" },
];
const notes = [
  { id: 1, title: "a", tags: ["ops", "release:v1.4"] },
  { id: 2, title: "b", tags: ["backend", "ops"] },
];

test("overdue means pending with a past due date", () => {
  assert.equal(isOverdue(tasks[0], TODAY), true);
  assert.equal(isOverdue(tasks[2], TODAY), false);
  assert.equal(isOverdue(tasks[3], TODAY), false);
});

test("filter defaults to pending, sorted by due date with undated last", () => {
  assert.deepEqual(filterTasks(tasks).map((t) => t.id), [1, 2, 4]);
});

test("owner and status filters combine", () => {
  assert.deepEqual(filterTasks(tasks, { owner: "maya", status: "all" }).map((t) => t.id), [1, 3]);
});

test("kpis count open, done, overdue and notes", () => {
  assert.deepEqual(computeKpis(tasks, notes, TODAY), { open: 3, done: 1, overdue: 1, notes: 2 });
});

test("owners and tags are unique and sorted", () => {
  assert.deepEqual(uniqueOwners(tasks), ["maya", "omar"]);
  assert.deepEqual(allTags(notes), ["backend", "ops", "release:v1.4"]);
});

test("escapeHtml neutralises markup", () => {
  assert.equal(escapeHtml('<img src=x onerror="x">'), "&lt;img src=x onerror=&quot;x&quot;&gt;");
});

test("formatBody renders **bold** markers", () => {
  assert.equal(formatBody("ship **today**"), "ship <strong>today</strong>");
});
