# CRISPR-ASR demonstration files

Use these samples in the website’s Python editor. The site inspects source without executing it.

1. Open CRISPR-ASR and select **Open Python file**.
2. Choose a sample and select **Run analysis**.
3. Compare the result with the checklist. For flagged samples, expand the finding and select **Highlight source**.
4. Where the checklist says **Preview repair**, open the preview to review the diff. Apply and re-scan to see the finding clear.

A comparison sample should produce zero findings in the current scanner. The shell preview assumes a POSIX deployment. YAML preview may change which YAML types are accepted.

## CWE-95 Dynamic code evaluation

Folder `01_CWE-95_Dynamic_Code_Evaluation`

- `01_eval_review.py` — 1 finding · Manual review
- `02_compile_review.py` — 1 finding · Manual review
- `03_json_comparison.py` — 0 findings

## CWE-78 Shell command risk

Folder `02_CWE-78_Shell_Command_Risk`

- `01_fixed_command_preview.py` — 1 finding · Guided preview
- `02_dynamic_command_review.py` — 1 finding · Manual review
- `03_argument_list_comparison.py` — 0 findings

## CWE-502 Unsafe deserialization

Folder `03_CWE-502_Unsafe_Deserialization`

- `01_yaml_loader_preview.py` — 1 finding · Guided preview
- `02_pickle_review.py` — 1 finding · Manual review
- `03_safe_yaml_comparison.py` — 0 findings

## CWE-330 Weak randomness

Folder `04_CWE-330_Weak_Randomness`

- `01_session_token_preview.py` — 1 finding · Preview repair
- `02_nonce_preview.py` — 1 finding · Preview repair
- `03_simulation_comparison.py` — 0 findings

## CWE-295 Disabled TLS verification

Folder `05_CWE-295_TLS_Verification`

- `01_requests_verification_review.py` — 1 finding · Manual review
- `02_tls_context_review.py` — 1 finding · Manual review
- `03_verified_tls_comparison.py` — 0 findings

## CWE-327 Weak hashing

Folder `06_CWE-327_Weak_Hashing`

- `01_sha1_review.py` — 1 finding · Manual review
- `02_md5_alias_review.py` — 1 finding · Manual review
- `03_sha256_comparison.py` — 0 findings

## CWE-367 Temporary-file race risk

Folder `07_CWE-367_Temporary_File_Race`

- `01_temporary_path_review.py` — 1 finding · Manual review
- `02_aliased_temporary_path_review.py` — 1 finding · Manual review
- `03_atomic_file_comparison.py` — 0 findings

## CWE-732 World-writable POSIX permissions

Folder `08_CWE-732_File_Permissions`

- `01_file_mode_review.py` — 1 finding · Manual review
- `02_directory_mode_review.py` — 1 finding · Manual review
- `03_owner_only_comparison.py` — 0 findings
