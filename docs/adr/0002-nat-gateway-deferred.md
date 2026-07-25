---
title: NAT Gateway — відкладено, не терміново
status: deferred
date: 2026-07-24
---

## Чому

Outbound-зв'язність уже працює через вбудований App Service Standard
SNAT у поєднанні з дефолтними Azure NSG outbound rules (жодних кастомних
Outbound-правил не визначено, тому діють неявні AllowVnetOutBound /
AllowInternetOutBound). Витрати на NAT Gateway зараз не виправдані
відсутністю конкретної потреби.

## Альтернатива

Переглянути явно при старті Neo4j Aura (Security Dashboard Phase 2) чи
будь-якого іншого зовнішнього сервісу з IP-allowlisting. App Service
наразі має 14 різних, непередбачуваних outbound IP-адрес — NAT Gateway
звів би це до однієї стабільної IP для простого allowlisting на боці
зовнішнього сервісу.
