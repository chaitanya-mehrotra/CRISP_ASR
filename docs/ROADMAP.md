# Implementation roadmap

1. **Foundation.** Establish the Python parser, typed API, React editor, development proxy, and Windows setup. Confirm an editor request reaches the Python parser and displays the actual response.
2. **Detection.** Introduce a rule registry and node locations. Cover the four proposed weakness categories with positive and negative test cases. Identify uncertain name resolution or data provenance in reported findings.
3. **Repair and validation.** Gate every template on explicit context requirements. Record transformation details and manual-review reasons. Reparse, compile, and rerun detection. Evaluate test isolation separately before accepting any uploaded tests.
4. **Benchmark.** Define ground-truth labels and measurement units before generating results. Run both methods on identical fixtures. Compute confusion counts, precision, recall, F1, patch outcomes, and wall-clock time from the run.
5. **Persistence and interface.** Add SQLite and SQLAlchemy for analysis and benchmark metadata. Connect analysis, validation, comparison, benchmark, and history views to the corresponding API results.
6. **Release verification.** Exercise the integrated workflow on Windows, document supported and unsupported patterns, and record reproducible benchmark results.
