# Deck outline

Hack for Social Cause 2027, theme 8 (Digital Safety & Cyber Fraud Awareness), sub-theme 8a: scam detection and reporting assistant for job-offer scams. State framing: Maharashtra. Aligned with UN SDG 8.7 and 16.2.

## Format rules

- 6 to 7 slides. Use the IIT Bombay template. **The template file is not in this repository; the team must apply it.**
- PDF, 10 MB maximum. Compress images before export.
- File name: `Maharashtra_<TeamName>_Deck.pdf`. Team name is a placeholder until registration.
- Slides 1 and 2: problem. 3 and 4: solution. 5: impact and scalability. 6 and 7: team, implementation and AI-tools disclosure.
- Speaker notes on every slide (below).
- No invented impact numbers. Targets are marked TBD until the team sets them.

## Judging criteria map

| Criterion | Where it is answered |
|---|---|
| Relevance | Slides 1, 2 |
| Technical Strength (robustness, code and docs quality) | Slides 3, 4, 6 |
| Functionality (working prototype, scale across regions and languages) | Slides 4, 5 |
| Creativity and Innovation | Slides 3, 4 |
| Social Cause Impact (measurable KPIs, clear proposal) | Slide 5 |
| Presentation and Team Synergy | Slides 6, 7 |

## Slide 1: The problem (1 of 2)

**Title:** Fake overseas job offers lead young people into scam compounds.

**On the slide:**
- Maharashtra police rescued over 60 Indians from Myanmar scam centres, reportedly lured online and sent to Thailand on tourist visas (as reported by Scroll).
- MEA has warned about fake Thailand data-entry jobs leading into Myanmar (as reported by EastMojo).
- Karnataka Cyber Command flagged IT, customer-support and data-entry roles in Thailand, Myanmar, Laos and Cambodia in July 2026 (as reported by ThePrint).

**Speaker notes:** Open with the team and the problem in one sentence. Name the offers as they arrive: WhatsApp messages with a tourist visa and a high fee. Quote the sources as reported; the team has not verified the figures independently. Do not name any agency as a fraud.

## Slide 2: The problem (2 of 2): who is affected and the gaps

**Title:** Beneficiaries and gaps.

**On the slide:**
- Beneficiaries: young job seekers in Maharashtra, families at home, placement cells in colleges, cyber cells.
- Gaps: MEA rules (work visa, three-party contract, registered agents, fee cap as reported at Rs 30,000 + 18% GST) are not checked at the moment of decision. Unregistered agents charge Rs 2 to 5 lakh, mostly over WhatsApp (as reported by Greater Kashmir).
- Nobody sees the pattern across cases.

**Speaker notes:** Explain that the decision to pay happens in a chat, before anyone can check the rules. Keep the framing to Maharashtra. Mention the Belagavi case as reported by Deccan Herald (Rs 2.5 lakh paid for Singapore data-entry jobs, ended in Cambodia, January 2026).

## Slide 3: The solution (1 of 2): check before you pay

**Title:** Saavdhan: check the job before you board.

**On the slide:**
- Paste an offer or upload a screenshot, letter or PDF.
- 12 rules with quoted evidence and rule sources.
- Verdicts: STOP, VERIFY_FIRST, NO_RED_FLAGS_FOUND. The best verdict always says to confirm with the Protector of Emigrants.
- Models read; Python decides.

**Speaker notes:** Show the difference between a verdict an AI model gives and a verdict the rules give. Stress that the app never gives an all-clear for an offer. Mention the Hindi, Marathi and Hinglish readers (the Hindi and Marathi copy is pending native review).

## Slide 4: The solution (2 of 2): check-in net and pattern map

**Title:** If they still go: check-in net and the pattern map.

**On the slide:**
- Check-in plan: up to two contacts (aliases), itinerary and interval. A missed check-in raises a simulated alert with the report packet. Nothing is sent in the prototype.
- Pattern map: anonymised reports by district (36 Maharashtra districts), phone numbers salted and hashed, offer wording grouped by template.
- Stack and architecture: FastAPI, React, SQLite, Tesseract OCR, optional LLM through an OpenAI-compatible gateway. Reuses the author's open-source Bakaya evidence engine.

