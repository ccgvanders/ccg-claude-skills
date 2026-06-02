---
name: html-print-form
description: >
  Use this skill whenever the user wants to build a structured form as a single HTML file
  that works interactively on screen AND prints cleanly to PDF via the browser's print dialog.
  Triggers include: marking rubrics, observation or feedback forms, self-assessment sheets,
  interview or moderation records, checklists, any structured template where the user will
  fill it in digitally and then print or export to PDF. Read this skill before writing any
  HTML form intended for print output — it captures decisions that took significant iteration
  to get right and will save time on every future task of this type.
---

# HTML Print Form Skill

## Overview

The goal is a **single self-contained HTML file** that:
- Looks and behaves like a structured form on screen
- Prints to PDF via browser Print → Save as PDF with layout and content fully preserved
- Requires no server, no dependencies, no installation

This is not a web app — it is a document-replacement tool. Design decisions should always
prioritise print fidelity over screen interactivity where the two conflict.

---

## When to use this pattern

The HTML print form sits in a gap that other common tools don't fill well. Use it when:
- **One person fills in the form** (not a data collection tool for multiple respondents)
- **The PDF document is the deliverable** — the output is what matters, not the data behind it
- **Print fidelity is a hard requirement** — layout, structure, and formatting must survive export

Typical use cases: incident reports, observation records, referral forms, moderation records,
interview notes, self-assessment sheets, field trip notes — anywhere the *document* is the
end product rather than the *data*.

### How it compares to other tools

| Tool | Best for | Poor for |
|---|---|---|
| **HTML print form** | Single user, structured input, PDF is the deliverable | Multi-respondent data collection, analysis |
| **Microsoft Forms** | Collecting multiple responses, Power Automate routing, analysis | Print/PDF output, document generation |
| **Fillable PDF** | Fixed-layout forms requiring Acrobat compatibility | Easy authoring, iterative updates |
| **Word template** | Familiar editing, narrative documents | Consistent print output, enforced structure |

### Privacy and hosting
The form holds **no data server-side** — it is pure HTML/CSS/JS. Nothing is transmitted or
stored anywhere. Data exists only in the user's browser while filling in, and leaves only
as a PDF on their own device. This makes it *more* private than Microsoft Forms, which
sends responses to Microsoft's servers.

For hosting, **GitHub Pages** is the simplest option for blank templates with no sensitive
content — free, renders correctly in any browser, and requires no infrastructure. For forms
that should remain behind the school network, IIS on an existing internal Windows Server is
the right call.

Note: SharePoint document libraries typically **download** HTML files rather than rendering
them — direct SharePoint links will not work as expected.

---

## Core principles

### 1. Always read the source document first
If the user uploads a Word doc, PDF, or image of the form, read and visually inspect it
before writing any code. The structure, field labels, column widths, and visual hierarchy
all need to match the original. Use `pandoc` or LibreOffice conversion + `pdftoppm` to
render a visual preview where needed.

### 2. Single file, no external dependencies
All CSS and JS inline in the HTML file. No CDN links, no external fonts. Use system fonts
(`'Segoe UI', Calibri, Arial, sans-serif`) which are available in all Windows/Mac print
environments and render reliably at small point sizes.

### 3. CCG brand colours (when relevant)
- Navy `#24356f`, Foundation Blue `#1e439b`, Dark Navy `#192752`, Burgundy `#991b2a`
- Only apply brand colours when explicitly requested or for official CCG documents
- For teaching/classroom documents: use a professional blue-grey palette derived from navy

---

## Text input fields — the right element for each use

### Short single-line text (names, dates, identifiers)
Use a plain `<input type="text">` with `border: none; border-bottom: 1px solid #999`.
This renders as an underline on screen and prints as a static underline in PDF.

```css
input[type="text"] {
  border: none;
  border-bottom: 1px solid #999;
  outline: none;
  font-family: inherit;
  font-size: inherit;
  background: transparent;
  width: 220px;
  padding: 1px 2px;
}
input[type="text"]:focus { border-bottom-color: var(--navy); }
```

### Multi-line comment / notes fields — USE contenteditable, NOT textarea
**Never use `<textarea>` for fields that need to print.** Textareas scroll and clip — any
text that exceeds the visible height is invisible in the printed PDF.

Use a `contenteditable` div instead, wrapped in a relative-positioned container so an
overflow warning can be positioned beneath it:

```html
<div class="comments-wrapper">
  <div class="comments-editable"
       id="f-comments"
       contenteditable="true"
       data-placeholder="Enter comments here…"
       spellcheck="true"
       role="textbox"
       aria-multiline="true"></div>
  <div class="comments-overflow-warning" id="comments-overflow-warning">
    ↕ Content extends beyond the visible box — it will print in full when you export to PDF.
  </div>
</div>
```

