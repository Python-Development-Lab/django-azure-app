#!/usr/bin/env python3
"""Converts OWASP ZAP report_json.json into SARIF 2.1.0 for GitHub Code Scanning.
No external dependencies — self-contained, since no verified official ZAP-to-SARIF
converter exists for the zaproxy/action-baseline output format.
"""
import json
import sys

RISK_TO_LEVEL = {"3": "error", "2": "warning", "1": "note", "0": "note"}


def convert(input_path: str, output_path: str) -> int:
    with open(input_path) as f:
        data = json.load(f)

    rules = {}
    results = []

    for site in data.get("site", []):
        site_name = site.get("@name", "unknown")
        for alert in site.get("alertitem", site.get("alerts", [])):
            rule_id = f"zap-{alert.get('pluginid', 'unknown')}"
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": alert.get("alert", "ZAP Finding"),
                    "shortDescription": {"text": alert.get("alert", "")[:200]},
                    "fullDescription": {"text": (alert.get("desc") or "")[:1000]},
                    "help": {"text": (alert.get("solution") or "")[:1000]},
                    "properties": {"tags": ["security", "dast", "owasp-zap"]},
                }
            level = RISK_TO_LEVEL.get(str(alert.get("riskcode", "1")), "warning")
            instances = alert.get("instances") or [{"uri": site_name}]
            for instance in instances:
                live_uri = instance.get("uri", site_name)
                results.append(
                    {
                        "ruleId": rule_id,
                        "level": level,
                        "message": {
                            "text": (
                                f"{alert.get('desc') or alert.get('alert', '')} "
                                f"[Live URL: {live_uri}]"
                            )[:2000]
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": ".zap/rules.tsv"
                                    }
                                }
                            }
                        ],
                    }
                )

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "OWASP ZAP",
                        "informationUri": "https://www.zaproxy.org/",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }

    with open(output_path, "w") as f:
        json.dump(sarif, f, indent=2)

    print(f"Converted {len(results)} ZAP findings ({len(rules)} unique rules) to SARIF")
    return 0


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "report_json.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "zap-results.sarif"
    sys.exit(convert(input_file, output_file))