**Speaker notes:** Keep the demo to one screen. Say plainly which parts are simulated: the alerts, the map data and the demo clock. The pattern-map data is synthetic.

## Slide 5: Impact and scalability

**Title:** Potential impact, measured by KPIs, scaled by region and language.

**On the slide:**
- KPIs (targets TBD by team):
  - Share of checked offers that get STOP or VERIFY_FIRST, with a human-reviewed sample to confirm accuracy.
  - Share of people who contact the family check-in before paying (pilot survey).
  - Time from offer to verdict (median 2.3 ms on the eval set; end-to-end pilot time TBD).
  - Number of placement cells and cyber cells using the pattern map (pilot target TBD).
- Scalability: extraction in English, Hindi, Marathi and Hinglish today. Add a language by adding copy and extractor vocabulary. The rules are the same across regions; the district list is configurable.
- Pilot plan: placement cells in two or three colleges in Maharashtra, then the cyber police cell in one district; measure KPIs over one term.
- Sustainability model: free for individuals; placement cells and cyber cells as partners; hosting cost covered by the partner institution (to be confirmed).

**Speaker notes:** Present impact as potential and a pilot plan. Do not state any number of people helped. Say the eval numbers come from 40 synthetic offers tuned on the same set, so they are optimistic. Mention the legal review and the DPDP open questions before any pilot.

## Slide 6: Team, implementation and roadmap

**Title:** Team, roles and roadmap.

**On the slide:**
- Team roles (names and colleges to be added; up to three students): team lead and submissions; rules and backend; frontend, copy and accessibility; data and testing (eval set, map data); a non-technology member for policy and pilot liaison.
- Roadmap: prototype (done), native-language review, held-out evaluation set, pilot with a placement cell, pilot with the cyber cell, MEA recruiter-list loader, legal review.
- Resource requirements: laptop and browser; small cloud host for the pilot (to be costed); Tesseract with Hindi and Marathi data (free); optional LLM gateway access (to be costed); time of a native reviewer for Hindi and Marathi.
- Repository: `README.md`, `docs/ARCHITECTURE.md`, `docs/RULES.md`, `docs/PRIVACY.md`, `eval/`, `tests/`, `LICENSE` (MIT).

**Speaker notes:** Introduce each member by role. Name the Bakaya reuse and that its author is the same person as the project author, as stated in the README. Describe the roadmap in order of risk: the recruiter-list loader and legal review come before the pilot.

## Slide 7: AI-tools disclosure and estimated AI share

**Title:** How AI was used, and how much of the work it produced.

**On the slide:**
- Tools: Claude Code (lead, Opus 5.5), Claude subagents (Sonnet and Haiku 5.5) for rules, extraction, frontend, check-in net, copy, QA, review and docs; Codex CLI for the evaluation data and the map.
- Human work: problem framing, product rules, every decision on verdict copy, review and testing, native-language review (pending), legal review (pending), final submission.
- Estimated AI share: **90 to 95 per cent of code and documentation drafted with AI tools, under human direction and review.** This is an estimate, not a measurement. Method: team judgement from the commit history and review logs in `AI_USAGE.md`.

**Speaker notes:** The AI disclosure is mandatory. Say the estimate is the team's judgement, that AI drafted most of the code and text, and that humans decided, reviewed and tested every change. Point to `AI_USAGE.md` for the log. Re-estimate at feature freeze.

## Checks before export

- [ ] IIT Bombay template applied; slide count 6 to 7
- [ ] PDF 10 MB or less
- [ ] File name `Maharashtra_<TeamName>_Deck.pdf`
- [ ] Every number traces to a source or is marked TBD
- [ ] No personal data, no Annexure content
- [ ] AI disclosure on slide 7 matches `AI_USAGE.md`
- [ ] Each slide mapped to a judging criterion (table above)
