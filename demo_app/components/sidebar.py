"""
Sidebar Component for Streamlit Chat Application
Handles API key configuration and feature toggles
"""
import streamlit as st


def sidebar():
    """
    Render sidebar with configuration options
    """
    st.sidebar.title("⚙️ Configuration")
    
    # API Key Configuration
    st.sidebar.markdown("### 🔑 API Key")
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        key="OPENAI_API_KEY_INPUT",
        help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
    )
    
    if api_key:
        st.session_state["OPENAI_API_KEY"] = api_key
        st.session_state["open_api_key_configured"] = True
        st.sidebar.success("✅ API Key configured!")
    else:
        st.session_state["open_api_key_configured"] = False
        st.sidebar.warning("⚠️ Please enter your API key")
    
    st.sidebar.markdown("---")
    
    # Feature Toggles
    st.sidebar.markdown("### 🎛️ Features")
    
    # File upload toggle
    st.session_state["file_selection"] = st.sidebar.checkbox(
        "📄 Enable PDF Uploads",
        value=True,
        help="Allow uploading PDF documents for analysis"
    )
    
    # Voice input toggle
    st.session_state["voice_selection"] = st.sidebar.checkbox(
        "🎤 Enable Voice Input",
        value=True,
        help="Enable voice-to-text using OpenAI Whisper"
    )
    
    # TTS voice selection
    if st.session_state.get("voice_selection", True):
        st.session_state["tts_voice"] = st.sidebar.selectbox(
            "🔊 TTS Voice",
            options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
            index=4,  # Default to "nova"
            help="Select voice for text-to-speech responses"
        )
    
    st.sidebar.markdown("---")
    
    # Session Management
    st.sidebar.markdown("### 💾 Session")
    
    # Session ID display
    session_id = st.session_state.get("session_id", "default_session")
    st.sidebar.text_input(
        "Session ID",
        value=session_id,
        disabled=True,
        help="Current conversation session identifier"
    )
    
    # Clear conversation button
    if st.sidebar.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Conversation cleared! How can I help you?"
            }
        ]
        st.session_state.pdf_content = ""
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Model Information
    st.sidebar.markdown("### 🤖 Model Info")
    st.sidebar.info(
        """
        **Language Model:** GPT-4o
        **Speech-to-Text:** Whisper-1
        **Text-to-Speech:** TTS-1
        **Max PDF Size:** 25 MB
        """
    )
    
    st.sidebar.markdown("---")
    
    # Tips
    with st.sidebar.expander("💡 Tips & Tricks"):
        st.markdown("""
        **Voice Input:**
        - Speak clearly and minimize background noise
        - Works in 99+ languages
        - Click the mic icon to record
        - Get audio responses automatically!
        
        **PDF Analysis:**
        - Upload one or multiple PDFs
        - Ask specific questions about the content
        - Context is maintained throughout the conversation
        
        **Audio Responses:**
        - When you use voice input, responses include audio
        - Choose your preferred voice in settings
        - Both text and audio are provided
        
        **Best Practices:**
        - Be specific in your questions
        - Reference previous messages in follow-ups
        - Use voice for quick queries
        """)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Built with Streamlit & LangChain<br>
        Powered by OpenAI
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    # For testing the sidebar independently
    st.set_page_config(page_title="Sidebar Test", page_icon="⚙️")
    sidebar()
    st.title("Sidebar Component Test")
    st.write("Check the sidebar configuration →")