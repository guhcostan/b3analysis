#!/usr/bin/env bash

# PreToolUse hook — validates ticker and date args before run.sh executes
# Exit 2 = block the tool call and show error to user
# Exit 0 = allow

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

if ! echo "$COMMAND" | grep -q "run.sh"; then
    exit 0
fi

TICKER=$(echo "$COMMAND" | grep -oE '\b[A-Z]{4}[0-9]{1,2}(\.SA)?\b' | head -1)
DATE=$(echo "$COMMAND" | grep -oE '\b[0-9]{4}-[0-9]{2}-[0-9]{2}\b' | head -1)

if [ -n "$TICKER" ]; then
    if ! echo "$TICKER" | grep -qE '^[A-Z]{4}[0-9]{1,2}(\.SA)?$'; then
        echo "Erro de validação: ticker '$TICKER' inválido. Formato esperado: WEGE3 ou WEGE3.SA" >&2
        exit 2
    fi
fi

if [ -n "$DATE" ]; then
    if ! echo "$DATE" | grep -qE '^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'; then
        echo "Erro de validação: data '$DATE' inválida. Formato esperado: YYYY-MM-DD" >&2
        exit 2
    fi
fi

exit 0
