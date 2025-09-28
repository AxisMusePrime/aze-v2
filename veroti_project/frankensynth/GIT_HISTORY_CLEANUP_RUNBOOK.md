GIT HISTORY CLEANUP RUNBOOK

Goal

 - Remove all occurrences of the BTC bech32 address `[REDACTED_BTC_ADDRESS]` and the generated artifacts in `frankensynth/` from repository history.

Safety pre-reqs

1. Create a full archive backup of the repository (done earlier: `frankensynth/backups/repo-backup-*.tgz`). Verify it exists before proceeding.
2. Ensure you have local clones of any remotes or coordination with other contributors (history rewrite requires force-push and will rewrite commit SHAs).
3. Run the steps below on a local clone/test mirror first.

Plan overview

1. Create a mirror clone of the repo for transformation and testing.
2. Run `git filter-repo` to remove path(s) and exact string matches.
3. Inspect the cleaned mirror; run tests and verify file lists and commit history integrity.
4. If verified, force-push changes to the upstream remote (only after coordination).
5. Communicate the forced-update instructions to collaborators and provide recovery steps.

Commands (explicit)

# 1. Create a mirror for safe testing
git clone --mirror /path/to/repo /tmp/aze-v2-mirror.git
cd /tmp/aze-v2-mirror.git

# 2. Remove specific files/paths from history (frankensynth artifacts)
# This removes the entire frankensynth/ directory from all commits
git filter-repo --invert-paths --path frankensynth/

# 3. Remove the specific BTC address occurrences from all remaining files
# Use an exact-replacement to redact the address from history
git filter-repo --replace-text <(printf "[REDACTED_BTC_ADDRESS]==[REDACTED_BTC_ADDRESS]\n")

# Note: On macOS, use a temporary file instead of process substitution if your shell doesn't support it:
# printf "[REDACTED_BTC_ADDRESS]==[REDACTED_BTC_ADDRESS]\n" > /tmp/replacements.txt
# git filter-repo --replace-text /tmp/replacements.txt

# 4. Verify the mirror: search for the address
git --no-pager grep -n "[REDACTED_BTC_ADDRESS]" || echo "address removed"

# 5. If verification passes, push changes back to remote (DANGEROUS: coordinate with team)
# This will rewrite history on the remote and requires force-push
git push --force --all origin
git push --force --tags origin

Rollback / recovery

- If something goes wrong, restore from the backup tarball created earlier: extract into a safe location and re-clone.
- Alternatively, if the mirror is not pushed yet, do nothing and the remote remains unchanged.

Notes and caveats

- `git filter-repo` is the recommended tool (faster, safer than BFG for textual replacements). Ensure it is installed: https://github.com/newren/git-filter-repo
- This runbook includes both a path deletion (remove `frankensynth/`) and textual replacement for the BTC address. You can choose one or both operations.
- After rewriting history, collaborators need to reclone or follow steps to align their local repositories.

If you want me to execute these steps now, reply with exactly: "do it". I will then:
- Double-check backups exist, run the mirror cleanup, run verification, and only then present the changes for your review before pushing to remote. I will not push force changes without your explicit "push" confirmation.

If you want a more conservative cleanup (only replace address occurrences, keep frankensynth/ artifacts archived), say "replace-only" and I'll prepare commands accordingly.
