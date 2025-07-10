from typing import Any
from typing_extensions import Annotated
from dataclasses import dataclass
from functools import partial

from pydantic import BaseModel, Field, AfterValidator

@dataclass
class Error:
    err: str

def after_validator(value:Any, name:str)->Error|Any:
    if not value:
        return Error(err=f"Could you enter this field {name}. I was unable to recognize it from your input.")
    return value

class Appointment(BaseModel):
    client_name: Annotated[str|None, AfterValidator(partial(after_validator, name="appointmentschedulingtask.appointment.client_name"))] = Field(description="Name of potential client. If not present, return None")
    date: Annotated[str|None, AfterValidator(partial(after_validator, name="appointmentschedulingtask.appointment.date"))] = Field(description = "Extract the date of appointment. If not present, return None")
    time: Annotated[str|None, AfterValidator(partial(after_validator, name="appointmentschedulingtask.appointment.time"))] = Field(description="Time of appointment. If not present return None")
    notes: Annotated[str|None, AfterValidator(partial(after_validator, name="appointmentschedulingtask.appointment.notes"))] = Field(description="Any additional notes about the appointment. If not present, return None")

class AppointmentSchedulingTask(BaseModel):
    appointments:Annotated[list[Appointment]|None, AfterValidator(partial(after_validator, name="appointmentschedulingtask.appointment"))]  = Field(description="Extract the list of appointments scheduled with potential clients. If it doesn't exist, return None")