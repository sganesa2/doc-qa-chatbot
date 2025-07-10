# Chatbot builder

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from chatbot.utils.chatbot_utils import ChatbotState
from chatbot.utils.chatbot_nodes import (
    human_approval_for_tool_call,
    structured_tool_node,
    advisor_agent,
    construct_inital_message,
    router
)

builder = StateGraph(ChatbotState)

# builder.add_node("human_approval_for_tool_call",human_approval_for_tool_call)
builder.add_node("structured_tool_node",structured_tool_node)
builder.add_node("advisor_agent",advisor_agent)
builder.add_node("construct_inital_message",construct_inital_message)
builder.add_node("router",router)

builder.set_entry_point("router")

checkpointer = MemorySaver()
chatbot_graph = builder.compile(checkpointer=checkpointer)