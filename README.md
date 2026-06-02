---
name: fillable-pdf
description: >
  Use this skill whenever the user wants to create a fillable PDF form — including any request
  involving AcroForm fields, PDF form fields, clickable checkboxes, radio buttons, text input
  fields, or a PDF that can be filled in and saved. Also triggers for requests to "build a form
  as a PDF", "make a PDF with fields", or "create a form document". ALWAYS read this skill before
  starting any fillable PDF task — it documents the only approach that produces working interactive
  fields in Adobe Acrobat, and contains critical gotchas that are not obvious and will waste
  significant time if missed.
---

# Fillable PDF Skill

## Overview

Creating fillable PDFs with working AcroForm fields (radio buttons, checkboxes, text fields)
requires a specific two-pass approach. Any shortcut — including relying entirely on pypdf's object
model — will produce fields that appear correct in code but fail silently in Acrobat.

**The only reliable approach:**
1. ReportLab renders the visual layout (colours, text, borders) → base PDF
2. Raw PDF byte strings are appended as an incremental update containing the AcroForm fields
3. pypdf is used only to read page object IDs for linking — never to construct field dictionaries

Read `references/approach.md` for the full rationale. Read `references/field-templates.md` for
copy-paste field construction code. Read `references/gotchas.md` for the critical failure modes.

---

## Workflow

### Step 1 — Collect field specifications during ReportLab layout

Use a global `SPECS` list. Each ReportLab Flowable that represents a form field calls
`c.absolutePosition(x, y)` during its `draw()` method to capture the absolute page coordinates,
then appends to `SPECS`.

```python
SPECS = []

def reg(name, ftype, page_idx, x, y, w, h, **kw):
    SPECS.append(dict(name=name, type=ftype, page=int(page_idx),
                      x=float(x), y=float(y), w=float(w), h=float(h), **kw))
```

Inside each field flowable's `draw()`:
```python
ax, ay = c.absolutePosition(field_x, field_y)
reg(self.fname, 'text', c._pageNumber - 1, ax, ay, field_w, field_h)
```

`c._pageNumber` is 1-based, so subtract 1 for 0-based page index.

### Step 2 — Read the visual PDF to get page object IDs

```python
from pypdf import PdfReader

r = PdfReader(visual_path)
page_obj_ids    = [pg.indirect_reference.idnum for pg in r.pages]
pages_tree_id   = r.trailer['/Root']['/Pages'].indirect_reference.idnum
catalog_id      = r.trailer['/Root'].indirect_reference.idnum
page_parent_ids = [pg.get('/Parent').indirect_reference.idnum for pg in r.pages]

import re
with open(visual_path, 'rb') as f:
    base_bytes = f.read()
max_existing = max(int(m) for m in re.findall(rb'(\d+) 0 obj', base_bytes))
nid = [max_existing + 1]
new_objs = {}  # id -> bytes

def alloc():
    i = nid[0]; nid[0] += 1; return i
```

### Step 3 — Write all AcroForm objects as raw bytes

See `references/field-templates.md` for the exact byte string patterns for each field type.
Key rule: **never construct field dictionaries using pypdf's DictionaryObject** — write them
as raw encoded byte strings assigned directly to `new_objs[oid]`.

### Step 4 — Write revised page objects with /Annots

For each page that has fields, write a new version of the page object (same object ID as the
original, which the incremental update will override) that includes `/Annots`:

