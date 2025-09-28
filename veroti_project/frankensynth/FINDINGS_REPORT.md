# Findings Report — frankensynth/pii_scan_results.json

Overview
--------
This report summarizes the results of a repository-wide sensitive-data scan produced at frankensynth/pii_scan_results.json. The scan covered the project root: /Users/axis/veroti_project and flagged 139 files with potential findings.

High-level counts
-----------------
- Total files flagged: 139
- Common finding types: BTC_BECH32, API_KEY_LIKE, EMAIL, PHONE, XPRV, XPUB (where detected)

Notes on false positives
------------------------
- Many "API_KEY_LIKE" hits are library constants, function names, or test/example strings found inside third-party packages (e.g., files under venv). These are not secrets by themselves and can be ignored.
- The scanner uses heuristics; please review each hit manually before taking destructive action.

Critical issues (recommended immediate attention)
-------------------------------------------------
These are files that appear to contain private keys, wallet seeds, or real API-like tokens. Treat these as compromised and rotate credentials immediately if they are live.

- docker-compose.yml (project root)
  - Findings: BTC_BECH32 address: [REDACTED_BTC_ADDRESS]
  - Why important: cryptocurrency addresses may indicate wallet usage; if private keys are present elsewhere, funds could be at risk.
  - Recommendation: If this is a public wallet or test data, consider redacting or moving to an offline document. If the corresponding private key exists in repo, remove and rotate.

- run_entylion_conduit.py (project root)
  - Findings: BTC_BECH32 address: [REDACTED_BTC_ADDRESS]
  - Recommendation: review and redact if necessary.

- frankensynth/codex_manifest_safe.py
  - Findings: EMAIL: [REDACTED EMAIL]
  - Recommendation: Replace with generic contact placeholder or move to environment variable/config not committed to git.

- veroti-project/docker-compose.yml
  - Findings: BTC_BECH32 address: [REDACTED_BTC_ADDRESS]

- Other notable files (venv and pip vendored packages)
  - Many API_KEY_LIKE and EMAIL hits are inside virtual environment or vendored packages. These are usually safe but noisy.

Next steps
----------
1. Manually inspect the flagged files in the project root and any source files (not inside venv) for real secrets: look for private keys (xprv), seed phrases, API keys, or config files containing tokens.
2. If secrets are confirmed, rotate or revoke them immediately.
3. Do NOT push any changes to remote origins until you have removed or redacted secrets and optionally cleaned git history.
4. Produce a prioritized top-20 sensitive files list (next task) and a git-history cleanup guide.

Appendix: How this report was generated
--------------------------------------
- A regex-based scanner (frankensynth/pii_redact.py) was used to traverse the repository and flag common PII patterns (emails, phone numbers, crypto addresses, xpub/xprv tokens, and generic API-like long tokens). The output was written to frankensynth/pii_scan_results.json.

Contact
-------
If you'd like, I can now:
- Produce the top-20 file list and recommended per-file actions (safe, non-destructive).
- Create a git-history cleanup guide and a preview of the git commands to run (you must confirm before running them).

