# Extraction Input state, output state

from typing import TypedDict

from pydantic import BaseModel

from langgraph.graph.message import AnyMessage

class ExtractionInput(TypedDict):
    ai_message: AnyMessage
    user_message: AnyMessage

class ExtractionOutput(TypedDict):
    structured_output: dict
    current_validation_error: str|None

class ExtractionContext(TypedDict):
    schema: BaseModel
    partially_extracted_output:dict

def construct_extraction_input(chatbot_state:dict)->ExtractionInput:
    state, _ = chatbot_state['state'], chatbot_state['config']
    return ExtractionInput(
        ai_message= state['messages'][-2]['content'],
        user_message= state['messages'][-1]['content']
    )

def construct_extraction_context(chatbot_state:dict)->ExtractionContext:
    state, _ = chatbot_state['state'], chatbot_state['config']
    return ExtractionContext(
        partially_extracted_output= state['current_extraction_state']
    )