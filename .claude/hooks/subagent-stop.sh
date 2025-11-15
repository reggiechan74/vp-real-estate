#!/bin/bash

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Extract NEW fields from v2.0.42+
AGENT_ID=$(echo "$HOOK_INPUT" | jq -r '.agent_id // empty')
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.agent_transcript_path // empty')

# Check if it's one of the triumvirate
if [[ "$AGENT_ID" == "adam" ]] || \
   [[ "$AGENT_ID" == "reggie-chan-vp" ]] || \
   [[ "$AGENT_ID" == "dennis" ]]; then

    # Display the ACTUAL transcript content
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 ${AGENT_ID^^} COMPLETE RESPONSE:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Output the full transcript
    if [[ -f "$TRANSCRIPT_PATH" ]]; then
        cat "$TRANSCRIPT_PATH"
    else
        echo "⚠️  Warning: Transcript not found at $TRANSCRIPT_PATH"
        echo "Falling back to agent_transcript field..."
        # Fallback: try to extract transcript from JSON input
        echo "$HOOK_INPUT" | jq -r '.agent_transcript // "No transcript available"'
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # THEN tell Claude to suppress its summary
    cat << 'EOF'
SYSTEM: The agent's complete output appears above.
Do NOT summarize, rephrase, or add commentary.
Simply acknowledge with "Done." or proceed to next task.
EOF
fi
