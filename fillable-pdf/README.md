# Fillable PDF Skill

Create fillable PDF forms with working AcroForm fields — text inputs, checkboxes, and radio buttons — that open and save correctly in Adobe Acrobat.

## When to use this

- The output must be a **native PDF** (not an HTML file exported to PDF)
- Fields need to be saveable in Acrobat or Adobe Reader
- The form has a fixed, precise layout that must not reflow
- Typical uses: official forms, documents that must match an existing PDF template

## How it compares to the HTML print form

| | HTML print form | Fillable PDF |
|---|---|---|
| Authoring complexity | Low | High |
| Update/iterate | Very easy (text file) | Requires re-running the script |
| Print fidelity | High | Exact |
| Fields saveable in Acrobat | No | Yes |
| Requires Python toolchain | No | Yes |

**Rule of thumb:** if the HTML print form can meet the requirement, use it — it's simpler to build and maintain. Use this skill when a native, saveable PDF is specifically required.

## Technical requirements

This skill uses a Python-based approach (ReportLab + pypdf). Claude will write and run the script in its code environment. No local Python installation is needed.

## Files

- `SKILL.md` — the skill itself; load this into Claude
