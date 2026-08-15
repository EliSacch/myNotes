# Accessibility audit checklist

Use while reviewing. Mark each item pass/fail with evidence.

## Document & landmarks
- [ ] `html[lang]` set
- [ ] Skip link to main content
- [ ] `<main id="main-content">` (or equivalent) present
- [ ] Multiple `<nav>` elements have distinct `aria-label`s
- [ ] Sensible heading order; avoid extra `<h1>`s inside dialogs

## Names & icons
- [ ] Every icon-only control has an accessible name (`aria-label` or visible text)
- [ ] Decorative icons have `aria-hidden="true"`
- [ ] Tooltips are not the sole name; visible on keyboard focus (`:focus-within`)

## Keyboard & focus
- [ ] All interactive controls reachable via Tab
- [ ] Visible `:focus-visible` (or equivalent) on interactive elements
- [ ] No `outline: none` without a replacement indicator
- [ ] Opening add/edit/modals moves focus appropriately
- [ ] Closing returns focus to a sensible trigger
- [ ] Programmatic focus is deferred when opening UI from another control (avoid “focused but can’t type”)

## Forms
- [ ] Inputs have associated labels
- [ ] Required fields exposed accessibly
- [ ] Errors use `aria-invalid` + `aria-describedby` and/or `role="alert"`
- [ ] Focus moves to error/invalid field on failed submit

## Dialogs
- [ ] `role="dialog"`, `aria-modal="true"`, labelled by title
- [ ] Background inert / non-interactable while open
- [ ] Escape closes
- [ ] Focus trapped or inert background so Tab stays usable
- [ ] Dialog title is not a competing page-level `<h1>`

## Disclosures / menus
- [ ] `aria-expanded` reflects state
- [ ] `aria-controls` points at the revealed panel
- [ ] Escape closes; optional outside-click dismiss
- [ ] Focus moves into panel on open when appropriate

## Status & async
- [ ] Flash/toast messages in a live region
- [ ] Failed async actions (e.g. todo toggle) announced to AT
- [ ] Loading buttons expose busy state (`aria-busy` / disabled)

## Visual design
- [ ] Text/icon contrast likely meets WCAG AA against backgrounds
- [ ] Focus ring contrast is adequate
- [ ] Error state not color-only
- [ ] Hit targets reasonably large (~24×24px minimum where practical)

## Motion
- [ ] `prefers-reduced-motion` respected for transitions/animations that could distract or block
