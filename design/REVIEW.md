# Frontend rebuild vs. mock screens

Source of truth: the 14 mock screens and the identity board in `docs/ui/` (kept outside the repo).
Screenshots of the built app: `docs/screenshots/` (synthetic data only, captured by `tools/screenshots/capture.mjs`).

## System (identity board)

Matches:
- Palette: Paper `#F4F4F0` background, Ink `#111111` text and dark pill buttons, Alert `#C62828` logo, warnings and red CTAs, white surfaces with soft offset shadows and 22–28px radii.
- Grey `#72726E` is used only for graphics. Small secondary text uses `#55554F` (6.6:1 on Paper) so it passes WCAG AA.
- Type: Archivo variable (self-hosted, `@fontsource-variable/archivo` width axis). Headlines run at weight 860–900 and 70% width. Noto Sans Devanagari covers Hindi and Marathi. IBM Plex Mono is used for quotes, source refs, hashes and list dates.
- Headlines end in a red full stop (or red `?` / `।`) via the `Headline` component.
- Logo: angular S mark recreated as inline SVG (`components/Brand.tsx`), with the SAAVDHAN wordmark and an SVG favicon.
- Verdict language (board section 09) is the `VerdictStrip`: STOP is a solid red block with white text, VERIFY FIRST has a red outline and red heading, NO RED FLAGS FOUND has a black outline. Each strip carries the verdict body and the recruiter-list line.
- Illustrations are inline SVG with gradients and drop shadows: document, magnifier, stop sign, clock ring, family figures, phone, report stack, pattern nodes and hash graph. No photos are used, and the campus-poster photograph is not used.
- Header on every screen: logo, Check / Check-ins / Help, a language dropdown (EN / हिंदी / मराठी) and a red-outline Demo button that opens a menu with the two synthetic demos. Below 860px the nav moves to a bottom tab bar. Tested at 390px with no horizontal scroll.

Deliberate differences:
- Body copy uses Archivo at normal width, not the condensed cut. Rule: readability and AA for long Devanagari and English text.
- Light theme only. Rule: the brand is Paper. No dark variant was asked for.

## Per screen

