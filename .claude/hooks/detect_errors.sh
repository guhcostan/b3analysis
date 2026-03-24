#!/usr/bin/env bash

# PostToolUse hook — scans run.sh output for errors and warns Claude
# Always exits 0 (informational only — never blocks)

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

if ! echo "$COMMAND" | grep -q "run.sh"; then
    exit 0
fi

OUTPUT=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_response',''))" 2>/dev/null || echo "")

WARNINGS=""

if echo "$OUTPUT" | grep -q "Traceback"; then
    WARNINGS="${WARNINGS}\n⚠️  Python Traceback detectado — verifique o erro acima antes de continuar."
fi

if echo "$OUTPUT" | grep -qE "(^Error:|Error:)"; then
    WARNINGS="${WARNINGS}\n⚠️  Linha de erro detectada no output — verifique se os dados estão completos."
fi

if echo "$OUTPUT" | grep -q "\[BCB\] Aviso:"; then
    WARNINGS="${WARNINGS}\n⚠️  Falha na API do BCB detectada — dados macroeconômicos podem estar incompletos."
fi

if [ -n "$WARNINGS" ]; then
    printf "\n--- Avisos do Hook detect_errors ---%b\n" "$WARNINGS" >&2
fi

exit 0
