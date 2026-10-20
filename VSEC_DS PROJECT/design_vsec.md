# RoadCast — UI/UX Design Specification

**Document:** `design.md`  
**Product:** RoadCast — Historical Traffic Analytics  
**Version:** 1.0  
**Audience:** Product designers, frontend developers, data-visualization designers, and QA testers

---

## 1. Design vision

RoadCast should feel like a premium, futuristic traffic-intelligence workspace: visually bold and responsive, but calm enough for users to interpret data accurately. Combine the clarity of an analytics product with the energy of a city at night.

**Core principle: make the data the hero.** Motion should explain state changes, guide attention, and make controls feel responsive—not distract from analysis.

### Product truth

RoadCast analyzes **historical traffic data**. It is not a live navigation service and must not imply current road conditions or guaranteed journey times.

- Show a visible **Historical data** label near the dashboard heading.
- Make the dataset, geography, date coverage, and source easy to find.
- Label traffic volume, speed, congestion, and travel time distinctly, with units and definitions.
- Distinguish measured values, derived categories, synthetic/demo data, and optional model estimates.
- Never use a live-looking pulse to imply live traffic.

### Design principles

1. Clarity before decoration.
2. Progressive disclosure: essential information first, technical detail when requested.
3. Motion with meaning; no animation that makes data ambiguous.
4. Consistent controls and states across pages.
5. Accessibility and reduced motion are first-class requirements.
6. Responsive layouts must preserve chart readability.
7. Be honest about missing data, coverage gaps, uncertainty, and limitations.

---

## 2. Information architecture

### Primary navigation

- **Dashboard** — overview metrics, filters, charts, and findings.
- **Explore Data** — dataset coverage, fields, and data-quality summary.
- **Insights** — notable historical patterns and interpretation.
- **About & Methodology** — source, definitions, preparation, limitations, and optional model methodology.

A **Help / Definitions** control can open a side panel or popover explaining key traffic terms. Do not treat volume, speed, congestion, and travel time as interchangeable.

### Main user journey

1. Open the Dashboard and read the historical-data note.
2. Check the dataset and its coverage.
3. Adjust supported time, date, road/segment, and context filters.
4. Review metrics and charts that reflect the selected filters.
5. Inspect chart points and read plain-language findings.
6. Open Explore Data or About & Methodology to verify source and limitations.

### Page structure

**Global shell:** header/navigation → main content → optional contextual help → footer.

**Dashboard:** heading and historical label → dataset coverage strip → filter toolbar → metric cards → primary chart → secondary charts → insight cards → source/limitations note.

**Explore Data:** heading → dataset summary → coverage indicators → quality summary → field dictionary → preparation notes → source/license/limitations.

**Insights:** heading and intro → shared filters where relevant → evidence-backed insight cards → interpretation and caveats.

**About & Methodology:** product purpose → non-live-data disclaimer → sources and license → field definitions and units → preparation summary → optional model/evaluation details → limitations and acknowledgements.

---

## 3. Layout, grid, and responsive behavior

### Desktop layout

Use a centered content container with a maximum width around **1440 px**.

- Header height: 68–76 px.
- Wide-screen page padding: 32 px; laptop: 24 px; mobile: 16 px.
- Section spacing: 28–36 px.
- Card padding: 20–24 px.
- Card gap: 16–20 px.
- Inputs/buttons: 44–48 px tall.
- Primary chart: approximately 360–440 px tall; never below 300 px without a strong reason.
- Footer top spacing: 40–56 px.
- Use a consistent 4 px spacing scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64 px.

Align page headings, filters, cards, and charts to one shared grid. Use four metric cards per row on wide desktop; two columns for secondary charts; stack sections when labels or plots become cramped.

### Breakpoints

| View | Width | Layout |
|---|---:|---|
| Wide desktop | ≥1440 px | Centered max-width container; four metric cards; paired secondary charts |
| Desktop/laptop | 1024–1439 px | 24 px page padding; multi-column charts if readable |
| Tablet | 768–1023 px | 20 px padding; two metric cards per row; stack complex charts |
| Mobile | 360–767 px | One-column content; compact header; filters in a panel or sheet |
| Very narrow | <360 px | Minimize decoration; wrap labels; prioritize readable controls |

Do not shrink chart labels until unreadable. Reduce tick density or stack charts first. Use horizontal scrolling only where necessary and make it obvious.

