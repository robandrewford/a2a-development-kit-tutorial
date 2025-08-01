import logging
import asyncio

import asyncclick as click
from common.types import AgentSkill, AgentCapabilities, AgentCard
from common.server import A2AServer
from my_project.task_manager import MyAgentTaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
@click.option("--google-adk-project-id", default=None)
@click.option("--google-adk-location", default=None)
@click.option("--google-adk-model-id", default=None)
async def amain(host, port, google_adk_project_id, google_adk_location, google_adk_model_id):
  skill = AgentSkill(
    id="my-project-echo-skill",
    name="Echo Tool",
    description="Echos the input given",
    tags=["echo", "repeater"],
    examples=["I will see this echoed back to me"],
    inputModes=["text"],
    outputModes=["text"],
  )
  logging.info(skill)
  capabilities = AgentCapabilities(streaming=True)
  agent_card = AgentCard(
    name="Echo Agent",
    description="This agent echos the input given",
    url=f"http://{host}:{port}/",
    version="0.1.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=capabilities,
    skills=[skill],
  )
  logging.info(agent_card)
  task_manager = MyAgentTaskManager(
    project_id=google_adk_project_id,
    location=google_adk_location,
    model_id=google_adk_model_id,
  )
  server = A2AServer(
    agent_card=agent_card,
    task_manager=task_manager,
    host=host,
    port=port,
  )
  await server.start()

def main():
  amain(_anyio_backend="asyncio")

