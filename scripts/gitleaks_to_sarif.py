#!/usr/bin/env python3
"""Converts gitleaks JSON report into SARIF 2.1.0 for GitHub Code Scanning.

Bypasses gitleaks' native --report-format sarif, which has a documented
history of silently failing to produce output across several releases
(see https://github.com/gitleaks/gitleaks/issues/1677). The JSON report
is already proven to work reliably in this pipeline, so we convert it
ourselves instead of re-running gitleaks a second time.
"""
import json
import sys


def convert(input_path: str, output_path: str) -> int:
    with open(input_path) as f:
        content = f.read().strip()

    findings = json.loads(content) if content else []

    rules = {}
    results = []

    for finding in findings:
        rule_id = finding.get("RuleID", "unknown-secret")
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": finding.get("Description", rule_id)},
                "properties": {"tags": ["security", "secret-scanning", "gitleaks"]},
            }

        file_path = finding.get("File", "unknown")
        start_line = finding.get("StartLine", 1) or 1

        results.append(
            {
                "ruleId": rule_id,
                "level": "error",
                "message": {
                    "text": f"{finding.get('Description', rule_id)} (commit: {finding.get('Commit', 'n/a')[:8]})"
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": file_path},
                            "region": {"startLine": start_line},
                        }
                    }
                ],
                "partialFingerprints": {
                    "gitleaksFingerprint": finding.get("Fingerprint", "")
                },
            }
        )

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Gitleaks",
                        "informationUri": "https://github.com/gitleaks/gitleaks",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }

    with open(output_path, "w") as f:
        json.dump(sarif, f, indent=2)

    print(f"Converted {len(results)} gitleaks findings ({len(rules)} unique rules) to SARIF")
    return 0


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "gitleaks-report.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "gitleaks-results.sarif"
    sys.exit(convert(input_file, output_file))
