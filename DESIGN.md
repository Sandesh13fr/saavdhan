---
name: Bakaya
description: A paper trail for reviewable payment claims
colors:
  green: "#246c54"
  nav: "#173b34"
  workspace: "#f5f6f2"
  paper: "#ffffff"
  ink: "#23382f"
  border: "#dce3d9"
  muted: "#647368"
  supporting-text: "#536747"
  primary-text: "#f7faf1"
  selected-row: "#eff5e7"
  neutral-status: "#edf2e7"
  neutral-status-text: "#5b7153"
  green-status: "#e5f0da"
  green-status-text: "#376744"
  amber-status: "#fcf0d0"
  amber-status-text: "#815e17"
  blue-status: "#e7f0ef"
  blue-status-text: "#3b6570"
typography:
  display:
    fontFamily: "Lora, serif"
    fontSize: "clamp(25px, 2.25vw, 34px)"
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "17px"
    fontWeight: 600
  title:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "14px"
    fontWeight: 600
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "14px"
    lineHeight: 1.65
  label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "13px"
    fontWeight: 500
rounded:
  panel: "8px"
  button: "6px"
  field: "5px"
  badge: "4px"
spacing:
  control-gap: "7px"
  panel-padding: "20px"
  workspace-gap: "21px"
  page-inline: "30px"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.primary-text}"
    rounded: "{rounded.button}"
    padding: "11px 14px"
  button-primary-hover:
    backgroundColor: "#1c5944"
  button-secondary:
    backgroundColor: "#fdfefa"
    textColor: "#41663a"
    rounded: "{rounded.button}"
    padding: "11px 14px"
  field:
    backgroundColor: "{colors.paper}"
    textColor: "#2d532c"
    rounded: "{rounded.field}"
    padding: "11px"
  navigation:
    backgroundColor: "#375a4a"
    textColor: "#e8f1d8"
    rounded: "7px"
    padding: "13px 10px"
  badge-neutral:
    backgroundColor: "{colors.neutral-status}"
    textColor: "{colors.neutral-status-text}"
    rounded: "{rounded.badge}"
    padding: "4px 7px"
  panel:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.panel}"
  source-paper:
    backgroundColor: "{colors.paper}"
    padding: "27px 24px"
---

# Design System: Bakaya

## Overview

**Creative North Star: "The Paper Trail"**

Bakaya uses a calm green and ivory workspace to make financial records inspectable. Serif headings provide the character of a document; compact sans-serif controls and aligned amounts support careful comparison. The approved ledger-first and evidence-first experiences share this world.

The interface makes uncertainty visible through plain status labels and review controls. Synthetic examples are labeled, and human approval precedes local export. These commitments constrain the presentation of records and actions throughout the product.

**Key Characteristics:**
- Deep green navigation and pale working surfaces.
- Crisp paper documents with nearby provenance.
- Compact financial records with tabular numerals.
- Explicit status text and restrained state colors.

## Colors

The palette combines a dark green frame, ivory working space, and white paper, with low-saturation green, amber, and blue status surfaces.

### Primary

- **Working Green** (`green`): primary actions, links, checkbox accents, and text carets.
- **Deep Navigation Green** (`nav`): persistent navigation and the browser theme color.

### Secondary

- **Review Amber** (`amber-status`, `amber-status-text`): checks that require attention, paired with explicit labels.
- **Source Blue** (`blue-status`, `blue-status-text`): informational status badges.
- **Confirmed Green** (`green-status`, `green-status-text`): positive status badges.

### Neutral

- **Workspace Ivory** (`workspace`): the main page ground.
- **Document White** (`paper`): panels, fields, and source documents.
- **Ledger Ink** (`ink`): the global foreground.
- **Quiet Divider** (`border`): panel boundaries and workspace separation.
- **Muted Text** (`muted`) and **Supporting Olive** (`supporting-text`): descriptions and secondary record details.
- **Selected Record** (`selected-row`): row selection, preserving readable records.
- **Neutral Status** (`neutral-status`, `neutral-status-text`): descriptive status labels.

**The Explicit Status Rule.** Always pair a status color with its textual meaning.

## Typography

**Display Font:** Lora, with serif fallback. Local Latin weights are 400 and 500.

**Body Font:** DM Sans, with sans-serif fallback. Local Latin weights are 400, 500, and 600.

The serif is concentrated in page titles, document headings, evidence headings, and dialogs. Sans-serif type carries navigation, financial tables, controls, and explanatory text.

The frontmatter captures the main hierarchy. Page titles balance their lines; page descriptions are limited to 75ch. Table body text uses 11px, table labels 10px, and status badges 9px. Evidence document lines use 12px with a 1.9 line-height and preserve source whitespace. Financial figures and dates use tabular numerals where implemented. Compact supporting labels vary by component; use the existing surrounding component rather than imposing a new global type scale.

