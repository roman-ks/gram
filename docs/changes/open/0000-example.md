# 0001 — Persist today's list across reloads

> Status: **open** · Type: feature · Created: 2026-06-24

## Goal
Today's entries and running total survive a page refresh, instead of living in
frontend state only. (DESIGN.md §9 flags this as a recommended one-liner.)

## Context
v1 appends entries to frontend state on save and never reloads them. The backend
already exposes `GET /api/entries/today` and `GET /api/today/summary` (§6).

## Acceptance criteria
- [ ] On page load, the list is populated from `GET /api/entries/today`.
- [ ] On page load, the total is populated from `GET /api/today/summary`.
- [ ] Saving a new entry still appends optimistically (no full reload needed).
- [ ] Refreshing the page shows the same entries and total.

## Scope / hints (optional)
- Affected areas: frontend/src/App.svelte
- Out of scope: edit/delete UI, macros display (still calories-only).

## Notes / decisions
<!-- filled in during implementation -->
