#Generic Uitl functions

from pathlib import Path
from json import load, dump
from typing import Generator

from pydantic import BaseModel

from chatbot.utils.workflow_schema import Error

chatbot_runs_path = Path(__file__).parent.parent.joinpath("chatbot_runs.json")

def get_chatbot_run(run_id:str):
    if not chatbot_runs_path.exists():
        raise FileNotFoundError(f"Chatbot runs file not found at {chatbot_runs_path}")
    with open(chatbot_runs_path,'r') as f_read:
        chatbot_run = load(f_read)[run_id]
    return chatbot_run

def store_chatbot_run(run_id:str, chatbot_run:dict)->None:
    
    with open(chatbot_runs_path,'w') as f_write:
        dump({},f_write)

    with open(chatbot_runs_path,'r') as f_read:
        all_chatbot_runs = load(f_read)
    with open(chatbot_runs_path,'w') as f_write:
        dump({**all_chatbot_runs,run_id:chatbot_run},f_write)

def field_iterator(output:BaseModel)->Generator[str, None, None]:
    for _,value in output:
        if isinstance(value, Error):
            yield value.err
        elif isinstance(value, BaseModel):
            field_iterator(value)
        elif isinstance(value, list):
            for v in value:
                if isinstance(v,BaseModel):
                    yield from field_iterator(v)
        else:
            continue