| Mock | What matches | Deliberate differences (rule) |
|---|---|---|
| 01 Home | Headline "Before you pay. Before you fly." with red stops, subline, black "Check my offer" pill, document + magnifier + "Tourist visa" callout, dashed line to an outline parent and child, three-step strip (Add offer / See evidence / Plan check-ins). | "Works offline" removed (the check needs the server). Added the board's Hindi line "विदेश की नौकरी? पहले जाँच।" with a red rule. |
| 02 Submit | "Let's check your offer.", left stepper Add / Review / Result, Paste chat / Upload file tabs, dashed upload zone with red badge, "Try demo" link, red "Review details" pill, document illustration. | "Offline mode" removed (no offline mode). The tabs show one input at a time (textarea or upload zone, as the brief asks). Both inputs are kept and sent together, so a tab shows a count or tick when the other input has content. "Try demo" opens the two-demo menu. The privacy note stays under the card. |
| 03 Review | "Does this look right?", stepper at step 2, 2-column fact tiles (icon, label, value, chevron), a red-outlined tile for the flagged value, red dot for missing values, document with magnifier on the flagged value. | No editing (no backend support). Subline reads "Tap a detail to see where it came from." and a tap reveals the verbatim quote in mono with its source ref. Missing values say "Not found in the offer." CTA is "See result", not "Run checks", because the checks already ran when the offer was submitted. "Edit details" returns to step 2 to resubmit. More fields sit under "More details from the offer". Only critical rule hits flag a tile, so the screen stays close to the mock's single red tile. |
| 04 Result STOP | Red octagon with bursts, giant "STOP", "Pause payment and travel. Verify the offer first.", rule rows with icon, red flag badge, title, short status and chevron, "See the evidence" pill, "Get reporting help" link, document with highlighted flagged row. | Every hit and unknown rule is shown (ordered hit > unknown, then severity), not three, and passed checks sit in a collapsed group (product rule). Rows say "Point to check · High", not "Demo data". The demo label is a chip at the top. Added the board's STOP verdict strip with the body text and "Agent list not checked yet." / dated list line (rule 3). Added "Download report packet" and "Make a check-in plan". The left icon sidebar is omitted: no extra destinations exist. Footer lines "Confirm with the Protector of Emigrants before paying." and "Show source quotes + list date", which links to the evidence screen. |
| 05 Result VERIFY FIRST | "VERIFY" black / "FIRST" red, "A few details need confirmation.", demo chip, rows, magnifier over documents with "?" card, "Edit details"-style secondary link. | Rows use the same expandable pattern as STOP, not radio circles (the circles implied a checklist the backend does not store). Primary CTA is "See the evidence" with "Get reporting help", as the brief specifies. Verdict strip and list line added (rule 3). |
| 06 No red flags | "No red flags found." with red stop, calm black magnifier, "View report" pill, "Plan check-ins" link, outlined note box with demo label. | The note "This does not mean safe." is replaced by "This is a check, not a clearance. Still verify independently." because the word "safe" is banned. The verdict strip carries the exact required text: "No red flags found. Confirm with the Protector of Emigrants before paying anything." The three Visa / Fees / Contract summary tiles are replaced by the passed-checks group. They only repeated "Demo data". Note: the local backend cannot return this level until a recruiter list is loaded (`verdict.py`), so it was verified visually with a mocked response, not end to end. |
| 07 Evidence | Chat panel with avatars and bubbles, the quoted line highlighted red with a red dot and a curved connector to the red rule card, "See why it was flagged.", "Rule reference" and "What to ask next" accordions, black "Download report" pill (GET packet ZIP). | Bubbles show the real synthetic offer lines (sender, time, source id in mono) instead of grey placeholders. Added "Flag n of N" with previous/next buttons to step through every flagged rule. Rules without a quote say so. Below 960px the rule card stacks above the chat and the connector is hidden. |
| 08 Check-in setup | "Demo alerts only" chip, "Keep family close.", contact cards with pink avatar and two inputs, permission checkbox, black "Create check-in plan" pill, red clock ring with hours, "Check in every" select, "Add trip details" accordion. | Added a "You" card for the traveller alias (required by the API). The second input is "How to reach them", not "Phone", so users do not enter real numbers. The second contact is optional. The permission checkbox is required before saving (UI-only consent, nothing stored). |
| 09 Check-in | "Time to check in." headline (changes to "Check in now." / "Check-in missed."), clock ring counting down to the next due time, "I'm okay" pill (POST checkin), two-person flat illustration with "2 family contacts" chip, Trip details / Change time / Get help tiles, timeline previous / now / next, "Simulated" chip. | Added an optional note field under "I'm okay" (the API accepts it). The demo skip-ahead control (POST `/api/demo/advance-clock`, 12h) is kept but visually secondary under a dashed divider. A missed state links to the family view. |
| 10 Family alert | "Simulated alert" chip, "Check-in missed.", "Try contacting them first.", "View trip & report" pill (downloads the ZIP), "Reporting options", phone with bell and two contact nodes, traveller card with destination, report ZIP link and chevron. | Added a "Family phone view" chip and per-alert "Simulated (demo)" badges. Each alert shows recipient alias, channel and time (from `safety.alerts`). Shows an empty state before any alert. |
| 11 Get help | "Demo directory" chip, "Find the right help.", cards with pink icon circles and arrow buttons for MEA, MADAD, Embassy, 1930, Police, report stack illustration, "Get report ZIP" pill, "Check current official contact details." footer. | Added eMigrate (check agent RC). Each card shows its address in mono and "Verify on the official site before use". The 1930 card reads "Cyber crime and lost money" because "fraud" is a banned word in copy. Added the limits (not legal advice, no automatic reporting, synthetic demo, can be wrong) and the rule sources list from `/api/meta`. |
| 12 Institution login | "See patterns. Respect privacy.", three report cards on a dashed red loop, "Synthetic data only", card with lock, "Institutional access", email and password fields with icons and show-password toggle, red "Enter demo" pill. | College / Police segmented toggle omitted: the backend has one officer role. CSRF token from login is kept for later requests as before. |
| 13 Pattern map | "Patterns, at a glance." with "Synthetic data" chip, district dropdown, grey district shapes on paper with red markers and halos, "Illustrative map" label, stat cards (Reports, Districts, Repeated hashes, each with a "Demo" chip), district chips and red "Explore patterns" pill. | Uses the existing `features/map` with a new no-basemap paper mode (`basemap={false}`, `variant="canvas"`, `highlight`). No tiles are requested. Highlighted districts also get a red outline, and the tooltips, legend and count list are kept so colour is not the only signal. Stats are computed from `/api/reports/map`. The left icon sidebar is omitted. Repeated agent and template hashes are listed below as links to the detail screen, with sign-out. |
| 14 Pattern detail | Headline "One contact. N districts.", "Synthetic data • Hash xxxx…xxxx" with copy button, centre node linked to district nodes with document badges, accordions (demo reports, districts, full hash), black pill, footer note. | The hash graph is drawn from real data, so the node count varies. "Export demo report" omitted (no backend export for patterns), so the pill returns to the map. Footer note reads "Hashes link reports; repetition alone does not establish wrongdoing." (product wording, not "A pattern is not proof of wrongdoing"). Number shown as a numeral ("5 districts") so it translates. |

