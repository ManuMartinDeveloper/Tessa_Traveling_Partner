import streamlit as st
import os
from llm_graph import create_travel_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
load_dotenv()

def generate_response(user_input):
  """Fetches user input, interacts with Groq API, and returns the generated response."""
  app = create_travel_agent()

  completion = app.invoke({"messages": [HumanMessage(content=user_input) ]})
#   response = ""
#   for chunk in completion:
#       response += chunk.choices[0].delta.content or ""
  return completion['messages'][-1].content

st.title("Tessa - Your Travel Booking Assistant ✈️")
st.subheader("I can help you search flights and hotels effortlessly!")

user_input = st.text_input("Enter your travel query here:")



if user_input:
  response = generate_response(user_input)
  st.write(response)
  st.markdown("---")  # Add a separator for clarity

footer_placeholder = st.empty()
with footer_placeholder:
    st.markdown(
        """
        <div style="text-align: right; font-size: 12px;">
            © 2024 Manu Martin | All Rights Reserved
        </div>
        """,
        unsafe_allow_html=True,
    )