The prompt below is for Claude Code (or a subagent), because `impeccable` is a Claude Code skill. Codex can't load it. Put your images in the repo first, for example under `design/mocks/` and `design/brand/`, and replace the placeholder paths.

```json
{
  "task": "Craft and polish Saavdhan's frontend to match the provided mock screens and brand guidelines, using the impeccable skill, without changing behaviour, API contracts or product rules.",
  "repo": "C:\\Users\\sande\\OneDrive\\Documents\\Projects_v13\\Saavdhan",
  "inputs": {
    "mock_screens": ["design/mocks/<01-check>.png", "design/mocks/<02-verdict>.png", "design/mocks/<03-checkin>.png", "design/mocks/<04-family>.png", "design/mocks/<05-map>.png", "design/mocks/<06-limits>.png"],
    "brand_guidelines": "design/brand/<brand-guidelines>.png",
    "current_state": "docs/screenshots/*.png (synthetic, captured from the live app)"
  },
  "skills": [
    "Invoke the `impeccable` skill before designing and follow its process (design read, critique, polish).",
    "Also read if present: .agents/skills/ui-ux-pro-max, responsive-design, accessibility-a11y, react, typescript SKILL.md files."
  ],
  "read_first": ["AGENTS.md", "docs/CONTRACTS.md (API shapes, i18n keys)", "frontend/src/App.tsx", "frontend/src/styles.css", "frontend/src/components/**", "frontend/src/screens/**", "frontend/src/features/map/map.css", "frontend/src/i18n/en.json"],
  "step_1_extract": [
    "From the brand guidelines image, write design/TOKENS.md listing colours (hex), type scale and font families, spacing scale, radii, shadows, iconography rules, logo usage and tone-of-voice notes. Mark anything you inferred rather than read from the image.",
    "From each mock, note its layout, components, states and hierarchy, and map it to the existing screen and components. List where the mock conflicts with product rules or existing features (step 2)."
  ],
  "step_2_rules_that_win_over_mocks": [
    "Never show the word 'safe' or an equivalent (सुरक्षित, guaranteed, verified, 100%). The best verdict text stays exactly: 'No red flags found. Confirm with the Protector of Emigrants before paying anything.'",
    "Verdict levels keep their meaning and weight: STOP is clearly alarming (red family); VERIFY_FIRST is amber; NO_RED_FLAGS_FOUND is calm and neutral, not a celebratory green. Colour is never the only signal: keep the icon and text.",
    "Every rule card keeps its verbatim quote, source ref, rule source link or 'Warning sign, not a rule' badge, severity and status. The recruiter-list line ('Agent list not checked yet' or the dated line) stays on the verdict banner.",
    "SYNTHETIC / SIMULATED badges stay visible wherever they appear now.",
    "No real-looking people, phone numbers, agencies or logos of real organisations in any image, icon or placeholder.",
    "Hindi and Marathi must render well: Devanagari-capable font stack (e.g. Noto Sans Devanagari, self-hosted via @fontsource if a new font is needed), no fixed widths that clip longer hi/mr strings, line-height ≥1.5 for Devanagari."
  ],
  "step_3_implement": [
    "Put tokens as CSS custom properties in frontend/src/styles.css (:root), with dark mode via prefers-color-scheme. Remove hard-coded colours from components.",
    "Restyle the existing components and screens to match the mocks: header and language toggle, bottom tab bar (mobile) / top nav (desktop), Check offer (paste area, upload, demo buttons), VerdictBanner, RuleHitCard, QuoteBlock, facts table, check-in plan form and status card, the simulated family phone, map screen chrome (map.css only, not the Leaflet logic), Limits.",
    "Add empty, loading and error states where the mocks show them, using existing i18n keys. If a new string is needed, add the key to en/hi/mr JSON (hi/mr marked for native review in frontend/src/i18n/REVIEW.md) and run python frontend/src/i18n/check_i18n.py.",
    "Motion: subtle and purposeful only, respect prefers-reduced-motion.",
    "If the brand includes a logo, add it as an inline SVG in a component, with an aria-label, and add a favicon."
  ],
  "constraints": [
    "Do not read or print .env.",
    "Plain CSS, no Tailwind, no UI framework, no new runtime dependencies except self-hosted fonts via @fontsource if the brand requires a font we lack.",
    "Do not change API calls, data shapes, routes, i18n key names, backend code or frontend/src/features/map logic.",
    "Mobile-first at 390px; check 768px and 1366px. Touch targets ≥44px. WCAG AA contrast (4.5:1 text, 3:1 UI). Visible focus states. Semantic landmarks and labels.",
    "Keep the JS bundle growth under 30 KB gzipped (fonts excluded); report the before/after size."
  ],
  "files_owned": ["frontend/src/styles.css", "frontend/src/components/**", "frontend/src/screens/**", "frontend/src/App.tsx (markup and classes only)", "frontend/src/features/map/map.css", "frontend/src/i18n/** (new keys only)", "frontend/index.html (fonts, favicon, theme-color)", "frontend/package.json and package-lock.json (fonts only)", "design/**", "docs/screenshots/**"],
  "acceptance": [
    "cd frontend; npm ci; npm run build passes.",
    "C:\\Users\\sande\\OneDrive\\Documents\\Projects_v13\\Saavdhan\\.venv\\Scripts\\python -m pytest tests -q passes (set SAAVDHAN_ENABLE_LLM=false and OPENAI_API_KEY= first).",
    "python frontend/src/i18n/check_i18n.py passes; grep -rniw safe frontend/src finds nothing.",
    "Run the impeccable skill's critique on the result and fix every high-priority item.",
    "Re-capture all screenshots with tools/screenshots/capture.mjs against a local server (SAAVDHAN_ENV=local, SAAVDHAN_ENABLE_LLM=false, temp SAAVDHAN_DATA_DIR, SAAVDHAN_DEMO_OFFICER_PASSWORD=screenshot-officer-pw-2026) and write design/REVIEW.md with a before/after table per screen: what matches the mock, what deliberately differs and why (cite the step-2 rule).",
    "Manual check at 390px in en, hi and mr: no clipped text, no horizontal scroll, the verdict banner readable at a glance."
  ],
  "deliver": "Commit on branch lane/frontend-polish with message 'Polish frontend to brand and mock screens' and a final line 'Co-Authored-By: Claude <noreply@anthropic.com>'. Do not push. Report changed files, bundle delta, contrast checks, screenshot paths and open questions about the mocks."
}
```

To run it:
1. Put the images in `design/mocks/` and `design/brand/`.
2. Replace the `<...>` file names in `inputs` with yours.
3. Create a worktree: `git worktree add ../saavdhan-polish -b lane/frontend-polish`.
4. Open a Claude Code session there and paste the JSON.

If you run this and the OpenFreeMap prompt at the same time, they both touch `frontend/src/features/map/map.css`. Run OpenFreeMap first, or drop `map.css` from this prompt's `files_owned`. Once the images are in the repo, I can run this lane myself.