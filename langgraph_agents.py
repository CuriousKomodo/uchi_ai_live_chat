from typing import TypedDict, Annotated, Sequence
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ['SSL_CERT_FILE'] = "/etc/ssl/cert.pem"

# Define the state schema
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The conversation history"]
    customer_info: Annotated[dict, "Customer information extracted from conversation"]
    current_agent: Annotated[str, "The current agent handling the conversation"]

# Initialize the language model
llm = ChatOpenAI(model="gpt-4")

def engagement_agent(state: AgentState) -> AgentState:
    """Agent that engages with customers and introduces the product."""
    messages = state["messages"]
    
    # Get the last human message
    last_message = messages[-1].content if messages else "Hello! I'm Uchi AI, your personal property search assistant. What's your first name?"
    
    # Generate response
    response = llm.invoke([
        {"role": "system", "content": """
        You are Uchi AI, an assistant helping customers find properties to buy.
        Your role is to:
        1. Greet customers warmly and ask about their motivation
        2. Ask if they are first-time buyers or buying alone/with someone
        3. Introduce Uchi AI's features in a non-sales way
        4. Check if they'd like to sign up
        
        Keep responses under 200 words and ask one question at a time.
        Be friendly and human-like. Avoid sales language.
        """},
        {"role": "user", "content": last_message}
    ])
    
    # Update state
    state["messages"].append(AIMessage(content=response.content))
    state["current_agent"] = "note_keeper"
    
    return {
        "current_agent": "note_keeper",
        "message": state["messages"]
    }

def note_keeper_agent(state: AgentState) -> AgentState:
    """Agent that extracts and stores customer information."""
    messages = state["messages"]
    
    # Extract information from conversation
    extraction_prompt = f"""
    Extract the following information from this conversation:
    {[msg.content for msg in messages]}
    
    Return a JSON with these fields:
    - motivation: str (why they want to buy)
    - is_first_time_buyer: bool
    - is_buying_alone: bool
    - is_happy_to_sign_up: bool
    
    If any information is missing, return null for that field.
    """
    
    extracted_info = llm.invoke([
        {"role": "system", "content": "Extract customer information from the conversation."},
        {"role": "user", "content": extraction_prompt}
    ])
    
    # Update customer info in state
    state["customer_info"] = extracted_info.content
    state["current_agent"] = "engagement"
    
    return {
        "customer_info": extracted_info.content,
        "current_agent": "engagement"
    }

def should_continue(state: AgentState) -> bool:
    """Determine if the conversation should continue."""
    if "customer_info" in state:
        customer_info = state["customer_info"]
        # Continue if any required information is missing
        return any(v is None for v in customer_info.values())
    else:
        return True

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("engagement", engagement_agent)
workflow.add_node("note_keeper", note_keeper_agent)

# Add edges
workflow.add_edge("engagement", "note_keeper")
workflow.add_edge("note_keeper", "engagement")

# Set entry point
workflow.set_entry_point("engagement")

# Compile the graph
app = workflow.compile()

def run_conversation(initial_message: str):
    """Run the conversation with the initial message."""
    initial_state = {
        "messages": [HumanMessage(content=initial_message)],
        "customer_info": {
            "motivation": None,
            "is_first_time_buyer": None,
            "is_buying_alone": None,
            "is_happy_to_sign_up": None
        },
        "current_agent": "engagement"
    }
    
    # Run the graph
    for output in app.stream(initial_state):
        print(output)
        
        # Check if we should continue
        if not should_continue(output):
            print("\nAll required information has been collected!")
            print("Customer information:", output["customer_info"])
            break
            
        # Get next user input
        user_input = input("Your response: ")
        output["messages"].append(HumanMessage(content=user_input))
    return output

if __name__ == "__main__":
    # Example usage
    result = run_conversation("I want to buy a property") 