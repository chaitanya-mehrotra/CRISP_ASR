# CRISPR-ASR

Team HelixForge's AST-based automated software repair research prototype. The analysis workspace includes a Monaco Python editor backed by FastAPI.

## Windows setup

Use Python 3.11 or later and Node.js 22.12 or later. Run the backend and frontend in separate PowerShell terminals from the repository root.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Interactive API documentation is at http://127.0.0.1:8000/docs.

### Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Open the URL printed by Vite. Edit a sample or select **Open Python file** to load a UTF-8 .py file, then select **Run analysis**. Pick a statement in the outline to jump to its source line. Session history records analysis attempts until the page reloads.

### Verification

From `backend`, run ` .\.venv\Scripts\python.exe -m pytest -q`. From `frontend`, run `npm run build`.

See [project status](PROJECT_STATUS.md) and the [implementation roadmap](docs/ROADMAP.md).

## Security findings

Open **Weak randomness demo** and select **Run analysis**. Expand the CWE-330 finding, select **Highlight source**, and try replacing the token generator with the suggested secrets-based approach. Re-run analysis to check the edited source.

The scanner flags selected patterns involving dynamic evaluation, shell commands, object deserialization, and security-sensitive randomness. It recognizes unambiguous module-level imports and aliases and suppresses names that are rebound in the file. Security-sensitive names for randomness are a hint. Review the origin and intended use of values before changing code. The scanner does not trace arbitrary data flow across functions or files. Fix guidance and snippets are for manual editing, and an empty result only means that the supported patterns were not found.

## Preview and apply a repair

Expand the **Weak randomness** finding in the demo and select **Preview repair**. Review the changed line, the parse and compilation checks, and the re-scan result. Select **Apply and re-scan** to edit the open buffer, then select **Download .py** to save a copy. The editor's normal Undo command reverses the applied edit.

The preview uses the existing random-module reference and replaces the selected generator method with the same method on SystemRandom, keeping the arguments and surrounding source. Direct function imports, star imports, detected writes to random-module attributes, and targets that cannot be edited without discarding formatting stay in manual review. Validation compiles and re-scans without executing the uploaded code. It does not run behavioral tests or establish that the whole file is secure.

## Expanded analysis and guided repairs

The API resolves names per lexical scope and recognizes unambiguous direct imports and aliases. Input evidence is limited to local syntax, parameters, and simple assignments. Conditional imports, rebinding, dynamic imports and cross-file data flow limit what the scanner can prove. Source highlighting uses end-exclusive Monaco positions and supports multi-line calls.

Guided previews cover simple module-qualified YAML load calls and fixed plain literal POSIX subprocess.run calls. YAML may change accepted input types. Shell previews require checking the executable and deployment platform. Dynamic evaluation and pickle-family findings stay in manual review. Verification checks syntax, compilation, and scanner results without executing code.

### Module and API map

- backend/app/core/symbols.py indexes scopes, imports, and simple assignments.
- backend/app/core/context.py produces bounded local evidence and learning prompts.
- backend/app/core/rules.py adds exact ranges and repair modes to findings from POST /api/parse.
- backend/app/core/repair_templates.py builds source edits from matching AST nodes.
- backend/app/core/repair.py checks the selected target and stages an edit.
- backend/app/core/verification.py rejects invalid candidates, unresolved targets, and unexpected scanner results. POST /api/repair-preview returns verification for accepted candidates.
- The workspace exports the current Python buffer and a source-free JSON security report. The report includes the current findings and the latest verified edit applied to that exact source, if available.

Use the YAML loader or Fixed shell command example to try guided preview. The Code breakdown tab shows functions, classes, imports, calls, and branch constructs. Open Why this spot? on a finding for its node chain, local evidence, and self-check.

### Additional rule coverage

Rule scope includes explicit TLS verification bypasses (CWE-295), MD5 and SHA-1 calls for review (CWE-327), temporary file naming with mktemp (CWE-367), and world-writable POSIX chmod modes (CWE-732). These checks use resolved imports and visible arguments. Explicit non-security hashes using usedforsecurity=False are excluded. Each rule offers guidance for manual review. Load **File and connection checks demo** to see all four.

## Local accounts

Select **Sign in** in the header to create a local account or to sign in. The Python scanner and examples are also available to guests. Accounts and expiring sessions are stored in backend/accounts.sqlite3. The login panel is designed for the localhost classroom prototype.


## Sample Python files

Use the [sample checklist](samples/README.md) for one-rule demonstrations and the [larger demos](samples/09_Larger_Multi_Issue_Demos/README.md) for before-and-after scans covering multiple findings. Open a sample in the workspace and select **Run analysis**.
