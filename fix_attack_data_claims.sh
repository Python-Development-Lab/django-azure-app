#!/usr/bin/env bash
set -e

echo "=== Виправлення T1068, T1110.004, T1528 у attack_data.json ==="

python3 << 'PYEOF'
with open('security/mitre/attack_data.json', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    (
        '''        {
          "id": "T1068",
          "name": "Exploitation for Privilege Escalation",
          "status": "detected",
          "control": "Threat Ontology pattern: privilege_escalation (KBSSE)",
          "detection": "RiskScoringMiddleware confidence threshold"
        },''',
        '''        {
          "id": "T1068",
          "name": "Exploitation for Privilege Escalation",
          "status": "gap",
          "control": "Threat Ontology pattern: privilege_escalation (KBSSE) — planned, not implemented",
          "detection": "Planned: RiskScoringMiddleware (concept only, no code yet — see backlog)"
        },'''
    ),
    (
        '''        {
          "id": "T1110.004",
          "name": "Credential Stuffing",
          "status": "detected",
          "control": "Threat Ontology pattern: credential_stuffing (KBSSE)",
          "detection": "RiskScoringMiddleware IoC signals"
        },''',
        '''        {
          "id": "T1110.004",
          "name": "Credential Stuffing",
          "status": "gap",
          "control": "Threat Ontology pattern: credential_stuffing (KBSSE) — planned, not implemented",
          "detection": "Planned: RiskScoringMiddleware (concept only, no code yet — see backlog)"
        },'''
    ),
    (
        '''        {
          "id": "T1528",
          "name": "Steal Application Access Token",
          "status": "detected",
          "control": "Threat Ontology pattern: token_theft (KBSSE)",
          "detection": "MSAL token refresh middleware anomaly check"
        }''',
        '''        {
          "id": "T1528",
          "name": "Steal Application Access Token",
          "status": "gap",
          "control": "Threat Ontology pattern: token_theft (KBSSE) — planned, not implemented",
          "detection": "TokenRefreshMiddleware refreshes tokens but performs no anomaly detection — gap"
        }'''
    ),
]

missing = []
for old, new in replacements:
    if old not in content:
        missing.append(old.strip().splitlines()[1] if len(old.strip().splitlines()) > 1 else old[:60])
        continue
    content = content.replace(old, new, 1)

if missing:
    print("УВАГА: не знайдено точного збігу для наступних записів (пропущено, без змін):")
    for m in missing:
        print(" -", m)
else:
    print("OK: усі 3 записи знайдено й замінено")

with open('security/mitre/attack_data.json', 'w', encoding='utf-8') as f:
    f.write(content)

import json
json.load(open('security/mitre/attack_data.json', encoding='utf-8'))
print("OK: JSON все ще валідний після редагування")
PYEOF

echo ""
echo "=== Перевірка результату ==="
grep -n -A4 '"id": "T1068"' security/mitre/attack_data.json
echo "-----"
grep -n -A4 '"id": "T1110.004"' security/mitre/attack_data.json
echo "-----"
grep -n -A4 '"id": "T1528"' security/mitre/attack_data.json

echo ""
echo "============================================================"
echo "Готово. Review, then commit:"
echo ""
echo "  git add security/mitre/attack_data.json"
echo "  git status"
echo "  git commit -m \"Fix inflated detection claims: RiskScoringMiddleware and token anomaly check don't exist in code\""
echo "  git push origin develop"
echo "============================================================"
