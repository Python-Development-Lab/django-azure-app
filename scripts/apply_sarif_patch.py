#!/usr/bin/env python3
"""Safely inserts SARIF-related steps into deploy-staging-terraform.yml
by anchoring on unique, simple single-line markers rather than trying to
match fragile multi-line shell blocks. Aborts if any anchor is not found
exactly once, to avoid silently corrupting the workflow file.
"""
import sys

BANDIT_SARIF_BLOCK = """      - name: Bandit — SARIF output
        run: |
          pip install bandit-sarif-formatter --quiet --break-system-packages
          bandit -r . \\
            --exclude ./packages,./venv,./staticfiles,./terraform \\
            --format sarif \\
            --output bandit-results.sarif \\
            --severity-level medium || true

      - name: Upload Bandit SARIF
        uses: github/codeql-action/upload-sarif@v4
        if: always()
        continue-on-error: true
        with:
          sarif_file: bandit-results.sarif
          category: bandit-sast

"""

GITLEAKS_SARIF_BLOCK = """      - name: Gitleaks — SARIF output
        run: |
          ./gitleaks detect \\
            --source . \\
            --config .gitleaks.toml \\
            --report-format sarif \\
            --report-path gitleaks-results.sarif \\
            --no-git \\
            --exit-code 0 || true
        continue-on-error: true

      - name: Upload Gitleaks SARIF
        uses: github/codeql-action/upload-sarif@v4
        if: always()
        continue-on-error: true
        with:
          sarif_file: gitleaks-results.sarif
          category: gitleaks-secrets

"""

ZAP_SARIF_BLOCK = """      - name: Convert ZAP report to SARIF
        if: always()
        run: python3 scripts/zap_to_sarif.py report_json.json zap-results.sarif

      - name: Upload ZAP SARIF
        uses: github/codeql-action/upload-sarif@v4
        if: always()
        continue-on-error: true
        with:
          sarif_file: zap-results.sarif
          category: zap-dast

"""

INSERTIONS = [
    ("      - name: Gitleaks — secrets detection\n", BANDIT_SARIF_BLOCK, "before"),
    ("      - name: pip-audit — dependency vulnerabilities\n", GITLEAKS_SARIF_BLOCK, "before"),
    ("      - name: Upload ZAP report\n", ZAP_SARIF_BLOCK, "before"),
]

ARTIFACT_LIST_INSERTIONS = [
    ("            bandit-report.json\n", "            bandit-results.sarif\n"),
    ("            gitleaks-report.json\n", "            gitleaks-results.sarif\n"),
    ("            report_json.json\n", "            zap-results.sarif\n"),
]


def main(path: str) -> int:
    with open(path) as f:
        lines = f.readlines()

    for anchor, block, position in INSERTIONS:
        matches = [i for i, l in enumerate(lines) if l == anchor]
        if len(matches) != 1:
            print(
                f"ABORT: anchor {anchor!r} found {len(matches)} times "
                f"(expected 1). No changes written."
            )
            return 1
        idx = matches[0]
        block_lines = block.splitlines(keepends=True)
        lines[idx:idx] = block_lines

    for anchor, new_line in ARTIFACT_LIST_INSERTIONS:
        matches = [i for i, l in enumerate(lines) if l == anchor]
        if len(matches) != 1:
            print(
                f"ABORT: artifact anchor {anchor!r} found {len(matches)} times "
                f"(expected 1). No changes written."
            )
            return 1
        idx = matches[0]
        lines.insert(idx + 1, new_line)

    with open(path, "w") as f:
        f.writelines(lines)

    print(
        f"Patched {path} successfully: {len(INSERTIONS)} step blocks + "
        f"{len(ARTIFACT_LIST_INSERTIONS)} artifact lines inserted."
    )
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else ".github/workflows/deploy-staging-terraform.yml"
    sys.exit(main(target))