### Mobile navigation

Replace the full navigation row with a compact brand mark and menu button. Open a clearly labeled drawer/panel with large touch targets. Put filters behind a **Filters** button that opens a bottom sheet or full-height panel. Show active filter chips on the page. Use one or two metric cards per row depending on available width.

---

## 4. Visual design system

### Suggested palette

A midnight-blue canvas with crisp, bright accents supports the traffic-intelligence theme. These colors are suggestions, not fixed brand requirements.

| Role | Suggested color | Usage |
|---|---|---|
| App background | `#0B1020` | Main canvas |
| Primary surface | `#121A2B` | Cards and panels |
| Elevated surface | `#19243A` | Menus and hover surfaces |
| Primary text | `#F4F7FB` | Headings and essential values |
| Secondary text | `#B7C2D6` | Supporting text |
| Muted text | `#8996AD` | Nonessential hints; verify contrast |
| Primary accent | `#5DE4C7` | Primary actions and selected states |
| Secondary accent | `#7AA7FF` | Links and selected chart series |
| Warm highlight | `#FFC46B` | Findings and notable patterns |
| Error | `#FF727F` | Errors |
| Success | `#65D69A` | Successful completion |
| Border | `#2B3850` | Card/input boundaries |

Verify text contrast against WCAG AA. For charts, use color-blind-conscious combinations plus line styles, markers, or labels. Color must never be the sole signal. Red should mean an actual error or clearly defined adverse state, not automatically “congestion.” Green must not imply “good” unless the legend defines it.

### Typography

Use a readable sans-serif family available in the project; no particular font file is assumed.

| Style | Size | Weight | Usage |
|---|---:|---:|---|
| Page title | 30–36 px desktop; 26–30 px mobile | 650–750 | Main heading |
| Section title | 20–24 px | 600–700 | Major sections |
| Card title | 15–17 px | 600 | Chart/metric titles |
| Metric value | 28–36 px | 650–750 | Key number |
| Body | 15–16 px | 400–500 | Explanatory text |
| Supporting text | 13–14 px | 400–500 | Metadata |
| Chart labels | 12–14 px | 400–500 | Axes and legend |
| Micro-label | 11–12 px | 500–600 | Use sparingly |

Use sentence case, avoid long all-caps labels, and prefer tabular numerals for metric values.

### Shapes, shadows, and iconography

- Cards: 14–18 px radius.
- Inputs/buttons: 10–12 px radius.
- Chips: pill or 8–10 px radius.
- Use subtle 1 px borders and restrained shadows; stronger shadows are reserved for overlays.
- Use gradients sparingly and never behind dense chart labels.
- Use one consistent line-icon style for dashboard, map pin, calendar, clock, filter, search, info, download/export if supported, chevron, close, warning, and external link.
- Possible assets: wordmark or typographic placeholder, abstract route motif, navigation/control icons, and optional empty-state illustration. Do not assume specific asset files exist or use a decorative map that could be mistaken for live navigation.

---

## 5. Detailed page layouts

### 5.1 Global header

**Desktop:** RoadCast wordmark on the left; primary navigation; help/definitions and only those utility actions the product supports on the right.

**Mobile:** compact wordmark plus menu button.

The active navigation item uses a clear underline, indicator, or filled state—not color alone. Header actions need accessible names and visible focus. Do not invent profile/account controls if accounts are not part of the product.

### 5.2 Dashboard

#### A. Page heading

- Title: **Historical traffic dashboard**
- Short description: “Explore how traffic patterns vary across the selected period and road segments.”
- Visible **Historical data** label with a help affordance explaining that results are not live traffic.
- Dataset name or selector only if multiple datasets are supported.
- Optional “View data source” link only if a real destination exists.

Stack these items on mobile.

#### B. Dataset and coverage strip

Show dataset name, geography/road-network coverage, start/end dates, retrieval/update date where known, and a source-details link. Omit unknown values or mark them unavailable; never invent coverage details.

#### C. Filter toolbar

Use one row on wide screens and wrap naturally on smaller screens. Include only filters supported by the selected dataset:
- Date range / time period.
- Time of day.
- Road, segment, or location.
- Weather/holiday or other context, only if those fields exist.
- **Apply filters** when changes are explicit.
- **Reset** to restore documented defaults.

Give each control a visible label. Show active selections as removable chips. Preserve selections after errors and show a small loading state during updates. If filters update immediately, avoid triggering a costly refresh for every rapid intermediate change. Explain unavailable filters when useful.

