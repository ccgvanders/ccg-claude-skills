# Fillable PDF — Approach Rationale

## Why not use pypdf's object model for field construction?

pypdf is excellent for reading PDFs and copying existing objects. However, when used to
*construct* AcroForm field dictionaries (via DictionaryObject, NameObject, etc.) and write
them to a new file, it applies normalisation and encoding transformations that silently
violate AcroForm spec requirements in ways that appear correct in Python but break in Acrobat.

Specifically:
- Radio button child widgets receive `/FT` and `/Ff` entries that should only be on the parent
- Appearance stream references get restructured in ways Acrobat rejects
- The `/AS` (appearance state) handling is incorrect for radio groups

These bugs were confirmed through extensive debugging. The behaviour is not fixable by
setting values differently — the transformation happens at write time. The only reliable
approach is to bypass pypdf's write path entirely for AcroForm objects.

## Why not use fpdf2, reportlab's AcroForm, or other libraries?

- **fpdf2**: Does not support radio buttons or checkboxes as of v2.8
- **ReportLab's AcroForm**: The platypus form layer has limited field type support and
  inconsistent Acrobat compatibility, particularly for radio groups
- **pdfrw**: Works for reading but has similar write-path issues to pypdf for AcroForm

## Why incremental update rather than a fresh PDF?

ReportLab produces high-quality visual PDFs with correct font embedding, colour spaces,
and compressed content streams. Reproducing all of this from scratch in raw bytes would
require reimplementing significant rendering logic. The incremental update approach lets
ReportLab handle everything it's good at, then appends the AcroForm layer as a separate
concern without touching the visual content.

PDF's incremental update mechanism (appending new/revised objects after the original
byte stream, with a new xref section and trailer pointing back to the previous one) is
specifically designed for exactly this use case — adding annotations and form fields to
an existing document.

## Why two passes (visual first, then fields)?

ReportLab's layout engine determines the final position of every element only during the
build pass. The `absolutePosition()` call inside a Flowable's `draw()` method returns the
correct page coordinates only at that point. There is no way to know where an element will
land before ReportLab places it, so we must let ReportLab build first, collect coordinates
during the draw pass, then write the fields referencing those coordinates.

## Why NeedAppearances false?

With `NeedAppearances true`, Acrobat ignores existing `/AP` streams on first render and
regenerates them using its own default appearance (solid blue squares for buttons). This
means fields look broken until the user interacts with them, even though the underlying
structure is correct. Setting it to `false` tells Acrobat to trust and use the appearance
streams we provide, which renders correctly immediately on open.

## Tested environment

This approach was developed and validated against:
- Adobe Acrobat Pro (Windows, current version as of May 2026)
- pypdf 3.x
- ReportLab 4.x
- Python 3.12

The PDF output conforms to PDF 1.7 specification AcroForm requirements.

## Signature fields: AcroForm vs E-Sign vs PandaDoc

Three distinct mechanisms exist for signatures on PDFs, with different appropriate uses:

**AcroForm `/Sig` field** — cryptographic certificate-based signature embedded in the PDF
structure. Requires a digital ID configured in Acrobat. Not practical in most school/org
environments without IT setup. Avoid for internal documents; the field will appear but be
inert if certificate infrastructure is not in place.

**Acrobat E-Sign** — Adobe's overlay signature workflow, accessible via the left panel or
the E-Sign tab in Acrobat. Applies a signature image as a floating annotation. The "Save a
certified copy" option adds an audit trail. Does not require a predefined form field — works
on any saved PDF. Appropriate for internal records where a visual signature and basic
certification is sufficient. A plain text "Name / Signature" field with a guidance note is
the correct companion field design (see gotchas.md #8).

**PandaDoc** — CCG has a PandaDoc licence. Handles the full legally binding e-signature
workflow with audit trail, recipient tracking, and formal document certification. Appropriate
for external contracts, formal HR documents, and any context where a legally binding
signature is a genuine requirement. This is out of scope for AcroForm PDF work; flag it as
the right tool when the use case warrants it.
