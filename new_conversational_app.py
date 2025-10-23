import streamlit as st
import os
from llm_graph_update import create_travel_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
load_dotenv()

st.set_page_config(
    page_title="Tessa - Travel Booking Assistant",
    page_icon="✈️",
    layout="wide",
)

st.title("Tessa - Your Travel Booking Assistant ✈️")
st.subheader("I can help you search flights and hotels effortlessly!")

# --- Setup Session State ---
# This runs only once per session
if "agent" not in st.session_state:
    st.session_state.agent = create_travel_agent()

if "messages" not in st.session_state:
    st.session_state.messages = [AIMessage(content="Hi! How can I help you with your travel plans today?")]

# --- Display existing chat history ---
for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

# --- Handle new user input ---
user_input = st.chat_input("Enter your travel query here:")

if user_input:
    # Add user message to state and display it
    st.session_state.messages.append(HumanMessage(content=user_input))
    st.chat_message("user").write(user_input)
    
    # Invoke the agent with the *entire* message history
    response_data = st.session_state.agent.invoke({"messages": st.session_state.messages})
    
    # Get the final AI response
    # response = response_data['messages'][-1].content
    response = response_data['messages'][-1]
    reply = ""
    try:
        print("Response content type:", type(response.content))
        if isinstance(response.content, str):
            print("String response detected")
            # Add AI response to state and display it
            st.session_state.messages.append(response)
            reply = response.content
            

        elif response.content[0].get("type")=="text":
            print("Text response detected")
            reply = response.content[0].get("text")
            response.content = response.content[0].get("text")
            st.session_state.messages.append(response)
            
            
    
    except:
        pass

    print("Response:", response.content, "\n-------------------------\n")
    print("Full response data:", response_data, "\n=========================\n")
    print("reply:", reply, "\n*************************\n")
    st.chat_message("assistant").write(reply)
    st.markdown("---")  # Add a separator for clarity

    


footer_placeholder = st.empty()
with footer_placeholder:
    st.markdown(
        """
        <div style="text-align: right; font-size: 12px;">
            © 2025 Manu Martin | All Rights Reserved
        </div>
        """,
        unsafe_allow_html=True,
    )