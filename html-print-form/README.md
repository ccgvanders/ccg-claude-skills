# HTML Print Form Skill

Build structured HTML forms that work interactively on screen and export cleanly to PDF via the browser's Print → Save as PDF dialog.

## When to use this

- One person fills in the form and the **PDF document is the deliverable**
- Print fidelity is a hard requirement — layout must survive export
- You want something simpler to build and update than a fillable PDF
- Typical uses: incident reports, observation records, referral forms, moderation records, interview notes, self-assessment sheets

## How it compares to other tools

| Tool | Best for |
|---|---|
| **HTML print form** | Single user, structured input, PDF is the deliverable |
| **Microsoft Forms** | Collecting multiple responses, Power Automate routing |
| **Fillable PDF** | Fixed-layout forms needing Acrobat compatibility |
| **Word template** | Narrative documents, familiar editing |

## Reference implementation

`ccg-form.html` in this folder is a working example with: name, date, age, campus (radio), year levels (checkboxes), and description (scrollable with overflow warning). It demonstrates all the key patterns from the skill.

## Files

- `SKILL.md` — the skill itself; load this into Claude
- `ccg-form.html` — reference implementation / starter template
