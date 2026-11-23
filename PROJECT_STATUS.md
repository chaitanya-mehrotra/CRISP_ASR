# CRISPR-ASR project status

## First milestone

- FastAPI health and AST parsing endpoints with typed responses and input bounds.
- React, Vite, Tailwind CSS, and Monaco editor connected to the parsing endpoint.
- API tests for health, AST output, invalid syntax, and the source length limit.
- Windows setup and implementation roadmap.

## Pending phases

Broader repair coverage, isolated behavioral validation, benchmarks, persistence, and remaining dashboard pages are tracked in [the roadmap](docs/ROADMAP.md).

## Verification

- Four backend API tests passed under Python 3.12.
- The Vite production build succeeded. Vite reported that the main bundle exceeded its warning threshold with Monaco included.
- The Vite development server served the app. A source request through its API proxy reached FastAPI and returned the expected AST summary.
- The editor interaction was not separately browser-tested.

## Website milestone

- Added a responsive analysis workspace with the Monaco editor, UTF-8 Python file upload, and three editable examples.
- Connected the syntax tree panel to FastAPI. Results include node counts, a node-type breakdown, and a clickable top-level outline. Syntax errors link back to the source line, and changed source marks the previous result as stale.
- Added session history for analysis attempts and a rule scope page describing the four planned vulnerability checks.

## Website verification

- Five backend tests passed, including the test for outline names and source lines.
- Verified in the browser that an uploaded Python file parses, outline links focus the editor, changed source marks results as stale, and invalid source produces a line-linked diagnostic and history entry.
- Checked the layout at 390 px and 1440 px wide with no horizontal overflow.
- Vite production build passed and reported a large main bundle with Monaco included.

## DNA workspace and weakness guidance

- Added a double-helix workspace header and themed navigation, a findings view with severity filtering, and exact source selection from each finding.
- Added four conservative AST checks and a rule catalog served from FastAPI.
- Added explanations and copyable safer patterns for manual repair.
- Browser verification covered severity filtering, the selected source range, a manual fix and re-scan, and the four live catalog entries. Checked the desktop and mobile layouts.
- All 18 backend tests passed. Coverage includes the four categories, false-positive examples, Unicode source positions, and the rules endpoint.

## Bioinspired EL interaction polish

- Replaced the background motif with a paired-strand DNA illustration and a scan animation attached to the real analysis action.
- Added tactile press feedback to the analysis controls, navigation, result views, and finding actions. Keyboard activation uses a centered pulse. Reduced-motion preferences suppress the moving effects.

## Repair preview and validation

- Added a targeted SystemRandom repair for supported weak-randomness findings.
- Added a before-and-after diff, syntax and compilation checks, and a re-scan that verifies the selected finding was removed.
- Applying a candidate is opt-in and undoable in the editor. Download exports the current buffer.
- Verified preview, apply, re-scan, undo, and download in the browser. Backend tests cover selective edits, Unicode and CRLF preservation, stale targets, unsupported cases, and compilation failure.

## Expanded analysis and reports

- Added lexical alias tracking, local origin hints, and interactive finding lessons.
- Added guarded YAML and POSIX literal-command previews. The separate verifier rejects candidates when the selected finding remains or additional findings change.
- Added structural counts and JSON export with before/after finding counts and verification for the latest applied repair.
- Verified YAML preview/apply/export, fixed-command preview, and syntax-error navigation in the browser.