#### D. Summary metric cards

Four cards on wide desktop; two per row on tablet; one or two per row on mobile.

Potential metrics, only if supported:
1. Average traffic volume with correct unit/definition.
2. Average speed with unit.
3. High-congestion periods with the threshold/definition.
4. Data coverage/observations with the counted unit (records, days, segments, etc.).

Each card has a short label, main value, unit, optional valid comparison, and info tooltip. Use a sparkline only when it adds genuine analytical value. Never fabricate values or present a derived score as a direct observation.

#### E. Primary visualization

A large chart card with title, short explanatory subtitle, metric/unit, optional supported selector, plot, axis labels, legend, “How to read this chart” affordance, and optional detail/expand action.

Choose chart type to answer a real question:
- Time series for change over time.
- Bar chart for comparing periods or segments.
- Heatmap for time-of-day/day-of-week patterns when data supports it.
- Scatter plot for relationships between measured variables.

#### F. Secondary visualizations

Use two columns on desktop and stack on smaller screens. Each chart must answer a distinct question, have its own title, description, unit, and legend where needed. Do not force a fixed chart count if the selected dataset cannot support it.

#### G. Insights

Each insight card includes a descriptive headline, one or two sentences about the observed pattern, selected period/segment context, link to supporting evidence when possible, and a caveat if sample size or coverage is limited. Use “In this dataset…” phrasing. Do not imply correlation proves causation.

#### H. Data limitations and footer note

At the bottom of the Dashboard, clearly state that data is historical, summarize important coverage limitations, and link to the source and methodology. Keep the global footer compact: RoadCast, navigation, source/methodology, and project attribution if required.

### 5.3 Explore Data

1. Heading and short description.
2. Dataset summary: source, license, retrieval date, geography, coverage when known.
3. Coverage cards: date range, record count, segments, fields—only if available.
4. Data-quality summary: missingness, duplicates, invalid ranges, and cleaning notes when checked.
5. Field dictionary table: field name, meaning, unit, availability.
6. Expandable preparation notes.
7. Source and limitations.

Tables need clear headers, readable row spacing, mobile overflow handling, and warnings that are not color-only.

### 5.4 Insights

Use a clear intro, shared filters where relevant, and one- or two-column insight cards. Each card needs finding, evidence, context, and limitation. Selecting an insight may navigate to or highlight its supporting chart if that behavior is implemented. If there are no valid findings, explain that plainly instead of generating unsupported claims.

### 5.5 About & Methodology

Use readable sections for: what RoadCast is/is not; source and license; definitions and units; data preparation; chart interpretation; optional model and evaluation details if applicable; known limitations; acknowledgements. Technical details may be expandable, but essential caveats stay visible.

---

## 6. Component hierarchy and states

### Reusable components

- Global header and responsive navigation
- Page heading and historical-data label
- Dataset coverage strip
- Filter toolbar, date controls, selects, checkboxes, search where supported
- Applied-filter chip
- Metric card
- Chart card, legend, tooltip, selected-point details
- Insight card
- Info tooltip/help popover
- Data-quality indicator
- Source/limitations note
- Loading skeleton, empty state, error panel
- Toast/inline feedback
- Modal, side panel, mobile filter sheet
- Footer

### Component anatomy

**Metric card:** label → value/unit → optional comparison/context → info affordance → optional small trend.

**Chart card:** title/subtitle → optional controls → plot → legend/labels → note or coverage context.

**Insight card:** finding → evidence/context → supporting-chart action → caveat.

**Forms:** labels above controls; minimum practical height 44 px; visible focus, selected, disabled, and error states. Explain invalid input close to the field. Placeholders never replace labels.

**Tooltips/popovers:** short explanations only; essential instructions must also be visible elsewhere. Support hover, keyboard focus, and tap. Keep within viewport; Escape dismisses overlays.

Every interactive component should define default, hover (where supported), focus, pressed, selected, disabled, loading, success/error, and empty states as applicable.

---

## 7. Animation system

### Motion personality

Use confident, crisp, slightly futuristic motion. Concentrate the “wow” effects in the first page reveal, route accents, chart entrance, and micro-interactions. Keep analysis itself calm and stable.

### Timing tokens

