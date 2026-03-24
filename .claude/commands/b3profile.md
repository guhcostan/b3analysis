# /b3profile

Switch the analysis quality profile. Controls which model each agent type uses.

**Usage:** `/b3profile $ARGUMENTS`

Examples:
- `/b3profile` — show current profile
- `/b3profile quality`
- `/b3profile balanced`
- `/b3profile budget`

---

## Profiles

| Profile | Synthesis (main) | Ticker agents | Macro agent | Cost |
|---|---|---|---|---|
| `quality` | claude-opus-4-6 | claude-opus-4-6 | claude-sonnet-4-6 | $$$ |
| `balanced` | claude-sonnet-4-6 | claude-sonnet-4-6 | claude-haiku-4-5 | $$ |
| `budget` | claude-sonnet-4-6 | claude-haiku-4-5 | claude-haiku-4-5 | $ |

**When to use each:**
- `quality` — Final decision before investing real money. Best reasoning on synthesis and per-ticker analysis.
- `balanced` — Default. Good quality, reasonable cost (~$3.50/portfolio run).
- `budget` — Exploratory screening. Quick pre-filter before running quality on top candidates.

---

## Instructions

Parse `$ARGUMENTS`. If no argument, just show the current profile and exit.

### Show current profile:
```bash
cat .b3profile 2>/dev/null || echo "balanced (default)"
```

### Set profile:

1. Write the profile name to `.b3profile`:
```bash
echo "{PROFILE}" > .b3profile
```

2. Update `.claude/settings.json` with the synthesis model:

For `quality`:
```json
{ "model": "claude-opus-4-6" }
```

For `balanced` or `budget`:
```json
{ "model": "claude-sonnet-4-6" }
```

3. Confirm to the user:
```
✅ Profile set to {PROFILE}

Agent assignments:
  Synthesis (main):   {SYNTHESIS_MODEL}
  Ticker analysis:    {TICKER_MODEL}
  Macro analysis:     {MACRO_MODEL}

Run /portfolio or /analyze to use this profile.
```
