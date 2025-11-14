#!/bin/bash

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Extract subagent type from the hook input
SUBAGENT_TYPE=$(echo "$HOOK_INPUT" | jq -r '.subagent_type // .agentType // empty')

# Check if it's one of the triumvirate
if [[ "$SUBAGENT_TYPE" == "adam" ]] || \
   [[ "$SUBAGENT_TYPE" == "reggie-chan-vp" ]] || \
   [[ "$SUBAGENT_TYPE" == "dennis" ]]; then

    cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  AGENT RESPONSE COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL: Pass through the agent's response UNFILTERED

❌ DO NOT add summary
❌ DO NOT add commentary
❌ DO NOT rephrase
✅ Let them speak in their own voice

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
fi
