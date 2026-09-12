# Research and classification

## Discovery by site type

Begin with the homepage, visible navigation/footer, sitemap and brand/about/contact pages. Follow linked product, service, collection, press-kit, editorial and support pages. Include visible downloadable brand/media kits where permitted. Service businesses may have no products: use case-study, service and campaign materials without fabricating a catalogue.

For a Shopify storefront, public product JSON and sitemaps can accelerate inventory. Check that each response is actually successful JSON; follow pagination until the end and compare unique product URLs with the sitemap. Do not assume a 250-item response is the whole catalogue. Collection names in navigation are not proof of product membership. Capture product URLs/IDs within each collection across its pagination or use a public membership endpoint when available. Store membership source URLs with the collection record. Treat archived collection/page URLs as potentially historical.

For other platforms, use their public page structure, rendered product/collection grids, structured data and authorised public feeds. The schema is platform-neutral. Do not scan private APIs, account areas, signed-in customer information or unrelated domains.

Prioritise brand identity and core pages before large catalogues. Continue in batches for large sites. A tool's page, time or file-size limit is a coverage limit: record it and the remaining known queue. If scale materially changes cost, obtain the host-required approval before incurring it; do not silently purchase credits.

## Assets

Inspect actual images and identify purpose from their placement and context. Classify logos, favicon/monogram, product images, collection artwork, campaign creative, lifestyle photography, icons, video and other brand materials. Product detail shots and model images still belong to that product; a lifestyle copy may also be useful if explicitly mapped. Keep customer-review media and third-party marks distinguishable and include only when permitted.

Do not count every responsive URL as a separate creative. Use content hashes for exact duplicates. Keep meaningful variants such as light/dark logos, mobile/desktop artwork and different angles. Same filename does not imply same content. Conversely, identical bytes can serve several products/collections; retain those relationships.

Actual SVG files can contain scripts or external resources. Preserve them as downloads but do not inject source markup directly into the HTML index. Validate that font files are fonts and video files are not error pages. Encrypted streaming, video platforms and permission-gated assets may only support source links; record those gaps.

## Fonts and colour

Use source CSS to identify declared families and weights, and computed styles on representative headings/body/buttons to establish use. Record both. A Helvetica/Arial/system-ui stack is platform-dependent; do not describe all fallback families as proprietary brand fonts. A file called 'logo-vector.png' remains raster. Do not identify a logo or baked-in headline font by visual guess alone. Separate official downloadable font releases from the exact web-font revision and include licences where available.

Prefer explicit CSS colour values over pixel sampling for the interface. Label sampled colours with their source image and estimated status. Separate primary identity colours, functional interface colours and product colourways. No invented Pantone or official CMYK values. The palette should reflect the actual brand, not a generic monochrome template.

## Copy and claims

Record the role and summary of every material page: brand story, hero, category, product detail, help centre, promotions and legal policies. Do not reproduce an entire third-party site's prose by default. Use source-linked summaries and limited excerpts. User-owned/supplied copy can be included when authorised. Tag such text with provenance and keep third-party reviews separate.

For stats, retain value, unit, period, locale, exact source and evidence status. Distinguish claimed rankings/ratings from independently audited facts. Reconcile conflicting ratings, delivery thresholds, promotions and date-sensitive policies; report the conflict if unresolved. Do not build reusable legal or certification claims from unverified source prose.

## Failure and completion

Blocked pages, bot challenges, empty JS widgets, oversized media, missing press kits, unverified fonts and inaccessible products are missing data, not evidence that the brand has no such material. Record the source, attempt status and impact. Do not bypass access restrictions. A completed kit may contain documented gaps, but cannot claim exhaustive retrieval when gaps remain.
