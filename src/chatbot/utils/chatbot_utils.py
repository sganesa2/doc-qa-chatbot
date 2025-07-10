#Chatbot state

from typing import TypedDict, Annotated

from langgraph.graph.message import MessagesState, add_messages, AnyMessage

class ChatbotState(MessagesState):
    run_id: str
    tool_call_messages: Annotated[list[AnyMessage], add_messages]
    current_extraction_state: dict
    current_validation_error: str|None
    workflows_run:list[str]

class ChatbotContext(TypedDict):
    schema: dict