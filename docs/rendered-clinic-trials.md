# Rendered clinic trial decks

The isolated trial adapter copies only the tracked synthetic English/Chinese drafts and synthetic ledger from `docs/evidence/clinic-source-trial/`, applies a consistent 16:9 Marp theme, renders real PDFs, rasterizes every page, and checks mechanical coverage. It does not generate or validate clinical claims and does not create fake PDFs when rendering is unavailable.

## Run

Use the normal Soak trial runner with a new output directory:

```powershell
python -m soak.trial examples/clinic-render.json --output runs/clinic-render-001
```

The adapter receives JSON on stdin from the trial runner. Commands use explicit generate/validate arguments and the isolated current directory. Validation compares the copied ledger with the approved tracked ledger. The successful manifest lists PDFs, styled Markdown, ledger, `render.json`, and each page PNG. Inspect those artifacts manually; `visual_review` remains `unverified`, and mechanical pass is not visual acceptance or a language-quality claim.

## Dependencies and limits

Requires Python, Node.js, a locally cached `@marp-team/marp-cli` JavaScript entry point, a browser usable by Marp (normally installed Chrome/Edge), Poppler `pdfinfo` and `pdftoppm` on PATH, and the repository's `soak.process.invoke`. There is no install, download, `npx` fetch, reportlab fallback, shell invocation, or PDF skill modification. Each tool process is bounded; each deck is limited to 40 pages and rendered at 150 DPI.

Overrides: `SOAK_NODE_BIN` selects the native Node executable; `SOAK_MARP_CLI` selects a local `marp-cli.js` file instead of narrow discovery under `%LOCALAPPDATA%/npm-cache/_npx/*/node_modules/@marp-team/marp-cli/`. Marp browser selection uses its `--browser auto` discovery and installed Chrome/Edge environment. The adapter records actual Node/Poppler versions; Marp and Poppler versions are queried with their native version arguments; unavailable version metadata remains unknown. Missing tools and render errors write a categorized `render.json` and return nonzero.

The source drafts are existing synthetic materials, not newly generated agent output. Their SHA-256 values identify the approved inputs; the style-modified copies are separate artifacts. Source revision labels in the sample config deliberately avoid claiming a clean or committed source snapshot.
