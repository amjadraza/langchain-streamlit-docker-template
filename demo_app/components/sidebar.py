import streamlit as st

from demo_app.components.faq import faq


def set_open_api_key(api_key: str):
    st.session_state["OPENAI_API_KEY"] = api_key
    st.session_state["open_api_key_configured"] = True
    print('OPENAI API key is Configured Successfully!')


def sidebar():
    with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
        )
        open_api_key_input = st.text_input(
            "Openai API Key",
            type="password",
            placeholder="Paste your API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
            value=st.session_state.get("OPEN_API_KEY", ""),
        )

        if open_api_key_input:
            # print(f'Entered API is {open_api_key_input}')
            set_open_api_key(open_api_key_input)

        if not st.session_state.get("open_api_key_configured"):
            st.error("Please configure your Open API key!")
        else:
            st.markdown("Open API Key Configured!")
        
        # Add dropdown for file selection
        file_selection = st.selectbox(
            "Choose file upload option:",
            options=["No files", "Single", "Multiple"],
            index=0,  # Default to "No files"
            help="Select whether you want to upload no files, a single file, or multiple files"
        )
        
        selection_map = {"No files": False, "Single":True, "Multiple":'multiple'}

        # Store the selection in session state
        st.session_state["file_selection"] = selection_map[file_selection]

        # Handle file upload based on selection
        if file_selection == "Single file":
            uploaded_file = st.file_uploader("Upload a file", type=None)
            if uploaded_file is not None:
                st.session_state["uploaded_files"] = [uploaded_file]
                st.success(f"File uploaded: {uploaded_file.name}")
        elif file_selection == "Multiple files":
            uploaded_files = st.file_uploader("Upload files", type=None, accept_multiple_files=True)
            if uploaded_files:
                st.session_state["uploaded_files"] = uploaded_files
                st.success(f"{len(uploaded_files)} files uploaded")
        else:
            # No files option selected
            st.session_state["uploaded_files"] = []

        st.markdown("---")

        st.markdown("---")
        st.markdown("# About")
        st.markdown(
            "📖 This App is template of lanchain-streamlit-docker example"
        )
        st.markdown("Made by [DR. AMJAD RAZA](https://www.linkedin.com/in/amjadraza/)")
        st.markdown("Credits for Template [hwchase17](https://github.com/hwchase17/langchain-streamlit-template)")
        st.markdown("---")

        faq()
