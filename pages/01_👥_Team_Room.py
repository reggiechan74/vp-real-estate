"""
The Team Room - Chat with AI Personas
Adam (Analyst), Reggie (VP), Dennis (Advisor)
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.styling import inject_custom_css
from utils.personas import get_persona, get_all_personas, format_persona_header, get_persona_welcome_message
from utils.team_room_chat import chat_with_agent, get_demo_response, is_ai_available

# Page config
st.set_page_config(
    page_title="The Team Room",
    page_icon="👥",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Initialize chat histories in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {
        'adam': [],
        'reggie': [],
        'dennis': []
    }

if 'current_persona' not in st.session_state:
    st.session_state.current_persona = 'adam'

# Check AI availability
ai_available = is_ai_available()

def generate_response(persona_name: str, prompt: str, history: list) -> str:
    """Generate response using AI if available, otherwise use demo"""
    if ai_available:
        result = chat_with_agent(persona_name, prompt, history)
        if result['status'] == 'success':
            return result['response']
        else:
            st.warning(f"AI Error: {result['response']}. Using demo mode.")
            return get_demo_response(persona_name, prompt)
    else:
        return get_demo_response(persona_name, prompt)

# Header
st.title("👥 The Team Room")
st.markdown("**Chat with Your AI Advisors** - Get expert insights from three specialized professionals")

st.markdown("---")

# Persona Selection Tabs
tab1, tab2, tab3 = st.tabs(["👔 ADAM (Analyst)", "💼 REGGIE (VP)", "🎯 DENNIS (Advisor)"])

personas_info = get_all_personas()

with tab1:
    st.session_state.current_persona = 'adam'
    persona = personas_info['adam']

    # Persona header
    st.markdown(format_persona_header('adam'), unsafe_allow_html=True)

    # Persona details
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        **Model:** {persona['model']} (Fast execution)

        **When to use Adam:**
        {chr(10).join([f"- {use_case}" for use_case in persona['use_cases']])}

        **Response Style:** {persona['response_style']}
        """)

    with col2:
        st.info(f"""
        **Quick Facts:**
        - ⚡ Fastest responses
        - 📊 Quantitative focus
        - 🤝 Diplomatic tone
        - 📈 80/20 analysis
        """)

    # Chat interface
    st.markdown("---")
    st.markdown("### 💬 Chat with Adam")

    # Display chat history
    for message in st.session_state.chat_history['adam']:
        with st.chat_message(message["role"], avatar=persona['avatar'] if message["role"] == "assistant" else None):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask Adam about your lease deal..."):
        # Add user message
        st.session_state.chat_history['adam'].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar=persona['avatar']):
            with st.spinner("Adam is analyzing..."):
                response = generate_response('adam', prompt, st.session_state.chat_history['adam'])
            st.markdown(response)
            st.session_state.chat_history['adam'].append({"role": "assistant", "content": response})

with tab2:
    st.session_state.current_persona = 'reggie'
    persona = personas_info['reggie']

    # Persona header
    st.markdown(format_persona_header('reggie'), unsafe_allow_html=True)

    # Persona details
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        **Model:** {persona['model']} (Deep analysis)

        **Credentials:** CFA, FRICS, VP of Leasing & Asset Management

        **When to use Reggie:**
        {chr(10).join([f"- {use_case}" for use_case in persona['use_cases']])}

        **Response Style:** {persona['response_style']}
        """)

    with col2:
        st.warning(f"""
        **Expertise:**
        - 🔬 Forensic analysis
        - 💼 Crisis management
        - 📊 Complex structures
        - 🎯 Brutally honest
        """)

    # Chat interface
    st.markdown("---")
    st.markdown("### 💬 Chat with Reggie")

    # Display chat history
    for message in st.session_state.chat_history['reggie']:
        with st.chat_message(message["role"], avatar=persona['avatar'] if message["role"] == "assistant" else None):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask Reggie about complex situations..."):
        # Add user message
        st.session_state.chat_history['reggie'].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar=persona['avatar']):
            with st.spinner("Reggie is conducting deep analysis..."):
                response = generate_response('reggie', prompt, st.session_state.chat_history['reggie'])
            st.markdown(response)
            st.session_state.chat_history['reggie'].append({"role": "assistant", "content": response})

with tab3:
    st.session_state.current_persona = 'dennis'
    persona = personas_info['dennis']

    # Persona header
    st.markdown(format_persona_header('dennis'), unsafe_allow_html=True)

    # Persona details
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        **Model:** {persona['model']} (Strategic depth)

        **Experience:** 36+ years, former president of major institutional RE operation

        **When to use Dennis:**
        {chr(10).join([f"- {use_case}" for use_case in persona['use_cases']])}

        **Response Style:** {persona['response_style']}
        """)

    with col2:
        st.success(f"""
        **Wisdom:**
        - 🎯 Strategic perspective
        - 🧠 Psychology insights
        - 💪 Tough love
        - ⚖️ Reality checks
        """)

    # Chat interface
    st.markdown("---")
    st.markdown("### 💬 Chat with Dennis")

    # Display chat history
    for message in st.session_state.chat_history['dennis']:
        with st.chat_message(message["role"], avatar=persona['avatar'] if message["role"] == "assistant" else None):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask Dennis for strategic advice..."):
        # Add user message
        st.session_state.chat_history['dennis'].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar=persona['avatar']):
            with st.spinner("Dennis is providing strategic wisdom..."):
                response = generate_response('dennis', prompt, st.session_state.chat_history['dennis'])
            st.markdown(response)
            st.session_state.chat_history['dennis'].append({"role": "assistant", "content": response})

# Sidebar with chat controls
with st.sidebar:
    st.markdown("### 🎛️ Chat Controls")

    # Show AI status
    ai_status_color = "🟢" if ai_available else "🟡"
    ai_status_text = "Real AI" if ai_available else "Demo Mode"
    st.info(f"{ai_status_color} **Status:** {ai_status_text}")

    if st.button("🗑️ Clear Current Chat"):
        current = st.session_state.current_persona
        st.session_state.chat_history[current] = []
        st.rerun()

    if st.button("🗑️ Clear All Chats"):
        st.session_state.chat_history = {'adam': [], 'reggie': [], 'dennis': []}
        st.rerun()

    st.markdown("---")

    st.markdown("### 📤 Export Options")
    st.info("Chat export coming soon")

    st.markdown("---")

    st.markdown("### 💡 Tips")
    st.markdown("""
    **Best Practices:**
    - Use Adam for routine analysis
    - Escalate to Reggie for complex issues
    - Consult Dennis for strategic decisions
    - Upload files for document analysis (coming soon)
    - Export conversations for records
    """)
