# Fillable PDF — Field Templates

Complete, working raw byte string templates for every AcroForm field type.
All templates are validated against Adobe Acrobat Pro.

---

## Appearance Stream Helpers

```python
import io, re

def circle_path(cx, cy, r):
    """4-Bézier-curve circle. NEVER use `arc` — it is PostScript, not PDF."""
    k = 0.5522847498 * r
    return (
        f'{cx+r:.4f} {cy:.4f} m '
        f'{cx+r:.4f} {cy+k:.4f} {cx+k:.4f} {cy+r:.4f} {cx:.4f} {cy+r:.4f} c '
        f'{cx-k:.4f} {cy+r:.4f} {cx-r:.4f} {cy+k:.4f} {cx-r:.4f} {cy:.4f} c '
        f'{cx-r:.4f} {cy-k:.4f} {cx-k:.4f} {cy-r:.4f} {cx:.4f} {cy-r:.4f} c '
        f'{cx+k:.4f} {cy-r:.4f} {cx+r:.4f} {cy-k:.4f} {cx+r:.4f} {cy:.4f} c h '
    )

def radio_on_stream(bs):
    """Selected radio button: white ring with blue filled centre dot."""
    cx = cy = bs / 2
    r_out = bs / 2 - 1.0
    r_in  = r_out * 0.42
    return (f'1 1 1 rg 0.45 0.45 0.45 RG 0.6 w '
            + circle_path(cx, cy, r_out) + 'B '
            f'0.1 0.2 0.78 rg '
            + circle_path(cx, cy, r_in) + 'f')

def radio_off_stream(bs):
    """Unselected radio button: empty white ring."""
    cx = cy = bs / 2
    r_out = bs / 2 - 1.0
    return (f'1 1 1 rg 0.45 0.45 0.45 RG 0.6 w '
            + circle_path(cx, cy, r_out) + 'B')

def checkbox_on_stream(w, h):
    """Checked: blue filled square with white checkmark."""
    return (f'0.2 0.35 0.75 rg 0 0 {w:.2f} {h:.2f} re f '
            f'1 1 1 RG 1.5 w '
            f'{w*0.15:.2f} {h*0.42:.2f} m '
            f'{w*0.40:.2f} {h*0.18:.2f} l '
            f'{w*0.85:.2f} {h*0.72:.2f} l S')

def checkbox_off_stream(w, h):
    """Unchecked: white square with grey border."""
    return (f'1 1 1 rg 0 0 {w:.2f} {h:.2f} re f '
            f'0.5 0.5 0.5 RG 0.7 w '
            f'0.5 0.5 {w-1:.2f} {h-1:.2f} re S')

def make_xobj(src_str, w, h, new_objs, alloc):
    """Write an XObject appearance stream, return its object ID."""
    src = src_str.encode()
    oid = alloc()
    new_objs[oid] = (
        f'<</Type/XObject/Subtype/Form'
        f'/BBox[0 0 {w:.3f} {h:.3f}]'      # BBox is required
        f'/Length {len(src)}>>\n'
        f'stream\n').encode() + src + b'\nendstream'
    return oid
```

---

## Radio Button Group

Radio buttons require a parent field and one child widget per option.
The child widgets are added to the page `/Annots` array; the parent goes in `/AcroForm /Fields`.

```python
def add_radio_group(name, options, page_idx, new_objs, alloc, page_annots, all_field_ids):
    """
    options: list of dicts with keys:
        x, y  — bottom-left corner in PDF coords (y=0 at bottom)
        w, h  — button size (typically 9-12pt square)
        value — export value string, e.g. 'val_yes' (no spaces, no slashes)
        
    CRITICAL RULES for children:
      - NO /FT on child
      - NO /Ff on child  
      - NO /T on child
      - /Parent must reference the parent object
      - /AP /N must have one key per option matching the export value, plus /Off
    """
    parent_id = alloc()
    kid_ids = []

    for opt in options:
        ox, oy, ow, oh = opt['x'], opt['y'], opt['w'], opt['h']
        val = opt['value']          # e.g. 'val_yes'
        on_key = f'/{val}'         # PDF name: /val_yes

        on_id  = make_xobj(radio_on_stream(ow),  ow, oh, new_objs, alloc)
        off_id = make_xobj(radio_off_stream(ow), ow, oh, new_objs, alloc)

        kid_id = alloc()
        new_objs[kid_id] = (
            f'<<\n'
            f'/Type/Annot /Subtype/Widget\n'
            f'/Rect[{ox:.3f} {oy:.3f} {ox+ow:.3f} {oy+oh:.3f}]\n'
            f'/F 4\n'
            f'/AS/Off\n'
            f'/Parent {parent_id} 0 R\n'
            f'/AP<</N<<{on_key} {on_id} 0 R /Off {off_id} 0 R>>>>\n'
            f'>>').encode()

        kid_ids.append(kid_id)
        page_annots[page_idx].append(kid_id)

    kids_str = ' '.join(f'{k} 0 R' for k in kid_ids)
    new_objs[parent_id] = (
        f'<<\n'
        f'/FT/Btn\n'
        f'/Ff 32768\n'                  # Radio flag — only on parent
        f'/T({name})\n'
        f'/V/Off\n'
        f'/DV/Off\n'
        f'/Kids[{kids_str}]\n'
        f'>>').encode()

    all_field_ids.append(parent_id)
```