## Mock controls with no backend

| Control (mock) | Handling |
|---|---|
| Works offline / Offline mode (01, 02) | Omitted. |
| Tap a detail to edit (03) | Mapped to "view source quote"; "Edit details" goes back to step 2. |
| Run checks (03) | Mapped to "See result" (analysis already ran). |
| Left icon sidebars (04, 13, 14) | Omitted. |
| Radio circles on VERIFY rows (05) | Replaced by expandable rows. |
| Visa / Fees / Contract tiles (06) | Replaced by the passed-checks group. |
| Phone field (08) | "How to reach them" free text (alias channel). |
| Permission checkbox (08) | Kept as a UI-only gate. |
| College / Police toggle (12) | Omitted. |
| All districts dropdown (13) | Highlights one district on the map. |
| Export demo report (14) | Omitted; pill goes back to the map. |

## Accessibility

- Landmarks: header, two navs (desktop and mobile), main, footer. Skip link. Focus moves to main on route change.
- Visible 3px ink focus outline on all controls. Targets are at least 44px.
- Tabs follow the ARIA tab pattern with arrow keys. Menus close on Escape and outside click.
- Rule rows, fact tiles and accordions are buttons with `aria-expanded` / `aria-controls`.
- Status is never colour-only: every row has a text status and severity, and flags have an icon.
- `prefers-reduced-motion` turns off animation. Entry motion only moves elements (no fade from invisible).
- Contrast: Alert on Paper 5.2:1, white on Alert 5.6:1, secondary text 6.6:1.

## Critique pass (impeccable)

DEGRADED: single-context critique. The harness discourages spawning sub-agents unless asked, so Assessments A and B ran in sequence in one context. The detector (`detect.mjs --json frontend/src`) returned no findings. Browser evidence came from Playwright captures at 390px and 1366px.
Findings fixed in the same pass:
- The `hidden` attribute was overridden by component `display` rules. Fixed globally.
- Opacity-0 entry animations could leave art invisible in captures. Motion now starts from a visible state.
- In Hindi and Marathi the wordmark fell back to Devanagari. Fixed.
- Help cards were cramped at desktop width and stacked badly on mobile. Layout and icon sizes adjusted.
- Too many review tiles were red. Now only critical hits flag a tile.
- Row status text wrapped badly. Fixed.

Open items:
- The two-person check-in illustration is simpler than the mock's soft render.
- The Marathi R7 title renders "अॅ" with a dotted circle in Noto Sans Devanagari. The pre-existing string needs native review (possibly "ॲ").
