"""
Team Room Chat Integration
Connects Streamlit Team Room to Claude agents via Anthropic API
"""

import subprocess
import json
import tempfile
import os
import re
from typing import Dict, List, Optional
from pathlib import Path

# Try to import anthropic
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# Agent configuration
AGENT_CONFIG = {
    "adam": {
        "agent_file": ".claude/agents/adam.md",
        "model": "claude-3-5-haiku-20241022"
    },
    "reggie": {
        "agent_file": ".claude/agents/reggie-chan-vp.md",
        "model": "claude-3-5-sonnet-20241022"
    },
    "dennis": {
        "agent_file": ".claude/agents/dennis.md",
        "model": "claude-opus-4-20250514"
    }
}


def load_agent_system_prompt(agent_file: str) -> Optional[str]:
    """
    Load agent system prompt from markdown file

    Args:
        agent_file: Path to agent .md file

    Returns:
        System prompt content or None if file not found
    """
    try:
        agent_path = Path(agent_file)
        if not agent_path.exists():
            return None

        with open(agent_path, 'r') as f:
            content = f.read()

        # Extract content after the YAML front matter
        # Front matter is between --- markers
        parts = content.split('---', 2)
        if len(parts) >= 3:
            # Content after second ---
            system_prompt = parts[2].strip()
            return system_prompt
        else:
            # No front matter, use whole content
            return content.strip()

    except Exception as e:
        print(f"Error loading agent file {agent_file}: {e}")
        return None


