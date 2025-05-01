import streamlit as st

# TODO manage the prompt through langfuse, for easier tweaks/testing & observability
import uuid

def live_chat(property_details):
    # Set OpenAI API key from Streamlit secrets
    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            print(message)
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?", key=str(uuid.uuid4())):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        print(st.session_state.messages)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = execute_agent()
        st.session_state.messages.append({"role": "assistant", "content": response})