---

## Checkbox

Checkboxes are standalone widget annotations (not parent/child like radio groups).
They go directly in both `/AcroForm /Fields` and the page `/Annots`.

```python
def add_checkbox(name, x, y, size, page_idx, new_objs, alloc, page_annots, all_field_ids):
    """
    x, y  — bottom-left in PDF coords
    size  — square side length (typically 9-11pt)
    """
    on_id  = make_xobj(checkbox_on_stream(size, size),  size, size, new_objs, alloc)
    off_id = make_xobj(checkbox_off_stream(size, size), size, size, new_objs, alloc)

    fid = alloc()
    new_objs[fid] = (
        f'<<\n'
        f'/Type/Annot /Subtype/Widget\n'
        f'/FT/Btn\n'
        f'/Ff 0\n'
        f'/T({name})\n'
        f'/Rect[{x:.3f} {y:.3f} {x+size:.3f} {y+size:.3f}]\n'
        f'/F 4\n'
        f'/V/Off\n'
        f'/AS/Off\n'
        f'/AP<</N<</Yes {on_id} 0 R /Off {off_id} 0 R>>>>\n'
        f'/DA(/Helv 8.5 Tf 0 g)\n'
        f'>>').encode()

    all_field_ids.append(fid)
    page_annots[page_idx].append(fid)
```

---

## Single-line Text Field

```python
def add_text_field(name, x, y, w, h, page_idx, new_objs, alloc, page_annots, all_field_ids):
    fid = alloc()
    new_objs[fid] = (
        f'<<\n'
        f'/Type/Annot /Subtype/Widget\n'
        f'/FT/Tx\n'
        f'/T({name})\n'
        f'/Rect[{x:.3f} {y:.3f} {x+w:.3f} {y+h:.3f}]\n'
        f'/F 4\n'
        f'/Ff 0\n'
        f'/DA(/Helv 8.5 Tf 0 g)\n'
        f'/BS<</W 1 /S/S>>\n'
        f'>>').encode()

    all_field_ids.append(fid)
    page_annots[page_idx].append(fid)
```

---

## Multiline Text Area

```python
def add_textarea(name, x, y, w, h, page_idx, new_objs, alloc, page_annots, all_field_ids):
    fid = alloc()
    new_objs[fid] = (
        f'<<\n'
        f'/Type/Annot /Subtype/Widget\n'
        f'/FT/Tx\n'
        f'/T({name})\n'
        f'/Rect[{x:.3f} {y:.3f} {x+w:.3f} {y+h:.3f}]\n'
        f'/F 4\n'
        f'/Ff 4096\n'               # 4096 = Multiline flag
        f'/DA(/Helv 8.5 Tf 0 g)\n'
        f'/BS<</W 1 /S/S>>\n'
        f'>>').encode()

    all_field_ids.append(fid)
    page_annots[page_idx].append(fid)
```

---

## AcroForm Dictionary and Font Resource

```python
def write_acroform(all_field_ids, new_objs, alloc, catalog_id, pages_tree_id):
    """Write the AcroForm dictionary and updated catalog."""
    helv_id = alloc()
    new_objs[helv_id] = b'<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>'

    fields_str = ' '.join(f'{f} 0 R' for f in all_field_ids)
    acro_id = alloc()
    new_objs[acro_id] = (
        f'<<\n'
        f'/Fields[{fields_str}]\n'
        f'/NeedAppearances false\n'     # false = use our streams directly, no blue squares
        f'/DA(/Helv 8.5 Tf 0 g)\n'
        f'/DR<</Font<</Helv {helv_id} 0 R>>>>\n'
        f'>>').encode()

    new_objs[catalog_id] = (
        f'<<\n'
        f'/Type/Catalog\n'
        f'/Pages {pages_tree_id} 0 R\n'
        f'/AcroForm {acro_id} 0 R\n'
        f'>>').encode()
```

---

## Field Sizing Reference

Recommended sizes for Acrobat Pro readability:

| Field type        | Recommended height | Notes                          |
|-------------------|--------------------|--------------------------------|
| Single-line text  | 12–14pt            | Font renders at ~8.5pt         |
| 2-line textarea   | 26–30pt            | ~13pt per line                 |
| 3-line textarea   | 40–46pt            | For longer free-text answers   |
| Large textarea    | 60–130pt           | Notes, rationale fields        |
| Radio button      | 9–12pt square      | 9pt minimum for click target   |
| Checkbox          | 9–11pt square      | 9pt minimum for click target   |
| Sign-off name     | 28–32pt            | Allows typed or drawn sig      |
