import asyncio
from typing import AsyncIterable

from common.task_manager import InMemoryTaskManager
from common.types import (
  Artifact,
  Message,
  SendTaskRequest,
  SendTaskResponse,
  SendTaskStreamingRequest,
  SendTaskStreamingResponse,
  Task,
  TaskState,
  TaskStatus,
)
from my_project.agent import create_google_adk_agent, run_google_adk_agent


class MyAgentTaskManager(InMemoryTaskManager):
  def __init__(self, project_id: str, location: str, model_id: str):
    super().__init__()
    if model_id:
      self.google_adk_agent = create_google_adk_agent(
        project_id=project_id,
        location=location,
        model_id=model_id
      )
    else:
      self.google_adk_agent = None

  async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
    # Upsert a task stored by InMemoryTaskManager
    await self.upsert_task(request.params)

    task_id = request.params.id
    # Our custom logic that simply marks the task as complete
    # and returns the echo text
    received_text = request.params.message.parts[0].text
    response_text = f"on_send_task received: {received_text}"
    if self.google_adk_agent:
      response_text = await run_google_adk_agent(agent=self.google_adk_agent, prompt=received_text)
    print(f"response_text: {response_text}")
    task = await self._update_task(
      task_id=task_id,
      task_state=TaskState.COMPLETED,
      response_text=response_text
    )

    # Send the response
    return SendTaskResponse(id=request.id, result=task)

  async def on_send_task_subscribe(
    self,
    request: SendTaskStreamingRequest
  ) -> AsyncIterable[SendTaskStreamingResponse]:
    # This is a simplified example of streaming.
    # In a real-world scenario, you would handle the task and session management.
    for i in range(3):
        yield SendTaskStreamingResponse(
            id=request.id,
            result={
                "status": "working",
                "message": f"Streaming message {i+1}"
            }
        )
        await asyncio.sleep(1)
    yield SendTaskStreamingResponse(
        id=request.id,
        result={
            "status": "completed",
            "message": "Streaming complete"
        }
    )

  async def _update_task(
    self,
    task_id: str,
    task_state: TaskState,
    response_text: str,
  ) -> Task:
    task = self.tasks[task_id]
    agent_response_parts = [
      {
        "type": "text",
        "text": response_text,
      }
    ]
    task.status = TaskStatus(
      state=task_state,
      message=Message(
        role="agent",
        parts=agent_response_parts,
      )
    )
    task.artifacts = [
      Artifact(
        parts=agent_response_parts,
      )
    ]
    return task