| Token | Duration | Easing | Use |
|---|---:|---|---|
| Instant | 80–120 ms | Ease-out | Pressed feedback, tiny color changes |
| Fast | 140–180 ms | Ease-out | Hover and chips |
| Standard | 200–280 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Cards, dropdowns, filter panels |
| Emphasis | 320–450 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Entrance reveals and overlays |
| Ambient | 1.8–3.0 s | Ease-in-out | Optional route-line accent |

Avoid long bounces for routine analytics actions. Do not animate large layout shifts.

### 7.1 Required hover effects

Hover behavior is for hover-capable devices only. Touch and keyboard users receive equivalent selected/focus feedback.

| Element | Hover effect | Duration | Notes |
|---|---|---:|---|
| Primary button | Slightly brighter accent; lift 1–2 px; soft accent shadow | 140–180 ms | Maintain text contrast |
| Secondary button | Brighter surface and border | 140–180 ms | Keep hierarchy clear |
| Navigation item | Text brightens; underline/indicator slides in | 160–220 ms | Active state stays distinct |
| Metric card | Border brightens; lift 2–3 px; slight shadow increase | 180–220 ms | Avoid disruptive scaling |
| Chart card | Subtle border accent/elevation | 180–220 ms | Do not resize plot |
| Chart point | Marker enlarges slightly; tooltip appears; series highlights | 100–160 ms | Include exact value and unit |
| Legend item | Related series highlights; others may dim slightly | 120–180 ms | Do not hide data unexpectedly |
| Filter chip | Surface brightens; remove icon becomes clearer | 140–180 ms | Adequate hit target |
| Text link | Underline strengthens and link color shifts | 120–160 ms | Preserve clear link affordance |
| Icon button | Surface highlight and slight icon emphasis | 120–160 ms | Explain ambiguous icons |
| Table row | Subtle surface highlight | 100–150 ms | Preserve row separation |
| Info icon | Accent tint; tooltip opens after short delay | 140–180 ms | Also support focus/tap |
| Clickable insight card | Border/shadow strengthens; lift 1–2 px | 160–200 ms | Make destination/state clear |

Do not show a pointer cursor for decorative elements. Hover must never be the only indication that something is interactive.

### 7.2 Required click/pressed effects

| Element | Click response | Timing | Outcome |
|---|---|---|---|
| Primary button | Scale to about 0.98 or press down 1 px; accent darkens slightly | 80–120 ms | Action starts; show loading if needed |
| Secondary button | Surface darkens and moves down 1 px | 80–120 ms | Action starts |
| Navigation | Active indicator moves to destination | 180–240 ms | New page/section becomes active |
| Select/dropdown | Fade plus short vertical reveal | 160–220 ms | Focus moves into menu |
| Apply filters | Pressed state, then subtle chart loading state | 120 ms press | Filters remain visible |
| Reset filters | Chips/controls transition to defaults smoothly | 160–240 ms | Documented defaults restored |
| Remove filter chip | Chip fades/scales out; remaining chips reflow | 140–180 ms | Filter removed |
| Chart point | Marker gets ring/highlight and persistent selected state | 120–180 ms | Show details if supported |
| Legend toggle | Series fades or changes emphasis | 160–240 ms | Legend reflects visibility |
| Expand chart | Smooth expansion or detail-view transition | 220–320 ms | Preserve context and offer close/back |
| Modal/panel open | Fade plus short scale/slide | 220–320 ms | Focus enters overlay |
| Modal/panel close | Reverse transition | 180–260 ms | Focus returns to trigger |
| Menu toggle | Icon transitions to close state; panel slides/fades | 180–240 ms | Expanded state is announced |
| Export/copy, if supported | Brief press and feedback after completion | 100–160 ms | Never claim success prematurely |

Animations must not delay the underlying action.

### 7.3 Signature “crazy” animations

**A. Dashboard entrance reveal**
- Reveal heading, coverage strip, metric cards, then charts.
- Fade in with a 10–16 px upward movement.
- Stagger sibling cards by 40–70 ms.
- Keep the full sequence around 400–700 ms and never block controls.
- Do not replay the whole sequence on every filter change.

**B. Animated route-line accent**
- Add a thin abstract road/route curve to the intro, header, or empty state.
- Animate a small highlight traveling along it once on initial load or very slowly as ambient decoration.
- Keep opacity low and ensure it cannot be mistaken for live vehicle movement.
- Remove or freeze it under reduced motion.