def chat_with_agent(
    persona: str,
    message: str,
    conversation_history: List[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Chat with a Claude agent persona via Anthropic API

    Uses agent system prompts from .claude/agents/*.md files

    Args:
        persona: "adam", "reggie", or "dennis"
        message: User's message
        conversation_history: Optional previous conversation

    Returns:
        dict with 'response' and 'status'
    """
    # Check if Anthropic API is available
    if not ANTHROPIC_AVAILABLE:
        return {
            "response": f"Anthropic package not installed.\n\nFalling back to demo mode:\n\n{get_demo_response(persona, message)}",
            "status": "error"
        }

    # Get API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "response": f"ANTHROPIC_API_KEY environment variable not set.\n\nFalling back to demo mode:\n\n{get_demo_response(persona, message)}",
            "status": "error"
        }

    # Get agent configuration
    agent_config = AGENT_CONFIG.get(persona)
    if not agent_config:
        return {
            "response": f"Unknown persona: {persona}",
            "status": "error"
        }

    # Load agent system prompt
    system_prompt = load_agent_system_prompt(agent_config["agent_file"])
    if not system_prompt:
        return {
            "response": f"Could not load agent system prompt for {persona}.\n\nFalling back to demo mode:\n\n{get_demo_response(persona, message)}",
            "status": "error"
        }

    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)

        # Build messages list from conversation history
        messages = []

        if conversation_history and len(conversation_history) > 0:
            # Include recent history (last 10 messages to manage token usage)
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                role = msg.get("role", "")
                content = msg.get("content", "")

                # Convert to Anthropic format
                if role == "user":
                    messages.append({"role": "user", "content": content})
                elif role == "assistant":
                    messages.append({"role": "assistant", "content": content})

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call Anthropic API
        response = client.messages.create(
            model=agent_config["model"],
            max_tokens=4096,
            system=system_prompt,
            messages=messages
        )

        # Extract response text
        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text += block.text

        if response_text:
            return {
                "response": response_text.strip(),
                "status": "success"
            }
        else:
            return {
                "response": "No response received from agent.",
                "status": "error"
            }

    except Exception as e:
        error_msg = str(e)
        return {
            "response": f"Error calling Anthropic API: {error_msg}\n\nFalling back to demo mode:\n\n{get_demo_response(persona, message)}",
            "status": "error"
        }


def get_demo_response(persona: str, message: str) -> str:
    """
    Generate an intelligent demo response for the Team Room

    Analyzes the message for keywords and generates contextual responses
    """
    msg_lower = message.lower()

    # Detect topic
    is_lease_question = any(word in msg_lower for word in ['lease', 'rent', 'tenant', 'landlord'])
    is_financial = any(word in msg_lower for word in ['rent', 'price', 'cost', 'npv', 'irr', 'ner'])
    is_credit = any(word in msg_lower for word in ['credit', 'financial', 'risk', 'default'])
    is_negotiation = any(word in msg_lower for word in ['negotiate', 'deal', 'offer', 'counter'])
    is_strategic = any(word in msg_lower for word in ['strategy', 'decision', 'should i', 'advice'])

    persona_responses = {
        "adam": f"""Thank you for your question! I've analyzed your request regarding: "{message[:60]}..."

**Quick Analysis:**
""" + (f"""
- This is a **{('lease deal' if is_lease_question else 'financial')}** question requiring quantitative analysis
- I'd approach this using our institutional framework
- {'The effective rent calculator would be ideal for this' if is_financial else 'Let me break down the key factors'}
""" if is_lease_question or is_financial else f"""
- Standard commercial real estate question
- Recommend a structured analytical approach
- I'll focus on quantifiable metrics
""") + f"""

**Recommended Analysis:**
""" + ("""
1. **Run Effective Rent Calculator** - Get NER, NPV, IRR metrics
2. **Compare to Market** - Benchmark against comps
3. **Risk Assessment** - Evaluate downside scenarios
4. **Document** - Prepare clear stakeholder presentation
""" if is_financial else """
1. **Gather Data** - Collect relevant financial information
2. **Run Analysis** - Use appropriate calculator tools
3. **Benchmark** - Compare against market standards
4. **Present** - Document findings clearly
""") + (f"""

**Credit Considerations:**
- Run Tenant Credit Analysis to assess risk
- Check DSCR, current ratio, debt coverage
- Determine appropriate security requirements
""" if is_credit else "") + f"""

**My Recommendation:**
{'Use the calculator tools to run the numbers - I can help interpret the results once you have them.' if is_financial else 'Start with data collection, then we can run the appropriate analysis.'}

**Next Steps:**
- Navigate to the relevant calculator in the sidebar
- Input your deal parameters
- Review the output metrics with me

*This is an enhanced demo response. For production AI, configure ANTHROPIC_API_KEY environment variable for real-time analysis from Adam.*
""",

        "reggie": f"""I've done a thorough analysis of your situation regarding: "{message[:50]}..."

**Initial Assessment:**
This is more complex than it appears on the surface. Let me break down what I'm seeing:

**Deep Dive Analysis:**
1. **Financial Structure:** The deal economics need careful scrutiny. I'd want to see full rent schedules, TI packages, and operating expense structures.

2. **Risk Factors:** Several concerns to address:
   - Market positioning and competitive set
   - Tenant creditworthiness and default probability
   - Lease structure and landlord protections
   - Exit strategies and renewal probabilities

3. **Forensic Check:** Following the money here - we need to verify:
   - Actual vs. projected cash flows
   - Hidden costs or contingencies
   - Comparable transaction validation

**Red Flags to Watch:**
⚠️ Ensure all assumptions are validated
⚠️ Verify market data independently
⚠️ Check for structural issues

**My Recommendation:**
[Comprehensive analysis with full documentation would go here]

**Framework for Decision:**
I'd build a systematic approach using our calculators:
- Effective Rent for deal economics
- Credit Analysis for tenant risk
- MCDA for competitive positioning

This requires exhaustive documentation. Let me know if you want me to dive deeper into any aspect.

*Note: This is a demo response. In production, you'll receive Reggie's full institutional-grade forensic analysis.*
""",

        "dennis": f"""Alright, let's cut through the noise and get to what really matters about: "{message[:50]}..."

**What I'm Hearing:**
You're asking about {message[:30]}...

**What's Really Going On:**
This isn't just about the numbers - it's about human psychology, politics, and hard choices. I've seen this pattern dozens of times over 36 years.

**The Human Psychology Here:**
Real estate is 30% spreadsheets and 70% people. Someone wants something, someone else has leverage, and everyone's posturing. What's the real story behind this question?

**My Take (Blunt Truth):**
- If this were your own money, would you do it?
- What's your gut saying vs. what the spreadsheet says?
- Who benefits if this goes through, and who's on the hook if it fails?

**What You Should Actually Do:**
1. Run the fundamentals (they always give you the right answer)
2. Assess the people factors (who's reliable, who's not)
3. Think 3-5 years out (Father Time is undefeated)
4. Make your decision and own it

**Hard Truth:**
[Blunt reality check would go here - the thing you might not want to hear but need to]

Remember: Think things through. Make decisions as if it were your own money. And don't let urgency force you into a bad deal.

What's the real decision you need to make here?

*Note: This is a demo response. In production, you'll receive Dennis's full strategic wisdom and reality checks.*
"""
    }

    return persona_responses.get(persona, "I'm not sure how to respond to that.")


def is_ai_available() -> bool:
    """
    Check if Anthropic API integration is available

    Returns:
        True if anthropic package is installed and API key is set
    """
    if not ANTHROPIC_AVAILABLE:
        return False

    # Check if API key is configured
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    return api_key is not None and len(api_key) > 0
