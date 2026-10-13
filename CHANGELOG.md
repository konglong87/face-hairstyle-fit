# Changelog

## 0.1.0 — Experimental preview

Initial preview; the GitHub release is prepared as a draft, not a stable release.

### Added

- Image-capable Agent Skill for personal-style exploration and coordinated hair, optional makeup, and outfits.
- Five style families, three expressions (Korean, Japanese, New Chinese), and three mixed recipes.
- Seven anchored styling dimensions, with no attractiveness scores or calibrated probabilities.
- Explicit photo roles and `ready` / `provisional` / `needs_input` report states.
- Catalog and report contracts, a local CLI, and escaped, photo-free static HTML reports.
- Contribution guidance, privacy-aware issue forms, support and security policies, and a PR checklist.

### Fixed

- Restore the unknown-photo-role constant used by report validation.
- Keep user-photo reports provisional while supported photo/preference issues remain unresolved.
- Align New Chinese expression support across the catalog, Skill, tests, and documentation.

### Validation and limits

- Contract tests and the three-image manual local replay are documented in the repository.
- The image replay checks workflow behavior, not model accuracy, independent evaluation, or a scientific style taxonomy.
- No real face images, individual consultation reports, credentials, or model weights are included in the repository or release assets.
- Visual reasoning needs an image-capable host Agent; the CLI does not analyze photos.