**C. Metric count-up**
- Count to the final value over about 350–650 ms on initial render only.
- Use only for real or documented derived metrics.
- Avoid repeated count-ups during rapid filter changes.
- Do not imply false precision; show final values immediately under reduced motion.

**D. Chart draw-in**
- Line charts draw over 350–600 ms on first render.
- Bars grow from the baseline over 250–450 ms.
- Keep axes/labels stable.
- For filter changes, prefer a subtle crossfade/series transition rather than a full dramatic redraw.
- Never animate in missing observations or imply an unsupported order.

**E. Subtle magnetic button**
- On hover, a decorative icon/highlight may move 1–2 px toward the pointer; text and hit area stay stationary.
- Disable on touch and reduced-motion settings.
- No large pointer-following movement.

**F. Insight reveal**
- Fade/slide insight heading and cards into view once per page visit.
- Do not hide content until animation completes or replay on every scroll.

**G. Filter-chip pop**
- New chips fade/scale from 0.96 to 1.0; removed chips fade/scale out.
- Animate only the changed chip, not the entire toolbar.

**H. Loading shimmer**
- Use restrained shimmer on skeleton cards/chart placeholders while loading.
- Reserve final content dimensions to prevent layout shifts.
- Use a static placeholder under reduced motion.
- Never show a fake live pulse when nothing is loading.

### 7.4 Reduced motion and motion safety

Respect the system/browser reduced-motion preference. Remove parallax, magnetic movement, ambient route animation, count-ups, and large transforms; use immediate changes or short fades instead. Never flash rapidly, shake repeatedly, or place continuous animation behind text or charts. Provide a complete static state for every animation. No action may require waiting for motion to finish.

---

## 8. Chart and data-visualization UX

- Every chart answers a clear question and includes title, axis labels, units, and a legend when needed.
- Keep tick density readable and avoid overlapping labels.
- Use consistent units across comparable charts.
- Use zero baselines for bar charts when appropriate; clearly explain any justified nonzero baseline.
- Never use color alone to distinguish a critical series.
- Show missing/unavailable values explicitly rather than treating them as zero.
- Disclose intentional interpolation or smoothing.
- Distinguish measured values, calculated indicators, and model estimates.
- Avoid false decimal precision.

### Hover, tap, and selection

Hovering a point shows date/time or category, value, unit, and series. Keep the tooltip inside the plot/viewport and avoid covering the point. Tapping on touch screens shows the same detail. A clicked point stays highlighted until changed or dismissed. Provide a clear way to clear selection; selection cannot depend on hover alone. Support keyboard access to data points or a textual/table alternative.

### Accessible chart alternatives

For each meaningful chart, provide a concise text summary and/or accessible data table. A download option is appropriate only if export is actually supported. Color and animation are enhancements, not the only route to information.

### Loading, empty, error, and partial-data states

- **Loading:** keep chart title visible, show skeleton plot and “Updating chart…” or similar. Avoid replacing the whole page with a spinner.
- **Empty:** explain that no observations match the filters and offer a relevant next action such as widening the period or clearing filters.
- **Error:** concise message and retry only if supported; preserve filters; do not expose stack traces.
- **Partial data:** show gaps and explain missing coverage when known.

---

## 9. Feedback and microcopy

Use brief, non-alarmist language. Toasts should be non-blocking, consistently placed, and never cover essential controls. Use text plus an icon, not color alone. Important errors should be inline near the relevant control. Show success only after the operation succeeds.

Empty states should explain the situation, offer a useful next step, and contain no invented findings. Avoid confirmation dialogs for reversible actions such as removing a filter chip.

**Preferred copy**
- “Historical traffic patterns”
- “Selected period”
- “Average speed (km/h)” or the actual dataset unit
- “No observations match these filters.”
- “This pattern appears in the selected historical data.”
- “View source and limitations”
- “Some periods have missing observations.”

**Avoid**
- “Live traffic” unless the product later has a verified live-data source.
- “Guaranteed travel time.”
- Unsupported causal claims such as “Weather caused congestion.”
- Vague labels such as “Traffic” when the chart actually shows vehicle count, speed, or a derived score.
- Alarmist “Critical” labels without a defined threshold.

Use consistent date/time formatting and identify the dataset’s time zone when known.

---

## 10. Accessibility requirements

Target **WCAG 2.2 AA**.

