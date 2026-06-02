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

Claude skills in the claude.ai interface are loaded from a file system attached to your account. To add a skill from this repo:

1. Open the `SKILL.md` file for the skill you want
2. Copy the full contents
3. In Claude, ask: *"Save this as a skill called `[skill-name]`"* and paste the content

Claude will store it and load it automatically whenever you ask for a relevant task.

> **Tip:** You can also just paste the skill content directly into a conversation and say *"use this skill for our session"* if you want a one-off use without saving it permanently.

---

## How to use a skill once added

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
