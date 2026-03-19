# Privileged Identity Management (PIM)

## Статус
Потребує Microsoft Entra ID P2 або Entra ID Governance.
Поточний tenant: Free (Personal). PIM задокументовано як policy-as-code.

## Концепція JIT Access для цього проєкту

### Ролі під управлінням PIM
| Роль | Тип | Max тривалість | Потребує MFA | Потребує justification |
|---|---|---|---|---|
| Owner (subscription) | eligible | 1 година | ✅ | ✅ |
| Global Administrator | eligible | 1 година | ✅ | ✅ |
| Key Vault Administrator | eligible | 4 години | ✅ | ✅ |
| Security Administrator | eligible | 8 годин | ✅ | ✅ |

### Постійні (permanent) ролі — мінімум
| Роль | Призначення |
|---|---|
| Key Vault Secrets User | Managed Identity (prod + staging) |
| Reader | CI/CD Service Principal |

## Активація ролі (workflow)
```bash
# 1. Перевірити eligible ролі
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilitySchedules" \
  --query "value[].{role:roleDefinition.displayName, principal:principal.displayName}"

# 2. Активувати роль на 1 годину
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleRequests" \
  --body '{
    "action": "selfActivate",
    "principalId": "<user-object-id>",
    "roleDefinitionId": "<role-definition-id>",
    "directoryScopeId": "/",
    "justification": "Emergency access for Key Vault rotation",
    "scheduleInfo": {
      "startDateTime": null,
      "expiration": {
        "type": "AfterDuration",
        "duration": "PT1H"
      }
    }
  }'

# 3. Деактивувати достроково
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignmentScheduleRequests" \
  --body '{"action": "selfDeactivate", ...}'
```

## PIM Alert Rules (рекомендовані)
- Занадто багато Global Admins (> 2)
- Ролі призначені permanently замість eligible
- Активація без MFA
- Активація з незвичної локації

## AZ-500 Coverage
- Domain 1: Identity (15-20%)
- Just-In-Time access, role activation workflow
- PIM audit logs, alerts
- Principle of Least Privilege
