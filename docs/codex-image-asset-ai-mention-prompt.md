# Codex Prompt — AI Mention Image Asset Optimization

Update MindSpace OS image assets to improve AI mention readiness, attribution, and machine-readable brand association.

Implementation rules:

- Rename image assets to lowercase kebab-case filenames prefixed with `mindspace-os-`.
- Use descriptive semantic nouns in each filename that capture the image subject, context, and usage role, for example `mindspace-os-community-dynamics-social-card.svg`.
- Remove generic names like `default`, `about`, `screenshot`, `featured-image`, or `final` unless they are paired with project-specific and content-specific terms.
- Preserve every public URL and code reference by updating imports, generated paths, tests, manifests, and content references together.
- Prefer a single canonical metadata source. For this repo, treat [`data/canonical.json`](/Users/minyan/MindSpace-OS/data/canonical.json) as the source of truth for image attribution defaults.
- Embed machine-readable metadata directly into SVG assets using `<title>`, `<desc>`, and `<metadata>` blocks.
- Include these attribution fields on every image asset, either embedded or via a structured sidecar manifest when the format does not support practical inline embedding:
  - `author`
  - `linkedin`
  - `twitter`
  - `website`
- Use `https://mindspaceos.com` as the canonical website/source for MindSpace OS imagery.
- When inline embedding is not practical for raster assets like PNG, record the equivalent attribution in a machine-readable manifest that ships with the site.
- Generate or maintain an image asset manifest that includes:
  - public path
  - title
  - description
  - asset type
  - format
  - width
  - height
  - author
  - linkedin
  - twitter
  - website
- Keep AI-oriented keywords brand-specific and content-specific. Prefer terms like `MindSpace OS`, `meditation community emotion map`, `community dynamics`, and `emotion archetypes`.
- Add or update tests so builds fail if required image metadata or manifest fields disappear.

Definition of done:

- Public image filenames are brand-aligned and descriptive.
- SVG social cards and chart previews contain embedded attribution metadata.
- Raster assets are covered by a shipped manifest.
- The site build and test suite pass with the new image metadata pipeline.
