# Findings Report — frankensynth/pii_scan_results.json

Overview
This report summarizes the results of a repository-wide sensitive-data scan produced at frankensynth/pii_scan_results.json. The scan covered the project root: /Users/axis/veroti_project and flagged 139 files with potential findings.

High-level counts

Notes on false positives

Critical issues (recommended immediate attention)
These are files that appear to contain private keys, wallet seeds, or real API-like tokens. Treat these as compromised and rotate credentials immediately if they are live.

  - Findings: BTC_BECH32 address: [REDACTED_BTC_ADDRESS]
  - Why important: cryptocurrency addresses may indicate wallet usage; if private keys are present elsewhere, funds could be at risk.
  - Recommendation: If this is a public wallet or test data, consider redacting or moving to an offline document. If the corresponding private key exists in repo, remove and rotate.

  - Findings: BTC_BECH32 address: [REDACTED_BTC_ADDRESS]
  - Recommendation: review and redact if necessary.

  - Findings: EMAIL: [REDACTED EMAIL]
  - Recommendation: Replace with generic contact placeholder or move to environment variable/config not committed to git.

  - Findings: BTC_BECH32 address: [REDACTED_BTC_ADDRESS]

  - Many API_KEY_LIKE and EMAIL hits are inside virtual environment or vendored packages. These are usually safe but noisy.

Next steps
1. Manually inspect the flagged files in the project root and any source files (not inside venv) for real secrets: look for private keys (xprv), seed phrases, API keys, or config files containing tokens.
2. If secrets are confirmed, rotate or revoke them immediately.
3. Do NOT push any changes to remote origins until you have removed or redacted secrets and optionally cleaned git history.
4. Produce a prioritized top-20 sensitive files list (next task) and a git-history cleanup guide.

Appendix: How this report was generated

Contact
If you'd like, I can now:
This findings report was moved to `frankensynth/offline_research/FINDINGS_REPORT.md` for hygiene.
Please inspect the offline copy for full details.

