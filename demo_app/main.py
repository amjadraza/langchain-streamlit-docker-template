"""Python file to serve as the frontend"""
import sys
import os

sys.path.append(os.path.abspath('.'))

import streamlit as st
import time
from demo_app.components.sidebar import sidebar
from langchain.chains import ConversationChain
from langchain.llms import OpenAI


def load_chain():
    """Logic for loading the chain you want to use should go here."""
    llm = OpenAI(openai_api_key=st.session_state.get("OPENAI_API_KEY"), temperature=0)
    chain = ConversationChain(llm=llm)
    return chain


def get_text():
    input_text = st.text_input("You: ", "Hello, how are you?", key="input")
    return input_text


if __name__ == "__main__":

    st.set_page_config(
        page_title="Chat App: LangChain Demo",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded", )
    st.header("📖 Chat App: LangChain Demo")
    sidebar()

    if not st.session_state.get("open_api_key_configured"):
        st.error("Please configure your API Keys!")
    else:
        chain = load_chain()

        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "How can I help you?"}]

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_input := st.chat_input("What is your question?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                with st.spinner('CHAT-BOT is at Work ...'):
                    assistant_response = output = chain.run(input=user_input)
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

