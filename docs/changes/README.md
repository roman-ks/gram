# Change requests

Self-contained briefs for features / bug fixes, written so Claude can implement
one **in a single pass**. Architecture decisions still live in
[../DESIGN.md](../DESIGN.md) (§11 decision log); this folder is for *work items*.

## Layout
```
TEMPLATE.md     copy this to start a request
open/           requests not yet shipped (queued or in progress)
done/           shipped requests — full context, kept as history
CHANGELOG.md    one line per shipped change (the skim-able timeline)
```

## Writing a request
1. Copy `TEMPLATE.md` to `open/NNNN-short-title.md` (NNNN = next number, zero-padded).
2. Fill in **Goal** and **Acceptance criteria** at minimum — those drive the work.
3. Hand it to Claude: *"implement docs/changes/open/NNNN-….md"*.

A good request answers: what should be true when done, how to verify it, and any
context not visible in the code. The acceptance criteria are the contract.

## Implementing a request (Claude does this)
1. Read the request + relevant code/DESIGN sections.
2. Implement against the acceptance criteria; tick each box.
3. Record any decisions/tradeoffs under **Notes / decisions**.
4. Flip the header to `Status: **done** · Shipped: YYYY-MM-DD` and move the file
   to `done/`.
5. Add one line to `CHANGELOG.md`.
6. If an *architectural* decision was made, also log it in DESIGN.md §11.

## Conventions
- IDs are sequential and never reused; the number stays with the file forever.
- One request = one cohesive change ("in one go"). Split big asks into multiple files.
- Reference requests in commits/PRs by ID, e.g. `feat: meal editing (#0007)`.