## Layout

The desktop shell uses a fixed left sidebar (226px), a topbar (67px), and a content area capped at 1920px. Page padding is 29px above and 30px horizontally. Above 1650px it expands to 35px and 40px.

The ledger workspace pairs a flexible table with a 320px record pane, separated by 21px. Evidence review uses a 210px document browser, flexible document, and 305px facts pane with 16px gaps. The review screen pairs decisions with a 330px packet pane.

At 1300px the shell and supporting panes narrow. At 1050px the ledger becomes one column and the record pane is hidden; evidence facts move below the document and browser. At 760px the sidebar becomes a toggled drawer, the page uses 18px horizontal padding, evidence files become a horizontal strip, and documents and facts stack. Wide financial tables scroll inside their own container; totals become stacked rows. Forms become one column. Preserve this behavior when adding records or controls.

**The Records Before Totals Rule.** Keep the ledger and linked evidence ahead of aggregate figures in the reading order.

## Elevation & Depth

Most surfaces are flat, separated by pale borders and background changes. Only source paper, modal dialogs, and the open mobile navigation drawer use shadows. Source paper sits within a gray-green stage so its boundary remains visible. Avoid introducing lifted cards into the ledger.

## Shapes

Panels and dialogs use gentle corners; controls use smaller corners, and badges are compact. Divider lines organize rows and field groups. Circular avatars identify people; small rounded document thumbnails identify source records. Financial tables remain rectangular and dense rather than turning each row into a card.

## Components

- **Buttons:** compact inline icon-and-label actions, with primary green and outlined pale secondary variants. Hover changes the background; keyboard focus has an offset outline. Disabled buttons reduce opacity and use a disabled cursor.
- **Fields:** plain bordered inputs, selects, and text areas with visible labels and a green focus outline. Existing form groups determine their padding and type size.
- **Navigation:** full-width text-and-icon rows with a green selected background. Mobile navigation uses the same rows in a drawer.
- **Status badges:** compact text labels on pale semantic backgrounds. Allow wrapping where source status or evidence filenames require it.
- **Panels:** white bordered containers with compact headings, internal dividers, and restrained corner rounding.
- **Ledger rows:** tabular amounts align right; the selected invoice receives a pale green row background. Source links stay adjacent to their record.
- **Evidence paper:** white source surface with numbered lines, preserved whitespace, provenance, and original-file access. Unreadable evidence retains an explicit warning.
- **Review and export:** review fields, unresolved checks, approval, and export state remain visible in the relevant panels. Local export follows recorded human approval.

Buttons transition background and text color over 160ms. Source paper settles over 220ms and the mobile drawer slides over 180ms. Reduced-motion preferences disable animations and transitions. Focus styling must remain visible independently of motion.

The final frontend review disposition is **ship** after the supporting-text contrast correction. This is a bounded visual and contract review: a separate quality-bar card was unavailable and the reviewer did not independently rerun backend checks.

No shipping raster assets were added in this design pass. QA screenshots are review evidence, not product assets. Uploaded originals belong to the user's evidence, not the brand imagery library.

## Do's and Don'ts

### Do

- Do keep financial amounts aligned and source links close to their facts.
- Do preserve synthetic labels, unresolved states, and human review before export.
- Do use existing green, ivory, paper, and border roles consistently.
- Do retain keyboard focus and reduced-motion behavior.

### Don't

- Don't present illustrative or synthetic values as verified real claims.
- Don't rely on color alone to explain a status.
- Don't hide uncertainty behind a success treatment.
- Don't add decorative raster imagery to the record workspace.


### Decluttering refinement — 11 October 2026

Three primary routes: Claim workspace, Evidence library, Review & export. Invoices/payments, interest and activity remain under More details. Model settings and diagnostics remain under Agent details; recent decisions are collapsed. Preserve every unresolved question, source link, required confirmation and approval gate.

Secondary text has a12px floor, operational body is13–14px, and mobile controls target44px. Status labels use text with restrained fill. Preparation and new-claim actions are secondary to the review task on an existing claim. Radix Dialog owns help/create modal focus, Escape and explicit opener-focus restoration. Tablet preparation and case controls wrap rather than overflow.

Verification: production build and browser approval/export path passed at desktop1440 and mobile390; tablet768 overflow check passed; secondary navigation, modal focus confinement, Escape and opener restoration passed. Fresh visual reviewer disposition ship for the bounded decluttering pass. Exact comp/card comparison and independent reviewer interaction testing were unavailable. No new imagery or microfrontend split was introduced.
