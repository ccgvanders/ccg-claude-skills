# CCG Claude Skills

A collection of Claude skills developed at Christian College Geelong for use by staff working with Claude (claude.ai).

Skills are reusable instruction sets that guide Claude to produce better, more consistent output for specific tasks. Each skill lives in its own folder and contains a `SKILL.md` file that Claude reads before starting the relevant task.

---

## What is a skill?

When you ask Claude to do something — create a form, build a document — it can read a skill file first that tells it exactly how to approach that task for our context: which tools to use, which patterns work, what to avoid, and why. This means you get consistent, high-quality output without having to re-explain requirements every time.

---

## Skills in this repo

| Skill | What it's for |
|---|---|
| [html-print-form](./html-print-form/) | Build structured HTML forms that fill in on screen and export cleanly to PDF |
| [fillable-pdf](./fillable-pdf/) | Create fillable PDF forms with working AcroForm fields (text, checkboxes, radio buttons) |

---

## How to add a skill to your Claude

> **Note on plan requirements:** The Skills upload feature in Claude.ai may require a paid (Pro) subscription. If you don't see the Skills option in Settings, check whether your plan includes it before proceeding. Contact the Director of Digital Learning if you're unsure which plan you have.

### Permanent install (recommended)

This adds the skill to your Claude account so it loads automatically whenever you do a relevant task — no need to do anything each session.

1. Download the skill folder from this repo (e.g. `html-print-form/`)
2. Zip the folder so the folder itself is at the root of the zip file
3. In Claude, go to **Settings → Customize → Skills → Upload**
4. Upload the zip file
5. Done — Claude will detect and load the skill automatically from now on

### One-off use (no account required)

If you just want to try a skill once, or your plan doesn't include Skills upload:

1. Open the `SKILL.md` file for the skill you want (click it in GitHub, then click **Raw**)
2. Copy the full contents
3. Paste it at the start of a Claude conversation with the message: *"Use this as your skill for this task"*
4. Then ask for what you need as normal

This works for any Claude plan but only applies to that conversation.

---

## How to use a skill once installed

You don't need to do anything special — Claude recognises when a task matches a skill and loads it automatically. For example:

- *"Build me an HTML form with fields for name, date, and description that prints to PDF"* → loads `html-print-form`
- *"Create a fillable PDF registration form"* → loads `fillable-pdf`

---

## Contributing

If you develop a skill that works well for a CCG task, add it here:

1. Create a new folder with a short descriptive name (e.g. `rubric-marking`)
2. Add a `SKILL.md` file following the format of existing skills
3. Optionally include reference files or example outputs in the same folder
4. Update the skills table in this README

---

## Questions

Contact the Director of Digital Learning.
