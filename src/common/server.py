import logging
import uvicorn
from fastapi import FastAPI
from my_project.task_manager import MyAgentTaskManager
from .types import AgentCard

logger = logging.getLogger(__name__)

class A2AServer:
    def __init__(
        self,
        agent_card: AgentCard,
        task_manager: MyAgentTaskManager,
        host: str = "0.0.0.0",
        port: int = 10002,
    ):
        self.app = FastAPI()
        self.agent_card = agent_card
        self.task_manager = task_manager
        self.host = host
        self.port = port

        self.app.add_api_route("/", self.read_root, methods=["GET"])
        self.app.add_api_route("/execute", self.execute, methods=["POST"])

    def read_root(self):
        return self.agent_card.dict()

    async def execute(self, body: dict):
        return await self.task_manager.execute_task(body)

    async def start(self):
        logger.info(f"Starting server at http://{self.host}:{self.port}")
        config = uvicorn.Config(self.app, host=self.host, port=self.port)
        server = uvicorn.Server(config)
        await server.serve()
