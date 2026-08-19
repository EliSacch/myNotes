---
name: accessibility-audit
description: >-
  Audit the app for accessibility (a11y) issues against WCAG-oriented checklist
  and PinIt UI patterns. Produces a severity-ranked report with file references
  and fix guidance. Use when the user asks for an accessibility audit, a11y
  review, WCAG check, screen-reader review, keyboard-navigation review, or
  accessibility report.
---

# Accessibility audit

## When to use

Run this skill when the user wants a **review/report**, not when they only want a small UI fix (the project accessibility rule covers day-to-day edits).

## Workflow

1. **Scope** — Default to the whole UI surface (`app/templates/`, `static/css/`, `static/scripts/`). If the user names files, a PR, or a feature, limit to that.
2. **Read first** — Skim templates, CSS, and JS that drive navigation, forms, modals, menus, editors, and flash/status UI. Grep for `aria-`, `role=`, `tabindex`, `focus`, `hidden`, `inert`, `outline`, `prefers-reduced-motion`.
3. **Check** — Walk [checklist.md](checklist.md). Note pass/fail with concrete file paths.
4. **Report** — Use the format below. Do not invent runtime issues you did not verify; mark static-only findings as static review.
5. **Fix?** — Only implement fixes if the user asks. Otherwise end with a prioritized fix order.

## Report format

```markdown
# Accessibility audit

**Scope:** …  
**Method:** static code review (templates / CSS / JS)  
**Summary:** one or two sentences

## Critical / high
- **Finding** — why it matters — `path` (and symbol if useful) — fix

## Medium
- …

## Low / polish
- …

## Already in good shape
- Brief bullets of strengths (only if real)

## Suggested fix order
1. …
```

Severity guide:
- **Critical/high** — blocks keyboard or AT use, missing names, unusable focus, broken dialogs
- **Medium** — incomplete patterns, contrast risk, missing live regions, weak focus management
- **Low** — polish, landmarks, reduced-motion gaps, nice-to-haves

## Project-specific gotchas

- Jinja tooltip macro is visual only (`aria-hidden` on tooltip text) — controls must have their own `aria-label`.
- Note title must use a real `<label>` / visually-hidden label, not `label="title"` on the input.
- Editor.js: set `autofocus: false`; focus the title after `isReady`, deferred with `requestAnimationFrame`.
- Disclosures (`#options-toggler`, `#dashboards-toggler`): Escape, `aria-controls` target, focus in/out.
- Async todo toggle failures should announce via `#a11y-status`.
