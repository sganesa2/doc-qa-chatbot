# call workflow tool
import time
import yaml
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from langchain_core.tools import StructuredTool

from chatbot.utils.generic_utils import get_chatbot_run


class CallWorkflowToolInput(BaseModel):
    run_id:str
    workflow_name:Literal["workflow_1", "workflow_2", "workflow_3"]

def _call_workflow(run_id:str, workflow_name:Literal["workflow_1", "workflow_2", "workflow_3"])->str:
    #inputs for api call
    chatbot_state = get_chatbot_run(run_id)
    #mimic workflow api call
    time.sleep(2)
    return workflow_name

def get_call_workflow_tool()->StructuredTool:
    with open(Path(__file__).parent.joinpath("prompts", "call_workflow_tool_desc.yaml"), "r") as f:
        description = yaml.safe_load(f)['description']
    call_workflow = StructuredTool.from_function(
        func = _call_workflow,
        name = "call_workflow",
        description = description,
        args_schema = CallWorkflowToolInput,
        return_direct = True
    )
    return call_workflow
    