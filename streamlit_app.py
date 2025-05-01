from typing import Dict, Tuple
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_agents import get_response
from customer_info_processor import CustomerInfoProcessor, CustomerInfo
import uuid

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "customer_info" not in st.session_state:
        st.session_state.customer_info = {}
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False

    if "wants_to_signup" not in st.session_state:
        st.session_state.wants_to_signup = False
    if "info_processor" not in st.session_state:
        st.session_state.info_processor = CustomerInfoProcessor()

def run_chat():
    # Display property info
    st.title("🤖Chat with Uchi AI")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Hello! What brought you here today?"
            }
        ]
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("Hello! What brought you here today?")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Hi, how can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            if "@" in str(prompt):
                st.session_state.wants_to_signup = True
            st.markdown(prompt)

        with st.chat_message("assistant"):
            new_state = get_response(
                messages=st.session_state.messages,
                customer_info=st.session_state.customer_info
            )
            response = new_state["response"]
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.wants_to_signup = new_state.get("wants_to_signup", False)
            st.markdown(response)

        # If user wants to sign up, process the conversation and show signup button
        if st.session_state.wants_to_signup:
            try:
                # Convert messages to BaseMessage format
                base_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        base_messages.append(HumanMessage(content=msg["content"]))
                    else:
                        base_messages.append(AIMessage(content=msg["content"]))

                # Process the conversation
                customer_info = st.session_state.info_processor.process_conversation(base_messages)
                signup_url = st.session_state.info_processor.generate_signup_url(customer_info)

                # Display signup button
                st.link_button("Register with us ✨", url=signup_url)

            except Exception as e:
                st.error(f"Error processing customer information: {str(e)}")

def main():
    initialize_session_state()
    run_chat()

if __name__ == "__main__":
    main()
