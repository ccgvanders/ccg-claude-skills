# Fillable PDF — Critical Gotchas

These are the failure modes discovered through extensive debugging. Each one causes silent
failures in Acrobat that look correct in code but produce broken interactive fields.

---

## 1. `arc` IS NOT A PDF OPERATOR — most critical bug

**The failure:** Radio buttons and checkboxes appear as solid blue squares in Acrobat,
and clicking them activates the wrong field or has no effect.

**The cause:** `arc` and `arcto` are PostScript operators. PDF uses cubic Bézier curves
for all curved paths. If you write `arc` in an appearance stream (XObject), Acrobat silently
discards the entire stream, renders its own default blue square, and uses a broken hit zone
that doesn't align with the visual.

**The fix:** Use 4 cubic Bézier curves to approximate a circle:

```python
def circle_path(cx, cy, r):
    """Correct PDF circle — 4 Bézier curves. Never use arc/arcto."""
    k = 0.5522847498 * r   # magic constant for 90-degree arc approximation
    return (
        f'{cx+r:.4f} {cy:.4f} m '
        f'{cx+r:.4f} {cy+k:.4f} {cx+k:.4f} {cy+r:.4f} {cx:.4f} {cy+r:.4f} c '
        f'{cx-k:.4f} {cy+r:.4f} {cx-r:.4f} {cy+k:.4f} {cx-r:.4f} {cy:.4f} c '
        f'{cx-r:.4f} {cy-k:.4f} {cx-k:.4f} {cy-r:.4f} {cx:.4f} {cy-r:.4f} c '
        f'{cx+k:.4f} {cy-r:.4f} {cx+r:.4f} {cy-k:.4f} {cx+r:.4f} {cy:.4f} c h '
    )
```

**How to verify:** After building, check no appearance streams contain ` arc `:
```python
streams = re.findall(rb'stream\r?\n(.*?)\r?\nendstream', raw, re.DOTALL)
assert not any(b' arc ' in s for s in streams)
```

---

## 2. Radio button children must NOT have /FT or /Ff

**The failure:** Clicking one radio button activates a different one, often in a different
question group. The wrong button fills, or buttons flicker and revert.

**The cause:** Per the PDF spec, `/FT` (field type) and `/Ff` (field flags) belong only on
the parent field dictionary. When child widget annotations also carry these entries, Acrobat
treats each child as an independent standalone button rather than an option within a group,
breaking the mutual-exclusion logic.

**The fix:** Child radio widget dictionaries contain ONLY:
`/Type`, `/Subtype`, `/Rect`, `/F`, `/AS`, `/Parent`, `/AP`

Never add `/FT`, `/Ff`, `/T`, or `/DA` to children.

**What the parent has:** `/FT /Btn`, `/Ff 32768`, `/T (field_name)`, `/V /Off`, `/DV /Off`, `/Kids [...]`

---

## 3. pypdf's DictionaryObject silently mangles field structure

**The failure:** Fields look structurally correct when inspected in Python, but Acrobat
produces broken behaviour — wrong buttons selected, fields unclickable, appearance streams
ignored.

**The cause:** pypdf's intermediate object representation applies transformations and
normalisation when serialising to bytes that alter the field dictionaries in ways that
violate AcroForm spec requirements. This is not fixable by setting values differently —
the transformation happens at write time.

**The fix:** Write ALL AcroForm field dictionaries as raw encoded byte strings:
```python
new_objs[kid_id] = (
    f'<<\n/Type/Annot /Subtype/Widget\n'
    f'/Rect[{ox:.3f} {oy:.3f} {ox+ow:.3f} {oy+oh:.3f}]\n'
    f'/F 4 /AS/Off\n'
    f'/Parent {parent_id} 0 R\n'
    f'/AP<</N<</{val} {on_id} 0 R /Off {off_id} 0 R>>>>\n'
    f'>>').encode()
```

Use pypdf only for reading (page IDs, object IDs, raw bytes of existing objects).
Never use it to construct or write field objects.

---

