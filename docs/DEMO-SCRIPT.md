# Demo video script

Target length: **3 to 5 minutes, strict**. Aim for 4:15 with the buffer.

Format: MP4 or MOV, at least 720p (1080p preferred), 80 MB maximum. Required coverage (from the Hack for Social Cause 2027 guidelines): team introduction, real-world problem, prototype walkthrough, user interaction, impact. The video opens with the team introduction and ends with impact.

Everything shown is synthetic. The student is a fictional persona in Pune, not a real person.

## Before recording

- Start the app locally (`uvicorn backend.main:app`), open http://localhost:8000 in a clean browser window at 1280x720 or larger.
- Run the two demo offers once and confirm the results match the table below. Record only after a dry run passes.
- Seed the demo officer (`scripts/seed_demo_officer.py`). Sign in on the map with the password typed from memory or a password manager. Do not show `.env` or a terminal with secrets on screen.
- Close notifications and other tabs. Hide the bookmarks bar.
- Check that the "Synthetic demo data" badge is visible on screen during the demo.

## Timed script

| Time | Screen and action | Narration (sample line) |
|---|---|---|
| 0:00 to 0:20 | Title card, then the team in one frame (names, college, roles) | "We are [team name]. [Name] leads, [name] builds the rules engine, [name] owns the frontend and copy, [name] owns the map and testing. Our project is Saavdhan, which means alert." |
| 0:20 to 0:45 | Problem slide or title card, no data | "Fake overseas job offers move young people into scam compounds. Maharashtra police have rescued Indians who were sent to Thailand on tourist visas. The offers come through WhatsApp, and agents often charge lakhs before anyone checks them." |
| 0:45 to 1:05 | App: nav tab "Check offer". Click "Try a demo offer", then "Bangkok data-entry offer (synthetic)". Click "Check offer". | "A fictional student in Pune gets this WhatsApp message. The offer is fictional. Saavdhan reads it and checks it against MEA guidance." |
| 1:05 to 1:45 | Tab "Result". Pause on the STOP heading. Scroll the red points: R1 (tourist visa), R4 (fee over cap), R6 (corridor and role). Show a quote and "Rule source". Show R2 as "Agent list not checked yet". | "Stop. The offer uses a tourist visa for work. The fee is above the MEA cap. The route and job match the pattern in reported cases. Every point links to the quote and the rule source. The agent list is not loaded in this build, so Saavdhan says so instead of guessing." |
| 1:45 to 2:15 | Tab "Check-in plan". Enter an alias for the traveller (for example "Traveller A", never a real name). Add one contact alias and channel. Enter a short travel plan. Set interval to 6 hours. Click "Save plan". | "The student still decides to go. Saavdhan does not block the trip. The check-in plan uses aliases only, with a contact at home." |
| 2:15 to 2:35 | Click "I am OK, check in now". Show status "On schedule" and the next check-in time. | "The traveller checks in on schedule." |
| 2:35 to 2:55 | Click "Demo: move the clock forward 12 hours". Status shows "Check-in missed". | "Now she misses a check-in. In the demo we move the clock forward instead of waiting." |
| 2:55 to 3:20 | Tab "Family". Show "Missed check-in alert" with the "Simulated (demo)" badge. Click "Open report packet" or "Download report packet" and show the ZIP is produced. | "The contact at home gets a simulated alert and the report packet. Nothing is sent to a real phone in this demo. The person decides what to do next." |
| 3:20 to 3:45 | Tab "Check offer". Click "Dubai offer with gaps (synthetic)" and "Check offer". Show VERIFY_FIRST with the fee point. | "A different offer gives a different answer. This one has a licence number and an employment visa, but its fee is above the cap. Saavdhan asks for written answers instead of saying it is a scam." |
| 3:45 to 4:15 | Tab "Map". Sign in as the demo officer. Show the 36 district map. Point to the one hashed agent that appears across Kolhapur, Nagpur, Nashik, Pune and Thane. Label it "Synthetic data only". | "The pattern map is for authorities and placement cells. It shows one hashed agent number across five districts, not a person's name or phone number." |
| 4:15 to 4:40 | Tab "Limits". Show "Saavdhan never reports anyone automatically" and "Not legal advice". | "Saavdhan does not report anyone and is not legal advice. It is a prototype and the data here is synthetic." |
| 4:40 to 5:00 | Title card with impact: the pilot plan (placement cells, cyber police, Maharashtra districts) and the request for feedback | "Our next step is a pilot with placement cells and cyber police in Maharashtra. Our goal is that a young person checks the job before they board. Thank you." |

Timings are approximate. Cut the Map section first if over time, but keep the team intro and impact.

## Expected demo results (check on a dry run)

| Offer | Expected verdict | Points to show |
|---|---|---|
| `bangkok-data-entry` | STOP | R1 tourist visa, R4 fee over cap, R6 corridor and role; R2 "not checked yet" |
| `dubai-near-miss` | VERIFY_FIRST | R4 fee over cap (high); R2 not checked; R9 information point |

If a dry run shows a different verdict, update the script and the narration, not the code, and report the difference to the lead.

## Narration rules

- Say "synthetic" or "fictional" when showing any offer or data.
- Do not give an all-clear for any offer. The best verdict is "No red flags found. Confirm with the Protector of Emigrants before paying anything."
- Do not name any real agency or person as a fraud.
- Do not read out phone numbers or addresses on screen.

## Recording checklist

- [ ] MP4 or MOV, at least 720p, 80 MB or less (export at 1080p and check size; reduce bitrate if needed)
- [ ] Length 3:00 to 5:00 (check with a media info tool)
- [ ] Team introduction at the start; impact at the end
- [ ] Only synthetic data on screen; no real names, phone numbers, addresses, passwords or `.env` contents
- [ ] "Synthetic" labels visible on the offer, map and family screens
- [ ] Hindi or Marathi copy shown only if native review is done; otherwise use the English UI
- [ ] Audio clear; narration recorded in a quiet room
- [ ] File named for submission (team name placeholder until registration: `Maharashtra_<TeamName>_Demo.mp4`)
- [ ] Reviewed by a human team member before upload; the team lead uploads to the MY Bharat portal
