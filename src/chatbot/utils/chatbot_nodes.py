#Chatbot nodes

import os
import yaml
from json import loads
from copy import deepcopy
from typing import List, Tuple, Dict
from functools import lru_cache
from pathlib import Path

from langchain_core.messages import AIMessage
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_core.runnables.config import RunnableConfig
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq

from langgraph.types import Command, Literal, interrupt
from langgraph.graph import END

from chatbot.utils.chatbot_utils import ChatbotState
from chatbot.utils.generic_utils import store_chatbot_run
from chatbot.utils.data_extraction_tool import get_extraction_tool
from chatbot.utils.call_workflow_tool import get_call_workflow_tool

@lru_cache(maxsize=None)
def _advisor_inits()->Tuple[ChatPromptTemplate, List[StructuredTool], Dict[str, StructuredTool], Runnable]:
    chatmodel = ChatGroq(groq_api_key=os.getenv("api_key"), model=os.getenv("model"))
    with open(Path(__file__).parent.joinpath("prompts", "advisor_agent_prompt.yaml"), "r") as f:
        advisor_agent_prompt = ChatPromptTemplate.from_messages([tuple(msg) for msg in yaml.safe_load(f)['prompt']])
    
    advisor_agent_tools = [
        get_extraction_tool(),
        get_call_workflow_tool()
    ]
    advisor_tools_by_name = {tool.name:tool for tool in advisor_agent_tools}

    advisor_model_with_tools = chatmodel.bind_tools(advisor_agent_tools)

    return advisor_agent_prompt, advisor_agent_tools, advisor_tools_by_name, advisor_model_with_tools

def human_approval_for_tool_call(state:ChatbotState)->Command[Literal['structured_tool_node']]:
    human_approval = interrupt(state['messages'][-1].content)
    return Command(
        update = {"messages":[("human", human_approval)]},
        goto = "structured_tool_node"
    )

def structured_tool_node(state:ChatbotState)->Command[Literal['router', END]]:
    _, _, advisor_tools_by_name, _ = _advisor_inits()
    msg1,msg2=None,None
    with open(Path(__file__).parent.joinpath("prompts", "const_messages.yaml"), "r") as f:
        messages = yaml.safe_load(f)['messages']
    exit_message = messages['exit_msg']

    tool_calls = state['tool_call_messages'][-1].tool_calls

    workflows_called = []
    extraction_tool_calls = [tool_call for tool_call in tool_calls if tool_call['name'] == "invoke_extraction_model"]
    call_workflow_tool_calls = [tool_call for tool_call in tool_calls if tool_call['name'] == "call_workflow"]

    for tool_call in call_workflow_tool_calls:
        tool = advisor_tools_by_name[tool_call['name']]
        human_approval = interrupt(state['messages'][-1].content)
        tool_response = tool.invoke(tool_call['args'])
        workflows_called.append(tool_response)

    if workflows_called:
        msg1 = messages['msg1'].format(workflows_called)

    if extraction_tool_calls:
        tool = advisor_tools_by_name[extraction_tool_calls[-1]['name']]
        tool_response = tool.invoke(extraction_tool_calls[-1]['args'])
        if not tool_response['current_validation_error']:
            return Command(
                update={
                    "current_extraction_state":tool_response["structured_output"],
                    "current_validation_error":None,
                    "messages":[("ai", " ".join([msg1,exit_message]))] if msg1 else [("ai", exit_message)],
                    "workflows_run":workflows_called
                },
                goto=END
            )
        state['current_extraction_state'] = tool_response["structured_output"]
        msg2 = messages['msg2'].format(tool_response['current_validation_error'])
    

    if msg1 and msg2:
        return Command(
            update={"current_validation_error":", ".join([msg1,msg2]), "workflows_run":workflows_called},
            goto="router"
        )
    if msg2:
        return Command(
            update={"current_validation_error":msg2},
            goto="router"
        )
    if msg1:
        return Command(
            update={"messages":[("ai", " ".join([msg1,exit_message]))], "workflows_run":workflows_called},
            goto=END
        )

def advisor_agent(state:ChatbotState, config:RunnableConfig)->Command[Literal['structured_tool_node', END]]:
    chatbot_context = config['configurable']['chatbot_context']
    advisor_agent_prompt, _, _, advisor_model_with_tools = _advisor_inits()

    state_copy = deepcopy(state)
    state_copy['messages'] = loads(ChatPromptValue(messages=state_copy['messages']).model_dump_json())['messages']
    state_copy['tool_call_messages'] = loads(ChatPromptValue(messages=state_copy['tool_call_messages']).model_dump_json())['messages']
    store_chatbot_run(run_id=state['run_id'],chatbot_run={"state":state_copy, "config":chatbot_context})

    runnable = advisor_agent_prompt|advisor_model_with_tools

    advisor_agent_response = runnable.invoke({
            "run_id":state['run_id'],
            "user_query":state['messages'][-1].content,
            "partially_extracted_output":state['current_extraction_state'],
            "conversation_history":state['messages'],
            "schema":chatbot_context['schema']
    })
    if advisor_agent_response.tool_calls:
        return Command(
            update={"tool_call_messages":[advisor_agent_response], "messages":[("ai", "Do you want to approve all tool calls or be prompted to approved each tool call? (approve_all/prompt_for_approval)")]},
            goto="human_approval_for_tool_call"
        )
    return Command(
        update={
            "messages":[("ai", advisor_agent_response.content)]
        },
        goto=END
    )

def construct_inital_message(state:ChatbotState, config:RunnableConfig)->Command[Literal[END]]:
    chatbot_context = config['configurable']['chatbot_context']

    model = ChatGroq(groq_api_key=os.getenv("api_key"), model=os.getenv("model"))
    with open(Path(__file__).parent.joinpath("prompts", "initial_message_prompt.yaml"), "r") as f:
        initial_message_prompt = ChatPromptTemplate.from_messages([tuple(msg) for msg in yaml.safe_load(f)['prompt']])
    
    runnable = initial_message_prompt|model

    inital_message = runnable.invoke({
        "schema":chatbot_context["schema"]
    })

    return Command(
        update={"messages":[("ai", inital_message.content)]},
        goto=END
    )

def router(state:ChatbotState, config:RunnableConfig)->Command[Literal['advisor_agent', 'construct_inital_message', END]]:

    if state.get('current_validation_error'):
        state["messages"].append(AIMessage(content=state['current_validation_error']))
        state['current_validation_error'] = None

    if state['messages']:
        if dict(state['messages'][-1])['type']=="human":
            return Command(
                goto = 'advisor_agent'
            )
        else:
            return Command(
                goto = END
            )
    else:
        return Command(
            goto="construct_inital_message"
        )