## 4. NeedAppearances true causes blue squares before first click

**The failure:** All radio buttons and checkboxes render as solid blue squares until the
user clicks them, at which point Acrobat regenerates the appearance and shows the correct
visual.

**The cause:** With `/NeedAppearances true`, Acrobat ignores existing appearance streams
and regenerates them from scratch using its own defaults on first render — producing blue
squares for buttons.

**The fix:** Set `/NeedAppearances false`. Our appearance streams are complete and correct,
so Acrobat should use them directly.

---

## 5. Incremental update page parent IDs must be read from the actual file

**The failure:** pdftk reports "Index out of bounds" error and refuses to open the PDF.
pypdf reports 0 pages.

**The cause:** When writing revised page objects in the incremental update, the `/Parent`
reference must point to the correct page tree node ID read from the actual file — not
hardcoded. Different ReportLab versions produce different object ID layouts.

**The fix:** Always read at runtime:
```python
page_parent_ids = [pg.get('/Parent').indirect_reference.idnum for pg in r.pages]
pages_tree_id   = r.trailer['/Root']['/Pages'].indirect_reference.idnum
catalog_id      = r.trailer['/Root'].indirect_reference.idnum
```

---

## 6. absolutePosition in ReportLab flowables is reliable but has a quirk

`c.absolutePosition(local_x, local_y)` returns PDF coordinates (y=0 at page bottom).
This is correct for PDF field rects. However, it must be called during `draw()`, not
during `wrap()`. The page number `c._pageNumber` is 1-based — subtract 1 for 0-based
page index when registering specs.

---

## 7. Appearance stream XObjects need /BBox matching their size

Every appearance stream must include a `/BBox` matching the field dimensions:
```
<</Type/XObject/Subtype/Form/BBox[0 0 {w} {h}]/Length {n}>>
```
Without `/BBox`, Acrobat clips or ignores the stream content.

---

## 8. AcroForm `/Sig` fields require certificate infrastructure — use a text field instead for internal documents

**The failure:** A `/FT/Sig` field appears in the PDF and renders visually as a box, but
clicking it does nothing in Acrobat. The field is inert.

**The cause:** AcroForm digital signature fields (`/FT/Sig`) trigger a certificate-based
cryptographic signing workflow. This requires a properly configured digital ID certificate
in Acrobat — either a self-signed certificate the user has created, or one issued by a
certificate authority and installed in Acrobat's trust store. In typical school and
organisational environments (including CCG), this infrastructure is not set up by default,
so the field simply does not respond to clicks.

A secondary issue: including `/AP<</N<</Blank 0 R>>>>` as a placeholder appearance entry
on the sig field (referencing PDF object 0, the null object) can cause Acrobat to treat the
field as malformed. Omitting the `/AP` entry entirely is correct for `/Sig` fields — Acrobat
generates its own appearance when the user actually signs.

**What Acrobat offers instead:** When a `/Sig` field is present but inoperable, Acrobat
surfaces its own E-Sign tools (left panel "Add Signature", or the "E-Sign" tab). These apply
a signature image as a floating overlay on the document — not bound to the AcroForm field.
The E-Sign "Save a certified copy" option adds an audit trail and certifies the document
state, which provides useful integrity value for internal records even without a cryptographic
certificate.

**The recommended approach for internal documents:**

Use a plain text field labelled "Name / Signature" with a guidance note below it:

```
Type your name, or use Acrobat's E-Sign function to place a digital signature.
```

This gives the signer a clear choice: type their name for a simple record, or use
Acrobat's E-Sign overlay for a more formal appearance. The E-Sign certified copy workflow
remains available at any time on any saved PDF — it does not require a predefined field
location.

**CCG context:** For documents requiring a legally binding signature (external contracts,
formal HR documents, external agreements), CCG has a PandaDoc licence which handles the
full signature workflow including audit trail and is better suited to those contexts than
an AcroForm field. AcroForm fillable PDFs are appropriate for internal review and record
documents; PandaDoc is appropriate where formal legal signature is the requirement.
