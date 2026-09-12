# Portable input schema

The agent writes two JSON files after research. Neither helper crawls the web. Downloads live in the same staging folder or its descendants; `local_path` is relative to the manifest's folder. Do not include secrets, customer data or raw tool session exports. Use UTF-8.

## manifest.json

```json
{
  "brand": {
    "name": "Example Brand",
    "url": "https://example.com",
    "captured_at": "2026-09-12",
    "locale": "en-AU",
    "currency": "AUD"
  },
  "products": [
    {"id": "p1", "name": "Cotton Tee", "url": "https://example.com/products/tee", "summary": "Original factual summary.", "price": 45, "currency": "AUD", "variants": []}
  ],
  "collections": [
    {"id": "c1", "name": "Essentials", "url": "https://example.com/collections/essentials", "product_ids": ["p1"], "membership_sources": ["https://example.com/collections/essentials"]}
  ],
  "assets": [
    {"id": "a1", "kind": "logo", "local_path": "downloads/wordmark.png", "filename": "wordmark.png", "url": "https://example.com/media/wordmark.png", "source_pages": ["https://example.com"], "rights": "Brand reference; original rights retained"},
    {"id": "a2", "kind": "product", "local_path": "downloads/tee.jpg", "filename": "tee.jpg", "url": "https://example.com/media/tee.jpg", "product_ids": ["p1"], "source_pages": ["https://example.com/products/tee"]}
  ],
  "colors": [
    {"name": "Ink", "hex": "#151515", "role": "Primary text", "evidence": "observed CSS", "source_url": "https://example.com"}
  ],
  "fonts": [
    {"family": "Example Sans", "weights": [400,600], "role": "Body and navigation", "status": "declared and rendered", "source_url": "https://example.com", "download_status": "Licence not verified; link only"}
  ],
  "pages": [
    {"url": "https://example.com", "title": "Homepage", "status": "captured", "copy_summary": "Original summary of purpose and messaging.", "evidence": "observed"}
  ],
  "coverage": {"scope": "Public brand and catalogue pages", "pages_discovered": 1, "pages_attempted": 1, "pages_captured": 1, "pagination_complete": true, "unvisited_urls": []},
  "missing": ["Approved vector master not found"],
  "conflicts": []
}
```

Required: `brand` fields name/url/captured_at; unique nonempty string IDs in each array; asset kind/local_path/url. All asset product and collection references must exist. Use the actual capture date and observed locale/currency; do not copy the example values.

Asset kinds: `logo`, `font`, `font-license`, `product`, `collection`, `campaign`, `lifestyle`, `icon`, `video`, `other`. For collection artwork set `collection_ids`. For campaigns add `campaign`. A product's membership is recorded in each collection's `product_ids`; the organiser copies its assets into each collection's `Products/` folder. Missing membership goes into the product directory only. Include `source_pages`, rights/licensing details and original filenames whenever available. Use `font-license` for downloaded licence text.

Supported file types: PNG/JPEG/WebP/GIF/TIFF/AVIF/SVG, WOFF/WOFF2/TTF/OTF, MP4/MOV/WebM, PDF/AI/EPS, and UTF-8 TXT/MD/JSON. Unsupported or invalid files are recorded as failures. This is signature validation, not a malware scan; inspect assets with the host's safe tools and verify font names with font tooling when available. Do not rename unsupported bytes to an accepted extension.

Store additional factual product fields (materials, sizes, prices, variant counts, image roles, care) in product records. They are preserved in `product.json`. A `summary` lets the PDF show an original digest of these facts. The helper preserves arbitrary non-sensitive fields in the manifest, so authorised copy may be placed in page records with a clear `copy_status` and provenance. Do not place full external copy there by default.

## report.json

```json
{
  "title": "Example Brand - Brand Reference",
  "cover_asset_id": "a1",
  "sections": [
    {
      "title": "Brand identity",
      "evidence": "observed + inferred (labelled in text)",
      "paragraphs": ["Write an original evidence-based overview here."],
      "rows": [["Item", "Finding"], ["Positioning", "Explain what is observed and what is inferred."]],
      "asset_ids": ["a1"],
      "sources": ["https://example.com"]
    }
  ]
}
```

The example demonstrates structure, not final content. Replace it with real research. Paragraphs and table cells are plain text, not HTML. Source links are HTTP(S). Tables have 1-4 columns and a header row; keep individual rows short enough to fit on a page. Sections flow across pages and begin on new pages. The renderer appends palette, products, collections, coverage and image contact sheets automatically; avoid repeating large inventories in authored sections.

Write sections for scope, identity/history, sourced stats, logos/application, fonts, design/layout, photography/pattern, voice/copy map and dated service/offer details. Add other sections when evidenced (e.g. packaging). Link evidence, label proposed rules, explain gaps. No invented official guidelines, unsupported stats or fabricated copy.

## Dependencies and verification

`brandkit.py` needs only Python 3.10+. `render_guidelines.py` needs ReportLab and Pillow. Use the available runtime or a local virtual environment. For languages outside Windows-1252, pass a Unicode TTF with the needed glyphs using `--font`; never silently replace a brand name with broken characters. Actual brand-font specimens can be shown using appropriate font tooling when verified and permitted.

After `organize`, read the returned run path and `13-Sources/coverage.json`. After `render_guidelines`, render the PDF using Poppler or another available PDF renderer and inspect representative pages, every distinct layout and any dense tables. Recheck all affected pages after corrections. Review `render_issues` as well as download failures. `package` refuses to overwrite an existing ZIP and requires the PDF and Markdown to exist; existence does not replace visual QA.
