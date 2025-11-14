# Lease Analysis Hooks

**Version:** 1.0
**Repository:** VP Real Estate Lease Abstract

## Overview

Intelligent skill activation system for commercial real estate lease analysis.

## Architecture

**3 Hooks:**
1. **UserPromptSubmit** (Reactive): Analyzes user prompts for keywords and agent invocations
2. **PreToolUse** (Proactive): Detects document types by filename before reading
3. **SubagentStop** (Enforcement): Ensures agent responses are passed through unfiltered

**Token Efficiency:** 96% reduction through proactive detection

## Hook Triggers

### UserPromptSubmit

Triggered when user submits a message.

**Agent Detection (Priority 1):**
Detects when user addresses Adam, Reggie, or Dennis by name and suggests invoking the appropriate agent.

**Patterns:**
- "Adam,", "hey adam", "ask adam", "adam can you", "adam what"
- "Reggie,", "hey reggie", "ask reggie", "reggie can you", "reggie what"
- "Dennis,", "hey dennis", "ask dennis", "dennis can you", "dennis what"

**Example:**
```
User: "hey adam, what's the difference between an offer to lease and lease agreement?"
Hook: 👤 AGENT ACTIVATION DETECTED
      🎯 AGENT REQUESTED: Adam
      📋 Role: Senior Analyst
      🤖 Model: haiku
      ACTION: Use Task tool with subagent_type="adam"
```

**Skill Detection (Priority 2):**
If no agent detected, analyzes keywords to suggest relevant skills.

**Keywords Detected:**
- Financial: NER, NPV, effective rent, breakeven, tenant credit, DSCR
- Legal: lease abstraction, assignment, sublease, default, termination
- Process: compliance, audit, comparison, valuation

**Example:**
```
User: "Calculate NER for this lease deal"
Hook: Suggests effective-rent-analyzer + commercial-lease-expert
```

### PreToolUse

Triggered BEFORE reading files.

**Patterns Detected:**
- Lease documents: `*lease*.pdf`, `*agreement*.docx`
- Offers: `*offer*lease*`, `*loi*`, `*term*sheet*`
- Financial: `*financial*statement*`, `*balance*sheet*`
- Calculator inputs: `*_input.json` in calculator directories

**Example:**
```
User: Read Sample_Inputs/offer_to_lease.pdf
Hook: (BEFORE read) Suggests offer-to-lease-expert + effective-rent-analyzer
Read tool: (THEN executes) File contents loaded
```

### SubagentStop

Triggered when a Claude Code subagent completes (Adam, Reggie, Dennis).

**Purpose:** Enforces the "pass-through unfiltered" requirement for agent responses

**Behavior:**
- Fires when any triumvirate subagent (adam/reggie-chan-vp/dennis) finishes responding
- Displays critical reminder to pass through agent response without summary/commentary
- Ensures agents speak in their own voice

**Example:**
```
Adam subagent completes
Hook: ⚠️  AGENT RESPONSE COMPLETE
      CRITICAL: Pass through the agent's response UNFILTERED
      ❌ DO NOT add summary
      ❌ DO NOT add commentary
      ❌ DO NOT rephrase
      ✅ Let them speak in their own voice
```

## Testing

**Test UserPromptSubmit:**
```bash
npm run test-prompt
```

**Test PreToolUse:**
```bash
npm run test-pretool
```

**Manual Testing:**
```bash
# UserPromptSubmit - Agent Detection
echo '{"prompt":"hey adam, analyze this deal"}' | ./skill-activation-prompt.sh
echo '{"prompt":"Reggie, help me with this crisis"}' | ./skill-activation-prompt.sh
echo '{"prompt":"Dennis what should I do?"}' | ./skill-activation-prompt.sh

# UserPromptSubmit - Skill Detection
echo '{"prompt":"review this lease agreement"}' | ./skill-activation-prompt.sh
echo '{"prompt":"calculate effective rent"}' | ./skill-activation-prompt.sh

# PreToolUse - Offer to Lease
echo '{"tool":"Read","parameters":{"file_path":"./Sample_Inputs/sample_offer_to_lease.pdf"}}' | ./pre-tool-use-skill-loader.sh

# PreToolUse - Financial Statement
echo '{"tool":"Read","parameters":{"file_path":"./financials.pdf"}}' | ./pre-tool-use-skill-loader.sh
```

## File Structure

```
.claude/hooks/
├── README.md                         # This file
├── package.json                      # Node dependencies
├── skill-activation-prompt.sh        # UserPromptSubmit wrapper
├── skill-activation-prompt.ts        # UserPromptSubmit logic
├── pre-tool-use-skill-loader.sh      # PreToolUse wrapper
├── pre-tool-use-skill-loader.ts      # PreToolUse logic
├── subagent-stop.sh                  # SubagentStop enforcement
├── generate-skill-rules.js           # Auto-generator
├── lease-types-map.json              # Document type mapping
└── skill-rules.json                  # (Auto-generated) Activation rules
```

## Maintenance

**Adding New Skills:**
1. Create skill in `.claude/skills/skill-name/`
2. Write SKILL.md with proper frontmatter
3. Run: `npm run generate-rules`
4. Test: `npm run test-prompt`

**Adding Document Patterns:**
1. Edit `lease-types-map.json`
2. Add pattern to appropriate document type
3. Test: `npm run test-pretool`

## Troubleshooting

**Hooks Not Triggering:**
```bash
# Check settings.json
cat ../.settings.json

# Check permissions
ls -la *.sh
chmod +x *.sh

# Check paths
grep "CLAUDE_PROJECT_DIR" *.ts
```

**Wrong Skills Suggested:**
```bash
# Regenerate rules
npm run generate-rules

# Check skill frontmatter
head -10 ../skills/*/SKILL.md
```

---

**Last Updated:** November 13, 2025
**Contact:** Reggie Chan, CFA, FRICS
