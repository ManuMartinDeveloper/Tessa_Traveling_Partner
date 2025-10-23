"""
This module defines the core logic for the conversational travel agent
using LangGraph to create a stateful, cyclical graph with a two-LLM
(worker/supervisor) architecture.
"""
import os
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

# Import the list of available tools that we defined in tools.py
from tools import available_tools

# --- 1. Define the Agent's State ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]

load_dotenv()

def create_travel_agent():
    """
    Creates and configures the conversational travel agent using LangGraph.
    """
    print("🤖 Initializing LangGraph agent with supervisor...")

    # --- 2. The LLMs, Tools, and Prompts ---
    
    # The "Worker" LLM: Responsible for tool calling
    worker_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.environ.get("GEMINI_API_KEY")
    )
    worker_llm_with_tools = worker_llm.bind_tools(available_tools)
    
    # The "Supervisor" LLM: Responsible for generating user-facing responses
    supervisor_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # You could use a more powerful model here if needed
        temperature=0.2,
        google_api_key=os.environ.get("GEMINI_API_KEY")
    )

    # Worker prompt: Minimal instructions for function calling
    worker_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that calls tools based on user input."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Supervisor prompt: Instructs the LLM on how to format the final response
    supervisor_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful travel assistant. Your goal is to provide a final, user-friendly answer based on the conversation history and tool outputs."
            "Summarize the tool results and present the key information clearly."
            "If you have found flight information, list the top 5 options with flight number, price, duration and also your recommendation."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # The agent runnable for the worker
    agent = worker_prompt | worker_llm_with_tools
    
    # The runnable for the supervisor
    summarizer = supervisor_prompt | supervisor_llm


    # --- 3. The Graph Nodes ---
    def call_model(state):
        """The primary 'agent' node. Decides on the next action."""
        response = agent.invoke({"messages": state["messages"]})
        print(f"🧠 Worker LLM response: {response}\n-----------------------------------------")
        return {"messages": [response]}

    tool_node = ToolNode(available_tools)

    def call_summarizer(state):
        """The 'supervisor' node. Generates the final response."""
        # The history now contains the tool output, which we want to summarize.
        # We invoke the summarizer chain with the full message history.
        response = summarizer.invoke({"messages": state["messages"]})
        print(f"🧠 Supervisor LLM final response: {response}\n=========================================")
        return {"messages": [AIMessage(content=response.content)]}


    # --- 4. The Conditional Edges ---
    def should_continue(state):
        """
        Determines the next step after the worker agent's decision.
        
        - If the agent decided to call a tool, we go to the 'action' node.
        - If not, it means we should generate a final response, so we go to the 'summarize' node.
        """
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "continue"
        else:
            # If there are no tool calls, the conversation might be over or need a summary.
            return "end"

    # --- 5. Assemble the Graph ---
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("action", tool_node)
    workflow.add_node("summarize", call_summarizer)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END,
        },
    )

    workflow.add_edge("action", "summarize")
    workflow.add_edge("summarize", END)

    # Compile the graph into a runnable object.
    app = workflow.compile()
    
    print("✅ LangGraph agent with supervisor initialized successfully.")
    return app
