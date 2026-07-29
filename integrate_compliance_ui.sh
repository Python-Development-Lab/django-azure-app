#!/usr/bin/env bash
set -e

echo "=== Step 1: Insert Python functions into core/views.py ==="
python3 << 'PYEOF'
with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

anchor = "# ── FinOps Dashboard"

if anchor not in content:
    raise SystemExit(
        "ERROR: anchor '# ── FinOps Dashboard' not found in core/views.py. "
        "Stopping without changes."
    )

if "_get_compliance_mappings" in content:
    print("Functions already present in core/views.py — skipping insertion (idempotent).")
else:
    new_functions = '''def _parse_compliance_file(file_path):
    """Parses a single compliance .md file: frontmatter (control_id,
    regulation, title, status, date) + '## Description' / '## Evidence' /
    optional '## Gaps' sections."""
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    frontmatter_raw, body = parts[1], parts[2]

    meta = {}
    for line in frontmatter_raw.strip().splitlines():
        if ':' not in line:
            continue
        key, _, value = line.partition(':')
        meta[key.strip()] = value.strip()

    sections = {}
    current_key = None
    current_lines = []
    for line in body.splitlines():
        if line.startswith('## '):
            if current_key:
                sections[current_key] = '\\n'.join(current_lines).strip()
            current_key = line[3:].strip()
            current_lines = []
        elif current_key:
            current_lines.append(line)
    if current_key:
        sections[current_key] = '\\n'.join(current_lines).strip()

    return {
        'control_id': meta.get('control_id', ''),
        'regulation': meta.get('regulation', ''),
        'title': meta.get('title', file_path.stem),
        'status': meta.get('status', 'unknown'),
        'date': meta.get('date', ''),
        'description': sections.get('Description', ''),
        'evidence': sections.get('Evidence', ''),
        'gaps': sections.get('Gaps', ''),
    }


def _get_compliance_mappings():
    """Scans docs/compliance/*.md, parses each file, sorted by filename."""
    compliance_dir = Path(__file__).parent.parent / 'docs' / 'compliance'
    mappings = []
    error = None

    try:
        if not compliance_dir.exists():
            return [], f"Directory {compliance_dir} not found"

        md_files = sorted(compliance_dir.glob('*.md'))
        for file_path in md_files:
            parsed = _parse_compliance_file(file_path)
            if parsed:
                mappings.append(parsed)
    except Exception as e:
        error = f"Error reading compliance files: {e}"

    return mappings, error


def security_compliance(request):
    """HTMX partial — GET /security/compliance/"""
    mappings, error = _get_compliance_mappings()

    total = len(mappings)
    implemented = sum(1 for m in mappings if m['status'] == 'implemented')
    partial = sum(1 for m in mappings if m['status'] == 'partial')

    return render(request, 'core/partials/security_compliance.html', {
        'mappings': mappings,
        'error': error,
        'total_controls': total,
        'implemented_count': implemented,
        'partial_count': partial,
    })


'''
    content = content.replace(anchor, new_functions + anchor)
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK: functions inserted into core/views.py")
PYEOF

echo ""
echo "=== Step 2: Route in core/urls.py ==="
if grep -q "name='security_compliance'" core/urls.py; then
    echo "Route already present — skipping."
else
    if grep -q "name='security_decisions'" core/urls.py; then
        sed -i "/name='security_decisions'),/a\\    path('security/compliance/', views.security_compliance, name='security_compliance')," core/urls.py
    else
        sed -i "/name='security_threat_intel'),/a\\    path('security/compliance/', views.security_compliance, name='security_compliance')," core/urls.py
    fi
    echo "OK: route added"
fi
grep -n "security_compliance" core/urls.py

