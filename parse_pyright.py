import json
import sys

with open('pyright_output_utf8.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

diagnostics = data.get('generalDiagnostics', [])

grouped = {}
for diag in diagnostics:
    file_path = diag.get('file', '')
    msg = diag.get('message', '').split('\n')[0]
    severity = diag.get('severity', '')
    line = diag.get('range', {}).get('start', {}).get('line', 0) + 1
    rule = diag.get('rule', '')
    
    key = (file_path, msg, rule)
    if key not in grouped:
        grouped[key] = []
    grouped[key].append(line)

print("--- UNIQUE ERRORS ---")
for (file_path, msg, rule), lines in grouped.items():
    print(f"File: {file_path}")
    print(f"Lines: {lines[:5]}{'...' if len(lines) > 5 else ''}")
    print(f"Rule: {rule}")
    print(f"Message: {msg}")
    print("-" * 20)
