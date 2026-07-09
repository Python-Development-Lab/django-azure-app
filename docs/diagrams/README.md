# Diagrams — Django Azure Security Template

Diagram-as-Code у форматі PlantUML.

## Файли

| Файл | Тип | Опис |
|---|---|---|
| `dfd_level0_context.puml` | DFD Level 0 | Context Diagram — зовнішні актори і потоки |
| `dfd_level1_processes.puml` | DFD Level 1 | Internal Processes — P1–P5, Data Stores |
| `zero_trust_sequence.puml` | Sequence | Zero Trust auth + device verification (NIST SP 800-207) |
| `c4_container.puml` | C4 Container | C4 Container Diagram (C4-PlantUML stdlib) |
| `cicd_pipeline.puml` | Activity | 7-job DevSecOps pipeline |

## Рендеринг в Codespace

```bash
# Рендерити всі діаграми в SVG
plantuml -tsvg docs/diagrams/*.puml -o output/

# Рендерити одну діаграму
plantuml -tsvg docs/diagrams/c4_container.puml
```

## VS Code

Встановлено: `jebbs.plantuml`
- `Alt+D` — preview поточного файлу
- `Ctrl+Shift+P` → "PlantUML: Export Current Diagram"