### Contrast
- Normal text: at least **4.5:1**.
- Large text: at least **3:1**.
- Meaningful UI boundaries and graphical objects: at least **3:1** where required.
- Check muted text, chart ticks, input borders, and focus indicators, not just headings.
- Even when a disabled control is exempt from a contrast requirement, its disabled state should remain understandable.

### Keyboard and focus
- All controls reachable in logical keyboard order.
- Use a visible 2–3 px focus outline with sufficient offset.
- Never remove default focus without an adequate replacement.
- Escape dismisses menus/dialogs when appropriate.
- Move focus into an opened modal and return it to the trigger when closed.
- Do not leave focus inside hidden or closed content.

### Screen readers and semantics
- Use logical heading hierarchy and meaningful page landmarks.
- Give icon-only buttons accessible names.
- Associate labels and errors with form controls.
- Announce loading/results politely without rereading the whole dashboard.
- Give charts accessible names and summaries.
- Mark decorative route motifs/icons as decorative.
- Use correct semantics for navigation, links, buttons, tables, dialogs, and control states.

### Touch and cognitive accessibility
- Aim for touch targets at least **44 × 44 px**.
- Keep controls separated and avoid drag-only interactions.
- Provide tap behavior equivalent to hover behavior.
- Explain domain terminology in plain language.
- Keep filter state visible and provide a clear reset.
- Do not rely on motion, color, or technical jargon as the only way to convey meaning.

---

## 11. Responsive behavior details

**Desktop:** use horizontal space for metric cards and paired charts; keep filters visible where practical; support hover and keyboard tooltips.

**Tablet:** reduce padding; stack charts when axes become crowded; use two metric cards per row; let filters wrap rather than compress.

**Mobile:** one primary column; filters in a panel/sheet; large touch targets; legends below charts where needed; reduce tick density before shrinking type; avoid hover-only controls and pointer-following effects. Preserve the historical-data caveat and source context without excessive scrolling.

---

## 12. Visual performance

These are design quality requirements, not a prescribed technology stack.

- Prefer opacity/transform animation over expensive layout changes.
- Reserve chart/card space before content loads.
- Avoid animating every component simultaneously.
- Stop ambient motion when unnecessary and honor reduced motion.
- Validate animation on lower-powered mobile devices.
- Keep the dashboard usable if decorative animation fails.
- Never let motion obscure data, interrupt focus, or delay controls.

---

## 13. Design handoff checklist

### Structure
- [ ] Header, navigation, main container, and footer are defined.
- [ ] Dashboard, Explore Data, Insights, and About & Methodology layouts are covered.
- [ ] Desktop, tablet, mobile, and narrow-screen behavior is specified.
- [ ] Shared spacing and component anatomy are consistent.

### Data clarity
- [ ] Historical—not live—data is stated clearly.
- [ ] Dataset source and coverage are visible when known.
- [ ] Metric labels include definitions/units.
- [ ] Observed values, derived indicators, synthetic data, and model estimates are distinguishable.
- [ ] No unsupported values, charts, or findings are introduced.

### Interaction and motion
- [ ] Interactive components define hover, focus, pressed, selected, disabled, loading, and error states as applicable.
- [ ] Touch users do not depend on hover.
- [ ] Hover and click timings follow the motion system.
- [ ] Entrance, chart, metric, and route accents are purposeful.
- [ ] Reduced-motion alternatives are defined.
- [ ] Dialogs, menus, chips, and chart selection have clear outcomes.

### Accessibility and polish
- [ ] Contrast is checked against WCAG 2.2 AA.
- [ ] Keyboard order and visible focus are verified.
- [ ] Touch targets are sufficiently large.
- [ ] Charts have accessible summaries or data alternatives.
- [ ] Color is not the sole carrier of meaning.
- [ ] Loading, error, empty, and partial-data states are defined.
- [ ] No animation implies live traffic or unsupported precision.
- [ ] Assets are described without assuming nonexistent files.

---

## 14. Final design direction

RoadCast should feel like a refined, futuristic analytics product with a memorable first impression and a calm, trustworthy core. Use the midnight canvas, crisp accent colors, route-line motif, animated chart entrances, metric count-ups, and responsive micro-interactions to create energy. Keep the user’s task central: select a period, understand the traffic measures, compare patterns, and interpret findings with limitations in view.

The best experience is not the one with the most animation. It is the one where every animation, hover state, and click response makes the interface easier to understand, more satisfying to use, and more trustworthy.
