# Data extraction tool

import os
import yaml
from pathlib import Path

from pydantic import BaseModel
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from chatbot.utils.generic_utils import get_chatbot_run, field_iterator
from chatbot.utils.data_extraction_utils import (
    construct_extraction_input, 
    construct_extraction_context, 
    ExtractionOutput
)
from chatbot.utils.workflow_schema import AppointmentSchedulingTask

class ExtractionToolInput(BaseModel):
    run_id:str
    
def _invoke_extraction_model(run_id:str)->ExtractionOutput:
    chatbot_run = get_chatbot_run(run_id=run_id)
    chatmodel = ChatGroq(groq_api_key=os.getenv("api_key"), model=os.getenv("model"))
    extraction_model = chatmodel.with_structured_output(AppointmentSchedulingTask)

    extraction_input, extraction_context = construct_extraction_input(chatbot_run), construct_extraction_context(chatbot_run)
    
    with open(Path(__file__).parent.joinpath("prompts", "extraction_prompt.yaml"), "r") as f:
        structured_output_prompt = ChatPromptTemplate.from_messages([tuple(msg) for msg in yaml.safe_load(f)['prompt']])
    runnable = structured_output_prompt|extraction_model

    structured_response = runnable.invoke({
        "user_message":extraction_input["user_message"],
        "ai_message":extraction_input["ai_message"], 
        "partially_extracted_output":extraction_context["partially_extracted_output"]
    })
    json_output = structured_response.model_dump_json()

    for current_validation_error in field_iterator(structured_response):
        return ExtractionOutput(
            structured_output = json_output,
            current_validation_error = current_validation_error
        )
    return ExtractionOutput(
        structured_output = json_output,
        current_validation_error = None
    )

def get_extraction_tool()->StructuredTool:
    with open(Path(__file__).parent.joinpath("prompts", "extraction_tool_desc.yaml"), "r") as f:
        description = yaml.safe_load(f)['description']
    invoke_extraction_model = StructuredTool.from_function(
        func = _invoke_extraction_model,
        name = "invoke_extraction_model",
        description = description,
        args_schema = ExtractionToolInput,
        return_direct = True
    )
    return invoke_extraction_model

