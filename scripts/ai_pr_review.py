#!/usr/bin/env python3
"""
AI PR review: sends a redacted diff + repo conventions to Claude,
writes a markdown review to stdout / a file.

Usage:
    python scripts/ai_pr_review.py --diff pr.diff --out review.md
"""
import argparse
import re
import sys
from pathlib import Path

import anthropic

CONVENTIONS_PATH = Path("docs/ai-review/conventions.md")
MODEL = "claude-sonnet-4-6"

SECRET_PATTERNS = [
    re.compile(r"(?i)(password|secret|client_secret|api[_-]?key|token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)DB_PASSWORD\s*=\s*\S+"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"\b[A-Za-z0-9_\-]{32,}\b"),
]


def redact(diff_text: str) -> str:
    redacted = diff_text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def load_conventions() -> str:
    if CONVENTIONS_PATH.exists():
        return CONVENTIONS_PATH.read_text()
    return "(No conventions.md found -- reviewing with generic best practices only.)"


SYSTEM_PROMPT = """You are a senior security-focused reviewer for a Django/Azure \
infrastructure repository. You review PR diffs against the repo's own stated \
conventions, not generic best practices. Deterministic scanners (Bandit, Trivy, \
Checkov-class tools) already run separately -- do not repeat what they catch \
(known CVEs, hardcoded secrets pattern-matching, basic lint). Focus only on what \
they structurally cannot see:

- Unintended permission/RBAC changes (scope creep, subscription-vs-resource-group \
  scope, new role assignments not matching least-privilege)
- Drift from the repo's own architectural conventions (see below)
- Logic issues: a Terraform change that looks correct in isolation but breaks an \
  invariant elsewhere (e.g. breaks the BUILDING=true build-time Key Vault \
  workaround, or reintroduces a previously-fixed race condition)
- Missing least-privilege on new resources

If you find nothing worth flagging, say so briefly -- do not invent findings to \
seem useful. Cite specific file:line references from the diff. Be concise: this \
is a PR comment, not a report."""


def build_user_prompt(diff: str, conventions: str) -> str:
    return f"""## Repo conventions (constitution)
{conventions}

## PR diff to review (secrets already redacted)
```diff
{diff}
```

Review this diff per your instructions. Output GitHub-flavored markdown, \
structured as:

### AI Review Summary
(one-line verdict: no concerns / minor notes / needs human attention)

### Findings
(bullet list, or "No findings outside conventional scanner coverage." if clean)

### Notes
(anything worth a human's attention that isn't a "finding" per se)
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    raw_diff = args.diff.read_text()
    if not raw_diff.strip():
        args.out.write_text("### AI Review Summary\nNo relevant changes to review.\n")
        return 0

    redacted_diff = redact(raw_diff)
    conventions = load_conventions()

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(redacted_diff, conventions)}],
    )

    text_blocks = [b.text for b in response.content if b.type == "text"]
    review_md = "\n".join(text_blocks).strip() or "AI review produced no output."

    args.out.write_text(review_md + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
