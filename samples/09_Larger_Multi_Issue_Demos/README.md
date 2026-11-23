# Larger CRISPR-ASR demonstrations

Open a before file using **Open Python file** and select **Run analysis**. Each before file has four findings, including at least one repair preview. Try previews one at a time and watch the count decrease. Then load the matching solved file to see the complete set of changes. These files are scan fixtures. The website analyzes them without executing them.

## Event registration — 4 findings to 0

| Finding | Fix in the solved file |
| --- | --- |
| CWE-95 dynamic evaluation | Read attendee data with json.loads and retain the field checks. Inputs now use JSON syntax. |
| CWE-502 unsafe YAML loading | Use yaml.safe_load. This demo expects standard YAML types. |
| CWE-330 weak randomness | Use random.SystemRandom().choices while retaining the ticket alphabet and length. |
| CWE-367 temporary-file race risk | Create the temporary file atomically with TemporaryFile, then read it through the same open handle. |

Try the **weak randomness** and **YAML** previews first. The other two changes are manual. The attendee example expects JSON, such as a record with a name and an email.

## Artifact report — 4 findings to 0

| Finding | Fix in the solved file |
| --- | --- |
| CWE-295 TLS verification disabled | Enable server certificate verification. |
| CWE-327 weak hashing | Use SHA-256 for the fingerprint and update the algorithm label. |
| CWE-732 world-writable permissions | Create a new file with owner-only POSIX permissions. The solved function expects an unused destination path. |
| CWE-78 shell command risk | Pass the fixed POSIX executable and argument separately with shell=False. |

The **shell** preview assumes a POSIX deployment. The other three changes are manual. An artifact digest is a fingerprint. Authenticating an artifact requires checking it against a trusted reference.

## What to say after scanning

“CRISPR-ASR reported four supported patterns in the original. After the changes, those findings cleared.” The verification here covers syntax, compilation, and the scanner results.