```python
for pg_i, page in enumerate(r.pages):
    aids = page_annots.get(pg_i, [])
    if not aids:
        continue
    orig_id   = page_obj_ids[pg_i]
    par_id    = page_parent_ids[pg_i]
    annots_str = ' '.join(f'{a} 0 R' for a in aids)

    # Reconstruct contents reference
    contents = page.get('/Contents')
    if hasattr(contents, 'indirect_reference') and contents.indirect_reference:
        cont_str = f'{contents.indirect_reference.idnum} 0 R'
    else:
        parts = [f'{c2.indirect_reference.idnum} 0 R'
                 for c2 in contents
                 if hasattr(c2, 'indirect_reference') and c2.indirect_reference]
        cont_str = ' '.join(parts)

    # Reconstruct resources reference
    res = page.get('/Resources')
    if hasattr(res, 'indirect_reference') and res.indirect_reference:
        res_str = f'/Resources {res.indirect_reference.idnum} 0 R'
    else:
        res_obj = res.get_object() if hasattr(res, 'get_object') else res
        fd = res_obj.get('/Font', {})
        if hasattr(fd, 'get_object'): fd = fd.get_object()
        frefs = []
        for fk in fd:
            fv = fd[fk]; fo = fv.get_object() if hasattr(fv, 'get_object') else fv
            if hasattr(fo, 'indirect_reference') and fo.indirect_reference:
                frefs.append(f'{fk} {fo.indirect_reference.idnum} 0 R')
        res_str = f'/Resources<</Font<<{" ".join(frefs)}>>\n>>'

    body = (f'<<\n/Type/Page\n/Parent {par_id} 0 R\n'
            f'/MediaBox[0 0 595.276 841.890]\n'
            f'/Contents {cont_str}\n'
            f'{res_str}\n'
            f'/Annots[{annots_str}]\n>>')
    new_objs[orig_id] = body.encode()
```

### Step 5 — Write AcroForm, updated catalog, write incremental update

```python
helv_id = alloc()
new_objs[helv_id] = b'<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>'

fields_str = ' '.join(f'{f} 0 R' for f in all_field_ids)
acro_id = alloc()
new_objs[acro_id] = (
    f'<<\n/Fields[{fields_str}]\n/NeedAppearances false\n'
    f'/DA(/Helv 8.5 Tf 0 g)\n'
    f'/DR<</Font<</Helv {helv_id} 0 R>>>>\n>>').encode()

new_objs[catalog_id] = (
    f'<<\n/Type/Catalog\n/Pages {pages_tree_id} 0 R\n'
    f'/AcroForm {acro_id} 0 R\n>>').encode()

# Write base bytes + incremental update
out = io.BytesIO()
out.write(base_bytes)
if not base_bytes.endswith(b'\n'):
    out.write(b'\n')

offsets = {}
for oid in sorted(new_objs.keys()):
    offsets[oid] = out.tell()
    out.write(f'{oid} 0 obj\n'.encode())
    out.write(new_objs[oid])
    out.write(b'\nendobj\n')

# Write xref as contiguous subsections
xref_pos = out.tell()
sorted_ids = sorted(offsets.keys())
runs = []
if sorted_ids:
    rs = sorted_ids[0]; run = [sorted_ids[0]]
    for i in range(1, len(sorted_ids)):
        if sorted_ids[i] == sorted_ids[i-1] + 1:
            run.append(sorted_ids[i])
        else:
            runs.append((rs, run)); rs = sorted_ids[i]; run = [sorted_ids[i]]
    runs.append((rs, run))

out.write(b'xref\n')
for rs, run in runs:
    out.write(f'{rs} {len(run)}\n'.encode())
    for oid in run:
        out.write(f'{offsets[oid]:010d} 00000 n \n'.encode())

prev = int(re.search(rb'startxref\r?\n(\d+)', base_bytes).group(1))
out.write(
    f'trailer\n<</Size {nid[0]}/Root {catalog_id} 0 R/Prev {prev}>>\n'
    f'startxref\n{xref_pos}\n%%EOF\n'.encode())

with open(output_path, 'wb') as f:
    f.write(out.getvalue())
```

---

## Verification

After building, verify with pdftk:
```bash
pdftk output.pdf dump_data_fields
```
Should list all fields with correct `FieldType`, `FieldName`, and `FieldStateOption` entries
for radio groups.

Also verify no invalid operators remain in appearance streams:
```python
import re
with open(output_path, 'rb') as f: raw = f.read()
streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', raw, re.DOTALL)
has_arc = any(b' arc ' in s or s.endswith(b' arc') for s in streams)
assert not has_arc, "arc operator found — appearance streams will fail in Acrobat"
```

---

## Reference files

- `references/gotchas.md` — Critical failure modes. Read before debugging any field issue.
- `references/field-templates.md` — Complete raw byte string templates for all field types.
- `references/approach.md` — Rationale for why pypdf's object model cannot be used directly.
