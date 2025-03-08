"""Python file to serve as the frontend"""
import sys
import os
sys.path.append(os.path.abspath('.'))

import streamlit as st
import time
import tempfile
from demo_app.components.sidebar import sidebar
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader

def load_chain():
    """Logic for loading the chain you want to use should go here."""
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=st.session_state.get("OPENAI_API_KEY"),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    chain = ConversationChain(llm=llm)
    return chain

def process_pdf(uploaded_file):
    """Process the PDF file and return its content."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        # Write the uploaded file content to the temporary file
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    # Use PyPDFLoader to load the PDF
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    
    # Extract text from all pages
    pdf_text = ""
    for page in pages:
        pdf_text += page.page_content + "\n\n"
    
    # Clean up the temporary file
    os.unlink(tmp_path)
    
    return pdf_text

def get_response_with_pdf_context(chain, query, pdf_content):
    """Get response from LLM with PDF content as context."""
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant that answers questions based on the provided context.
        
        Context from PDF:
        {pdf_content}
        
        Human: {query}
        
        Assistant:"""
    )
    
    # Prepare the prompt with PDF content and query
    formatted_prompt = prompt.format(pdf_content=pdf_content, query=query)
    
    # Get response from the LLM
    response = chain.llm.predict(formatted_prompt)
    
    return response

if __name__ == "__main__":
    st.set_page_config(
        page_title="Chat App: LangChain Demo",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.header("📖 Chat App: LangChain Demo")
    sidebar()
    
    if not st.session_state.get("open_api_key_configured"):
        st.error("Please configure your API Keys!")
    else:
        chain = load_chain()
        
        # Initialize PDF content in session state
        if "pdf_content" not in st.session_state:
            st.session_state["pdf_content"] = ""
        
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "How can I help you? You can upload a PDF document, and I'll use its content to provide better answers."}
            ]
        
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Handle user input
        user_input = st.chat_input("What is your question?", accept_file=st.session_state["file_selection"], file_type=["pdf"])
        
        if user_input:
            pdf_uploaded = False
            query = user_input.text if hasattr(user_input, 'text') else user_input
            
            # Check if files were uploaded
            if hasattr(user_input, 'files') and user_input.files:
                uploaded_files = user_input.files
                
                # Process each uploaded PDF file
                all_pdf_content = ""
                processed_files = []
                
                for uploaded_file in uploaded_files:
                    if uploaded_file.name.lower().endswith('.pdf'):
                        processed_files.append(uploaded_file.name)
                        with st.spinner(f'Processing PDF: {uploaded_file.name}...'):
                            pdf_content = process_pdf(uploaded_file)
                            all_pdf_content += f"\n\n=== Content from: {uploaded_file.name} ===\n\n{pdf_content}"
                            pdf_uploaded = True
                
                if processed_files:
                    file_names = ", ".join(processed_files)
                    st.session_state.messages.append({"role": "user", "content": f"Uploaded PDFs: {file_names}"})
                    with st.chat_message("user"):
                        st.markdown(f"Uploaded PDFs: {file_names}")
                    
                    # Store the concatenated content from all PDFs
                    st.session_state["pdf_content"] = all_pdf_content
                            
                    with st.chat_message("assistant"):
                        st.markdown(f"PDF processed successfully. You can now ask questions about the content of {uploaded_file.name}.")
                    st.session_state.messages.append({"role": "assistant", "content": f"PDF processed successfully. You can now ask questions about the content of {uploaded_file.name}."})
        
            # If there is a text query, process it
            if query:
                st.session_state.messages.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query)
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    with st.spinner('CHAT-BOT is at Work ...'):
                        # If we have PDF content, use it as context
                        if st.session_state["pdf_content"]:
                            assistant_response = get_response_with_pdf_context(chain, query, st.session_state["pdf_content"])
                        else:
                            # Otherwise, use the normal chain
                            assistant_response = chain.invoke(input=query)
                    
                    # Simulate stream of response with milliseconds delay
                    for chunk in assistant_response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})