```css
.comments-wrapper { position: relative; }

.comments-editable {
  width: 100%;
  min-height: 9em;       /* size to anticipated content — 9em ≈ 6–8 lines */
  height: 9em;
  padding: 4px 2px;
  font-family: inherit;
  font-size: 8.5pt;
  line-height: 1.55;
  color: #1a1a1a;
  outline: none;
  overflow-y: auto;      /* scrollable on screen — content is never lost */
  overflow-x: hidden;
  word-break: break-word;
  white-space: pre-wrap;
  border: 1px solid var(--border);
  border-radius: 3px;
}

/* Placeholder via CSS pseudo-element */
.comments-editable:empty::before {
  content: attr(data-placeholder);
  color: #aaa;
  pointer-events: none;
}

/* Overflow warning — hidden until JS detects overflow */
.comments-overflow-warning {
  display: none;
  margin-top: 4px;
  font-size: 7.5pt;
  color: #8a1a25;
  background: #fff0f2;
  border: 1px solid #f0c0c5;
  border-radius: 3px;
  padding: 3px 8px;
}
.comments-overflow-warning.visible { display: block; }
```

**Critical print rules:** In `@media print`, expand the box to full content height and
suppress the overflow warning (it's no longer relevant — everything prints):

```css
@media print {
  .comments-editable {
    overflow: visible;
    height: auto;
    border: 1px solid #999;
    background: #fff !important;
  }
  .comments-overflow-warning { display: none !important; }
}
```

**Overflow warning JS:** Wire up a live check on the `input` event. Also call it from
`resetForm()` after clearing the field so the warning dismisses on reset:

```javascript
const commentsBox     = document.getElementById('f-comments');
const commentsWarning = document.getElementById('comments-overflow-warning');

function checkCommentsOverflow() {
  const overflowing = commentsBox.scrollHeight > commentsBox.clientHeight + 2; // +2px tolerance
  commentsWarning.classList.toggle('visible', overflowing);
}

commentsBox.addEventListener('input', checkCommentsOverflow);
```

In `resetForm()`:
```javascript
commentsBox.textContent = '';
checkCommentsOverflow();
```

### Why scroll + warning, not overflow: hidden
The previous pattern used `overflow: hidden`, which silently hides content the user has
typed — a poor contract. The scroll + warning approach makes the behaviour explicit:
- **On screen:** content is scrollable and fully accessible; nothing is lost
- **In print:** box expands to full height; everything renders
- **Warning:** tells the user there is more content than the fixed box shows, and reassures
  them it will all appear in the PDF

**Other approaches and when to use them:**

| Approach | When to use |
|---|---|
| Scroll + warning (default) | Most forms — safe contract, no content loss |
| Dynamic height (remove fixed height) | When flexible page length is acceptable; simplest |
| Hard character limit | When the PDF must fit exactly one page and content must be capped |
| Line count limit | Useful supplement to character limit; catches Enter-key abuse |

### Sizing the comment box
Size `min-height` to the *anticipated* content length, not the minimum. A short comments
field: `6em`. A full teacher feedback field: `9em`. A notes section for a long form: `12em`.

### Resetting a contenteditable field
Use `.textContent = ''` not `.value = ''` (which only works on form inputs).
Always call the overflow check function after reset so the warning clears.

---

## Numeric score / rating inputs

For scored forms, use `<input type="number">` with `min`, `max`, and inline validation:

```html
<input type="number" class="score-number" id="inputA"
       min="0" max="10" placeholder="—"
       oninput="onScoreInput('A')" onchange="onScoreInput('A')">
```

```css
.score-number {
  width: 46px;
  text-align: center;
  border: 1.5px solid var(--border);
  border-radius: 4px;
  padding: 3px 4px;
  font-size: 10pt;
  font-weight: 700;
  color: var(--dark-navy);
  background: #fff;
  outline: none;
}
.score-number.invalid { border-color: #991b2a; background: #fff0f0; }
```

Validation pattern — mark invalid visually, suppress total calculation while invalid:

```javascript
function onScoreInput(crit) {
  const input = document.getElementById(`input${crit}`);
  const val = parseInt(input.value.trim());
  if (isNaN(val) || val < 0 || val > 10) {
    input.classList.add('invalid');
    return;  // don't update total
  }
  input.classList.remove('invalid');
  updateTotal();
}
```

Hide validation messages in print:
```css
@media print { .validation-msg { display: none !important; } }
```

---

## Rubric-specific pattern: band highlighting synced to score input

When the form has scored criteria with descriptor bands (e.g. Not Shown / Below / At Standard),
the click-to-select and manual score input should stay in sync:

- Each descriptor cell carries `data-min`, `data-max`, `data-pre` attributes
- Clicking a cell: sets the score input to `data-pre` (lower bound of band), highlights cell
- Typing a score: highlights whichever band contains that value, clears highlight if out-of-range
- Clicking an already-selected cell toggles it off and clears the input

```html
<td class="selectable"
    data-crit="A" data-min="6" data-max="7" data-pre="6"
    onclick="selectCell(this)">Descriptor text here.</td>
```

```javascript
function selectCell(cell) {
  const crit = cell.dataset.crit;
  const pre  = parseInt(cell.dataset.pre);
  const input = document.getElementById(`input${crit}`);
  const alreadySelected = cell.classList.contains('selected');

  document.querySelectorAll(`[data-crit="${crit}"].selectable`)
    .forEach(el => el.classList.remove('selected'));

  if (alreadySelected) {
    input.value = '';
    updateHint(crit, null);
  } else {
    cell.classList.add('selected');
    input.value = pre;
    updateHint(crit, pre);
  }
  updateTotal();
}

function highlightBand(crit, score) {
  document.querySelectorAll(`[data-crit="${crit}"].selectable`).forEach(cell => {
    const min = parseInt(cell.dataset.min);
    const max = parseInt(cell.dataset.max);
    cell.classList.toggle('selected', score !== null && score >= min && score <= max);
  });
}
```

Selected cell print style — use a solid background that survives PDF rendering:
```css
@media print {
  .rubric-table tr.desc-row td.selected {
    background: #c5d9f2 !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
```

---

## Print CSS — the decisions that matter

### Colours and backgrounds must be forced
Browsers suppress background colours in print by default. Force them with:
```css
@media print {
  .element-with-bg {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
```
Apply to: coloured table headers, alternating row shading, selected/highlighted cells,
any element where background colour carries meaning.

### Page breaks — keep tables together
Use both the legacy and modern property for maximum compatibility:
```css
@media print {
  .rubric-table,
  .footer-table {
    page-break-inside: avoid;
    break-inside: avoid;
  }
  /* Prevent footer/comments table orphaning on its own page */
  .footer-table {
    page-break-before: avoid;
    break-before: avoid;
  }
}
```

`avoid` works in Chrome and Edge for elements that fit within a single page.
If a table is taller than one page, `avoid` will be ignored — this is expected behaviour.

### Page margins
`10mm` all sides is the practical minimum for A4 in Chrome/Edge that keeps headers and
footers clear and allows content to breathe:
```css
@page { margin: 10mm 10mm 10mm 10mm; }
```

### Running headers
A small right-aligned metadata line at the top of the page (document title, subject,
date) helps when the PDF is printed and separated from other documents:
```html
<div class="running-header">Subject | Year Level | Form Name | Date</div>
```
```css
.running-header {
  font-size: 7.5pt; color: #666;
  text-align: right;
  padding: 6px 16px 4px;
  border-bottom: 1px solid #ccc;
}
```

### Remove interactive chrome from print
```css
@media print {
  .toolbar { display: none; }           /* Print/Reset buttons */
  .star-btn { border-color: #aaa; }     /* Visual toggle buttons */
}
```

### Avoid orphaned page footers
If a footer line is the only thing on the last page, remove it — the total/score is
already visible in the content above it. Don't add redundant summary footers.

---

## Toolbar (screen only)

Always include a Print button and a Reset button in a toolbar div that is hidden in print:

```html
<div class="toolbar">
  <button class="toolbar-btn btn-print" onclick="window.print()">🖨 Print / Export to PDF</button>
  <button class="toolbar-btn btn-reset" onclick="resetForm()">↺ Reset Form</button>
  <span class="toolbar-hint">Brief usage instruction here.</span>
</div>
```

The Reset function must handle `contenteditable` divs (`.textContent = ''`) as well as
regular inputs (`.value = ''`).

---

## Table layout

Use `table-layout: fixed` with explicit `<colgroup>` column widths for rubric-style tables.
This prevents columns from reflowing unpredictably when text lengths vary:

```html
<colgroup>
  <col style="width: 14%">     <!-- label column -->
  <col style="width: 14.4%">   <!-- repeated for each band column -->
  ...
</colgroup>
```

Cell text at `7.8pt` / `line-height: 1.35` is readable and compact enough for dense rubric
content. Don't go below `7pt` for descriptor text.

---

## Workflow for a new form task

1. **Read the source document** (upload, PDF, image, or description) before writing any code
2. **Identify field types**: short text, multi-line text, numeric scores, toggles, checkboxes
3. **Agree structure** with the user before building — column layout, sections, field sizing
4. **Apply the patterns above** for each field type
5. **Size comment boxes** to anticipated content — ask the user if unclear ("1–2 sentences" vs "full paragraph")
6. **Test print output** by asking the user to try Print → Save as PDF in Chrome and share the result
7. **Iterate on page breaks** if content splits badly — tighten padding before forcing breaks

---

## Reference implementations

`Module_3_Rubric_Digital.html` — Year 10 Data Analytics marking rubric
- Three scored criteria, each with six band columns
- Click-to-select band + manual numeric score input, kept in sync
- Auto-summing total in header badge and footer cell
- contenteditable teacher comments box
- Prints to 2–3 pages in Chrome with correct breaks and background colours preserved

`ccg-form.html` — General CCG data entry form
- Short text, date, number, radio (single-select), checkbox (multi-select), and contenteditable fields
- Scroll + overflow warning pattern on the description box
- Confirmed reset that clears all field types including contenteditable and dismisses the warning
- Prints to one A4 page in Chrome with full description content preserved
