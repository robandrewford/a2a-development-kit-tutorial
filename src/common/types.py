from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    inputModes: List[str]
    outputModes: List[str]

class AgentCapabilities(BaseModel):
    streaming: bool

class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    capabilities: AgentCapabilities
    skills: List[AgentSkill]

class Artifact(BaseModel):
    parts: List[dict]

class JSONRPCResponse(BaseModel):
    id: str
    result: dict

class Message(BaseModel):
    role: str
    parts: List[dict]

class SendTaskRequest(BaseModel):
    id: str
    params: dict

class SendTaskResponse(BaseModel):
    id: str
    result: dict

class SendTaskStreamingRequest(BaseModel):
    id: str
    params: dict

class SendTaskStreamingResponse(BaseModel):
    id: str
    result: dict

class Task(BaseModel):
    id: str
    status: dict
    artifacts: List[Artifact]

class TaskState(str, Enum):
    COMPLETED = "completed"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"

class TaskStatus(BaseModel):
    state: str
    message: Message

class TaskStatusUpdateEvent(BaseModel):
    id: str
    status: TaskStatus
    final: bool
