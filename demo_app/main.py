"""
Upgraded Streamlit Chat Application with Voice Support
- Modern LangChain patterns (RunnableWithMessageHistory)
- Voice input with OpenAI Whisper STT
- PDF processing with RAG
- Latest Streamlit audio features
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

import streamlit as st
import time
import tempfile
from typing import Optional

# Modern LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader

# OpenAI for Whisper STT
from openai import OpenAI

# Import sidebar component (assuming it exists)
try:
    from demo_app.components.sidebar import sidebar
except ImportError:
    def sidebar():
        """Fallback sidebar if import fails"""
        st.sidebar.title("Settings")
        api_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            key="OPENAI_API_KEY",
            help="Enter your OpenAI API key"
        )
        if api_key:
            st.session_state["OPENAI_API_KEY"] = api_key
            st.session_state["open_api_key_configured"] = True
        
        # File upload selection
        st.session_state["file_selection"] = st.sidebar.checkbox(
            "Enable file uploads",
            value=True
        )
        
        # Voice input selection
        st.session_state["voice_selection"] = st.sidebar.checkbox(
            "Enable voice input",
            value=True
        )


# Store for conversation history
store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Get or create conversation history for a session"""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def create_conversational_chain(api_key: str, pdf_content: str = ""):
    """
    Create a modern conversational chain with message history support
    
    Args:
        api_key: OpenAI API key
        pdf_content: Optional PDF content to use as context
    
    Returns:
        RunnableWithMessageHistory chain
    """
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        temperature=0,
        streaming=True
    )
    
    # Create prompt template with optional PDF context
    if pdf_content:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions based on the conversation history 
            and the provided PDF context.
            
            PDF Context:
            {pdf_content}
            
            Use this context to provide accurate and relevant answers."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        # Create chain with prompt and LLM
        chain = prompt | llm
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer questions based on the conversation history."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        # Create chain with prompt and LLM
        chain = prompt | llm
    
    # Wrap with message history
    conversational_chain = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    
    return conversational_chain, pdf_content if pdf_content else None


def transcribe_audio(audio_bytes, api_key: str) -> str:
    """
    Transcribe audio using OpenAI Whisper API
    
    Args:
        audio_bytes: Audio file bytes
        api_key: OpenAI API key
    
    Returns:
        Transcribed text
    """
    try:
        client = OpenAI(api_key=api_key)
        
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes.getvalue())
            tmp_path = tmp_file.name
        
        # Transcribe using Whisper
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return transcript
    
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return ""


def text_to_speech(text: str, api_key: str, voice: str = "nova") -> bytes:
    """
    Convert text to speech using OpenAI TTS API
    
    Args:
        text: Text to convert to speech
        api_key: OpenAI API key
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Audio bytes
    """
    try:
        client = OpenAI(api_key=api_key)
        
        # Generate speech using TTS
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Return audio bytes
        return response.content
    
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None