echo ""
echo "=== Step 3: Template templates/core/partials/security_compliance.html ==="
mkdir -p templates/core/partials
cat > templates/core/partials/security_compliance.html << 'EOF'
{# templates/core/partials/security_compliance.html — English version #}

<div class="compliance-panel">
    <h3 class="compliance-panel-title">Compliance Mapping — ISO/IEC 27001:2022 Annex A (Technological)</h3>

    {% if error %}
        <div class="compliance-error">
            ⚠️ {{ error }}
        </div>
    {% else %}
        <p class="compliance-summary">
            Selected controls shown: <strong>{{ total_controls }}</strong> of 34 A.8.x Technological controls
            ({{ implemented_count }} implemented, {{ partial_count }} partial).
            Organizational, People and Physical themes (59 further controls) are not covered here.
        </p>

        {% for item in mappings %}
            <div class="compliance-card compliance-{{ item.status }}">
                <div class="compliance-header">
                    <span class="compliance-regulation-badge">{{ item.regulation }}</span>
                    <span class="compliance-control-badge">{{ item.control_id }}</span>
                    <span class="compliance-status-badge status-{{ item.status }}">
                        {% if item.status == "implemented" %}✓ Implemented
                        {% elif item.status == "partial" %}◐ Partial
                        {% elif item.status == "planned" %}○ Planned
                        {% elif item.status == "not_applicable" %}— N/A
                        {% elif item.status == "gap" %}✕ Gap
                        {% else %}{{ item.status }}
                        {% endif %}
                    </span>
                </div>
                <h4 class="compliance-title">{{ item.title }}</h4>
                <p class="compliance-description">{{ item.description }}</p>
                {% if item.evidence %}
                    <p class="compliance-evidence"><strong>Evidence:</strong> {{ item.evidence }}</p>
                {% endif %}
                {% if item.gaps %}
                    <p class="compliance-gaps"><strong>Gaps:</strong> {{ item.gaps }}</p>
                {% endif %}
            </div>
        {% empty %}
            <p class="compliance-empty">No compliance mappings documented yet.</p>
        {% endfor %}
    {% endif %}
</div>
EOF
echo "OK: template created"

echo ""
echo "=== Step 4: HTMX block in templates/core/security.html ==="
python3 << 'PYEOF'
with open('templates/core/security.html', 'r', encoding='utf-8') as f:
    content = f.read()

if 'compliance-section' in content:
    print("HTMX block already present — skipping.")
else:
    lines = content.splitlines(keepends=True)
    insert_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '</div>' and lines[i] == lines[i].lstrip():
            insert_idx = i
            break

    if insert_idx is None:
        raise SystemExit(
            "ERROR: could not find an unindented closing </div> in security.html."
        )

    new_block = '''  <!-- HTMX: Compliance Mapping, loads on page load, parallel -->
  <div id="compliance-section"
       hx-get="{% url 'core:security_compliance' %}"
       hx-trigger="load"
       hx-swap="innerHTML"
       hx-indicator="#compliance-spinner">
    <div id="compliance-spinner" style="text-align:center; padding:2rem; color:#666;">
      <div style="font-size:1.5rem; margin-bottom:0.5rem;">📜</div>
      Loading compliance mapping...
    </div>
  </div>
'''
    lines.insert(insert_idx, new_block)
    with open('templates/core/security.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"OK: HTMX block inserted before line {insert_idx + 1}")
PYEOF

echo ""
echo "=== Step 5: Syntax and lint checks ==="
python3 -c "import ast; ast.parse(open('core/views.py', encoding='utf-8').read())" && echo "core/views.py: Syntax OK"
python3 -c "import ast; ast.parse(open('core/urls.py', encoding='utf-8').read())" && echo "core/urls.py: Syntax OK"

if command -v flake8 >/dev/null 2>&1; then
    flake8 core/views.py --max-line-length=120 && echo "flake8: OK"
else
    echo "flake8 not found in PATH — skipping lint"
fi

echo ""
echo "============================================================"
echo "Done. Manual next step — review git diff, then commit:"
echo ""
echo "  git status"
echo "  git add core/views.py core/urls.py templates/core/partials/security_compliance.html templates/core/security.html"
echo "  git commit -m \"Add Compliance Mapping UI panel to Security Dashboard\""
echo "  git push origin develop"
echo "============================================================"
