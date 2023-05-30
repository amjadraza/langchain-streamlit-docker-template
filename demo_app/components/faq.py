# flake8: noqa
import streamlit as st


def faq():
    st.markdown(
        """
# FAQ
## How to use App Template?
This is a basic template to set up Langchain Demo App with Docker


## What Libraries are being use?
Basic Setup is using langchain, streamlit and openai.

## How to test the APP?
Set up the OpenAI API keys and run the App

## Disclaimer?
This is a template App, when using with openai_api key, you will be charged a nominal fee depending
on number of prompts etc.

"""
    )
