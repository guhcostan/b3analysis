# /b3:profile

Troca o perfil de análise. Controla qual modelo Claude é usado por tipo de agente.

**Uso:** `/b3:profile $ARGUMENTS`

Exemplos:
- `/b3:profile` — mostra o perfil atual
- `/b3:profile quality`
- `/b3:profile balanced`
- `/b3:profile budget`

---

## Perfis disponíveis

| Perfil | Síntese (sessão principal) | Agentes de dados | Custo aproximado |
|---|---|---|---|
| `quality` | claude-opus-4-6 | claude-opus-4-6 | $$$ |
| `balanced` | claude-sonnet-4-6 | claude-sonnet-4-6 | $$ |
| `budget` | claude-sonnet-4-6 | claude-haiku-4-5 | $ |

**Quando usar cada perfil:**
- `quality` — Decisão real de investimento. Melhor raciocínio na síntese e análise por ticker.
- `balanced` — Padrão. Boa qualidade com custo razoável (~$3,50 por run de carteira).
- `budget` — Triagem exploratória. Pré-filtro rápido antes de rodar `quality` nos melhores candidatos.

---

## Instruções

Parse `$ARGUMENTS`. Se nenhum argumento, apenas mostre o perfil atual e encerre.

### Mostrar perfil atual:
```bash
cat .b3profile 2>/dev/null || echo "balanced (padrão)"
```

### Definir perfil:

1. Escrever o nome do perfil em `.b3profile`:
```bash
echo "{PERFIL}" > .b3profile
```

2. Atualizar `.claude/settings.json` com o modelo de síntese:

Para `quality`:
```json
{ "model": "claude-opus-4-6" }
```

Para `balanced` ou `budget`:
```json
{ "model": "claude-sonnet-4-6" }
```

3. Confirmar ao usuário:
```
✅ Perfil definido: {PERFIL}

Modelos ativos:
  Síntese (sessão principal): {MODELO_SINTESE}
  Agentes de análise:         {MODELO_AGENTES}

Use /b3:swarm, /b3:portfolio ou /b3:analyze para aplicar este perfil.
```