def process_pdf(uploaded_file) -> str:
    """
    Process the PDF file and return its content
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        Extracted text from PDF
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Use PyPDFLoader to load the PDF
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        
        # Extract text from all pages
        pdf_text = "\n\n".join([page.page_content for page in pages])
        
        return pdf_text
    
    finally:
        # Clean up the temporary file
        os.unlink(tmp_path)


def display_message_with_animation(message: str, placeholder) -> str:
    """
    Display message with typing animation
    
    Args:
        message: Message to display
        placeholder: Streamlit placeholder for the message
    
    Returns:
        Full message
    """
    full_response = ""
    for chunk in message.split():
        full_response += chunk + " "
        time.sleep(0.05)
        placeholder.markdown(full_response + "▌")
    
    placeholder.markdown(full_response)
    return full_response


def main():
    """Main application function"""
    
    # Page configuration
    st.set_page_config(
        page_title="AI Chat with Voice & Audio Responses",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.header("🤖 AI Chat Assistant")
    st.markdown("*With Voice Input, Audio Responses & PDF Analysis*")
    
    # Initialize sidebar
    sidebar()
    
    # Check if API key is configured
    if not st.session_state.get("open_api_key_configured"):
        st.error("⚠️ Please configure your OpenAI API Key in the sidebar!")
        st.stop()
    
    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm your AI assistant. You can:\n- Type your questions\n- 🎤 Use voice input (get audio responses!)\n- 📄 Upload PDF documents for analysis"
            }
        ]
    
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = ""
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = "default_session"
    
    if "file_selection" not in st.session_state:
        st.session_state.file_selection = True
    
    if "voice_selection" not in st.session_state:
        st.session_state.voice_selection = True
    
    if "audio_input_used" not in st.session_state:
        st.session_state.audio_input_used = False
    
    if "tts_voice" not in st.session_state:
        st.session_state.tts_voice = "nova"
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input with voice and file support
    prompt = st.chat_input(
        "Type your message or use voice input...",
        accept_file=st.session_state.get("file_selection", True),
        file_type=["pdf"],
        accept_audio=st.session_state.get("voice_selection", True)
    )
    
    # Process user input
    if prompt:
        user_text = None
        audio_transcription = None
        
        # Check if audio was provided
        if hasattr(prompt, 'audio') and prompt.audio:
            st.session_state.audio_input_used = True  # Track audio usage
            
            with st.spinner("🎤 Transcribing audio..."):
                audio_transcription = transcribe_audio(
                    prompt.audio,
                    st.session_state.get("OPENAI_API_KEY")
                )
            
            if audio_transcription:
                # Display transcription
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"🎤 Voice: {audio_transcription}"
                })
                with st.chat_message("user"):
                    st.markdown(f"🎤 Voice: {audio_transcription}")
                
                user_text = audio_transcription
        else:
            st.session_state.audio_input_used = False  # Reset flag for text input
        
        # Check if text was provided
        if hasattr(prompt, 'text') and prompt.text:
            user_text = prompt.text
            st.session_state.messages.append({
                "role": "user",
                "content": user_text
            })
            with st.chat_message("user"):
                st.markdown(user_text)
        
        # Check if files were uploaded
        if hasattr(prompt, 'files') and prompt.files:
            processed_files = []
            all_pdf_content = ""
            
            for uploaded_file in prompt.files:
                if uploaded_file.name.lower().endswith('.pdf'):
                    with st.spinner(f'📄 Processing {uploaded_file.name}...'):
                        pdf_content = process_pdf(uploaded_file)
                        all_pdf_content += f"\n\n=== Content from: {uploaded_file.name} ===\n\n{pdf_content}"
                        processed_files.append(uploaded_file.name)
            
            if processed_files:
                file_names = ", ".join(processed_files)
                message = f"📄 Uploaded: {file_names}"
                
                st.session_state.messages.append({
                    "role": "user",
                    "content": message
                })
                with st.chat_message("user"):
                    st.markdown(message)
                
                # Update PDF content in session state
                st.session_state.pdf_content = all_pdf_content
                
                # Acknowledge PDF processing
                ack_message = f"✅ PDF processed! I've analyzed {len(processed_files)} document(s). You can now ask questions about the content."
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ack_message
                })
                with st.chat_message("assistant"):
                    st.markdown(ack_message)
        
        # Generate response if there's text to process
        if user_text:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                with st.spinner("🤔 Thinking..."):
                    # Create the chain with current PDF content
                    chain, pdf_ctx = create_conversational_chain(
                        api_key=st.session_state.get("OPENAI_API_KEY"),
                        pdf_content=st.session_state.get("pdf_content", "")
                    )
                    
                    # Prepare input with PDF content if available
                    chain_input = {"input": user_text}
                    if pdf_ctx:
                        chain_input["pdf_content"] = pdf_ctx
                    
                    # Get response with conversation history
                    response = chain.invoke(
                        chain_input,
                        config={"configurable": {"session_id": st.session_state.session_id}}
                    )
                    
                    # Extract text from AIMessage
                    response_text = response.content if hasattr(response, 'content') else str(response)
                
                # Display response with animation
                full_response = display_message_with_animation(response_text, message_placeholder)
                
                # Generate TTS audio if audio input was used
                if st.session_state.audio_input_used:
                    with st.spinner("🔊 Generating audio response..."):
                        selected_voice = st.session_state.get("tts_voice", "nova")
                        audio_response = text_to_speech(
                            full_response,
                            st.session_state.get("OPENAI_API_KEY"),
                            voice=selected_voice
                        )
                    
                    if audio_response:
                        # Display audio player
                        st.audio(audio_response, format="audio/mp3")
                
                # Add to message history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })


if __name__ == "__main__":
    main()