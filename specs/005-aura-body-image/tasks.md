# Tasks: Aura Rebrand & Div Hotspot Body Map

**Input**: Design documents from `/specs/005-aura-body-image/`
**Prerequisites**: body-hotspots-spec.md, plan.md, spec.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US4)

---

## Phase 1: Setup

**Purpose**: Prepare image asset and update types

- [x] T001 [US1] Optimize `bodyimage_divided.png` → `frontend/src/assets/body/body-image.jpg` (JPEG, < 200KB)
- [x] T002 [US1] Update `frontend/src/components/body-map/types.ts` — remove `PolygonData`, add `HotspotData { region, top, left, width, height }`

**Checkpoint**: Types ready, image optimized

---

## Phase 2: Cleanup (Delete old polygon files)

**Purpose**: Remove SVG polygon data files replaced by inline hotspot arrays

- [x] T003 [P] [US1] Delete `frontend/src/components/body-map/body-data-front.ts`
- [x] T004 [P] [US1] Delete `frontend/src/components/body-map/body-data-back.ts`
- [x] T005 [P] [US1] Delete `frontend/src/components/body-map/body-data-face.ts`

**Checkpoint**: Old polygon data removed

---

## Phase 3: User Story 1 — Div Hotspot Body Map (Priority: P1) MVP

**Goal**: Replace SVG polygon body map with 3 CSS-cropped panels + div hotspots
**Independent Test**: Load Dashboard, verify 3 panels render, hover/click regions, detail data loads

- [x] T006 [US1] Rewrite `frontend/src/components/body-map/BodyMap.vue` — 3 panel divs with `overflow:hidden` + `marginLeft` CSS crop, single `<img>` per panel from `body-image.jpg`, `<button>` hotspots with % positioning (15 front, 8 back, 5 face), hover/click/selected states, density via border color
- [x] T007 [US1] Verify `frontend/src/views/DashboardView.vue` — layout already uses `#050505` background, no changes needed

**Checkpoint**: Three-panel div hotspot body map functional

---

## Phase 4: User Story 2 — App Rename to Aura (Priority: P1)

**Goal**: Replace all "MedTracker" branding with "Aura"
**Independent Test**: Check login page, sidebar, browser tab

- [x] T008 [P] [US2] Edit `frontend/src/views/LoginView.vue` — "MedTracker" → "Aura"
- [x] T009 [P] [US2] Edit `frontend/src/components/AppLayout.vue` — sidebar title → "Aura"
- [x] T010 [P] [US2] Edit `frontend/index.html` — `<title>` → "Aura"

**Checkpoint**: Zero instances of "MedTracker" in UI

---

## Phase 5: User Story 3 — Dark Theme Verification (Priority: P2)

**Goal**: Body map section uses dark holographic aesthetic
**Independent Test**: Visual inspection

- [x] T011 [US3] Verify `BodyMapLegend.vue` and `BodyMapTooltip.vue` — already dark-themed, no changes needed

**Checkpoint**: Dark theme verified

---

## Phase 6: User Story 4 — Density & Treatment Indicators (Priority: P2)

**Goal**: Visit density and active treatment visualization on hotspot divs
**Independent Test**: Create visits/treatments, verify colored borders and orange glow

- [x] T012 [US4] Density shown via `getDensityColor()` border + inset box-shadow on hotspot divs; active treatments get orange border (`#F59E0B`) — implemented inline in `hotspotStyle()` and `.has-treatment` class

**Checkpoint**: Data visualization complete

---

## Phase 7: Polish

- [x] T013 [P] Rename `SVG_REGION_KEYS` → `SELECTABLE_REGION_KEYS` in `body-regions.ts`
- [ ] T014 [P] Test responsive layout — panels stack vertically on mobile (< 768px)
- [x] T015 [P] Verify image size (189KB < 200KB) and build passes

---

## Dependencies & Execution Order

```
Phase 1 (T001 → T002)
  ↓
Phase 2 (T003 ∥ T004 ∥ T005)
  ↓                                Phase 4 (T008 ∥ T009 ∥ T010)
Phase 3 (T006 → T007)
  ↓
Phase 5 (T011)
  ↓
Phase 6 (T012)
  ↓
Phase 7 (T013 ∥ T014 ∥ T015)
```

### Task Summary

- **Total tasks**: 15
- **Completed**: 14
- **Remaining**: 1 (T014 — manual responsive testing)
- **Per-story**: US1=7 (setup+cleanup+core), US2=3, US3=1, US4=1, Polish=3
- **MVP scope**: Phases 1-4 (T001-T010)
