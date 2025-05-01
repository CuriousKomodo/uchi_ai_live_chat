import streamlit as st
from langgraph_agents import run_conversation
import uuid

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "customer_info" not in st.session_state:
        st.session_state.customer_info = {
            "motivation": None,
            "is_first_time_buyer": None,
            "is_buying_alone": None,
            "is_happy_to_sign_up": None
        }
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False

def live_chat():
    initialize_session_state()
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # If conversation hasn't started, show initial message
    if not st.session_state.conversation_started:
        initial_message = "I want to buy a property"
        st.session_state.messages.append({"role": "user", "content": initial_message})
        with st.chat_message("user"):
            st.markdown(initial_message)
        
        # Run the agent with initial message
        result = run_conversation(initial_message)
        st.session_state.messages.append({"role": "assistant", "content": result["messages"][-1].content})
        st.session_state.customer_info = result["customer_info"]
        st.session_state.conversation_started = True
        
        # Display assistant's response
        with st.chat_message("assistant"):
            st.markdown(result["messages"][-1].content)
    
    # Accept user input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Run the agent with user's message
        result = run_conversation(prompt)
        
        # Update session state with new information
        st.session_state.customer_info = result["customer_info"]
        
        # Display assistant's response
        with st.chat_message("assistant"):
            st.markdown(result["messages"][-1].content)
            st.session_state.messages.append({"role": "assistant", "content": result["messages"][-1].content})
        
        # If all information is collected, show signup link
        if all(v is not None for v in st.session_state.customer_info.values()):
            st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <a href='https://uchi-survey.streamlit.app' target='_blank' style='background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>
                    Click here to sign up for Uchi AI!
                </a>
            </div>
            """, unsafe_allow_html=True)

def main():
    st.title("Uchi AI - Your Personal Property Search Assistant")
    st.markdown("""
    Welcome to Uchi AI! I'm here to help you find your dream home. 
    Let's start by getting to know your preferences and requirements.
    """)
    
    live_chat()
    
    # Display collected information in a sidebar
    with st.sidebar:
        st.header("Collected Information")
        if st.session_state.customer_info:
            for key, value in st.session_state.customer_info.items():
                if value is not None:
                    st.write(f"{key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    main()

