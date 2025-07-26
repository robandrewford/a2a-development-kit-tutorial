# A2A-development-kit-tutorial

[A2A development kit tutorial Source Code](https://github.com/sing1ee/python-a2a-tutorial)

## Table of Contents
- [A2A-development-kit-tutorial Source Code](#python-a2a-tutorial-source-code)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Set up Your Environment](#set-up-your-environment)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running the Application](#running-the-application)
  - [Agent Skills](#agent-skills)
    - [Implementation](#implementation)
    - [Test Run](#test-run)
  - [Agent Card](#agent-card)
    - [Implementation](#implementation-1)
    - [Test Run](#test-run-1)
  - [A2A Server](#a2a-server)
    - [Task Manager](#task-manager)
    - [A2A Server](#a2a-server-1)
    - [Test Run](#test-run-2)
  - [Interacting With Your A2A Server](#interacting-with-your-a2a-server)
  - [Adding Agent Capabilities](#adding-agent-capabilities)
    - [Streaming](#streaming)
  - [Using a Local Ollama Model](#using-a-local-ollama-model)
    - [Requirements](#requirements)
    - [Integrating Ollama into our A2A server](#integrating-ollama-into-our-a2a-server)

## Introduction

In this tutorial, you will build a simple echo A2A server using Python. This barebones implementation will show you all the features A2A has to offer. Following this tutorial, you will be able to add agent functionality using Ollama or Google's Agent Development Kit.

**What you'll learn:**
- The basic concepts behind A2A
- How to create an A2A server in Python
- Interacting with an A2A server
- Add a trained model to act as the agent

## Set up Your Environment

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sing1ee/python-a2a-tutorial.git
    cd python-a2a-tutorial
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

### Running the Application

Once you've set up your environment, you can run the A2A server with the following command:

```bash
uv run my-project
```

>>>>>>> Stashed changes

## Agent Skills

An agent skill is a set of capabilities the agent can perform. Here's an example of what it would look like for our echo agent:

```ts
{
  id: "my-project-echo-skill"
  name: "Echo Tool",
  description: "Echos the input given",
  tags: ["echo", "repeater"],
  examples: ["I will see this echoed back to me"],
  inputModes: ["text"],
  outputModes: ["text"]
}
```

This conforms to the skills section of the Agent Card:

```ts
{
  id: string; // unique identifier for the agent's skill
  name: string; //human readable name of the skill
  // description of the skill - will be used by the client or a human
  // as a hint to understand what the skill does.
  description: string;
  // Set of tag words describing classes of capabilities for this specific
  // skill (e.g. "cooking", "customer support", "billing")
  tags: string[];
  // The set of example scenarios that the skill can perform.
  // Will be used by the client as a hint to understand how the skill can be
  // used. (e.g. "I need a recipe for bread")
  examples?: string[]; // example prompts for tasks
  // The set of interaction modes that the skill supports
  // (if different than the default)
  inputModes?: string[]; // supported mime types for input
  outputModes?: string[]; // supported mime types for output
}
```

### Implementation

Let's create this Agent Skill in code. Open up `src/my-project/__init__.py` and replace the contents with the following code:

```python
from common.types import AgentSkill

def main():
  skill = AgentSkill(
    id="my-project-echo-skill",
    name="Echo Tool",
    description="Echos the input given",
    tags=["echo", "repeater"],
    examples=["I will see this echoed back to me"],
    inputModes=["text"],
    outputModes=["text"],
  )
  print(skill)

if __name__ == "__main__":
  main()
```

### Test Run

Let's give this a run:

```bash
uv run my-project
```

The output should look something like this:

```bash
id='my-project-echo-skill' name='Echo Tool' description='Echos the input given' tags=['echo', 'repeater'] examples=['I will see this echoed back to me'] inputModes=['text'] outputModes=['text']
```

## Agent Card

Now that we have defined our skills, we can create an Agent Card.

Remote Agents are required to publish an Agent Card in JSON format describing the agent's capabilities and skills in addition to authentication mechanisms. In other words, this lets the world know about your agent and how to interact with it.

### Implementation

First lets add some helpers for parsing command line arguments. This will be helpful later for starting our server:

```bash
uv add click
```

And update our code:

```python
import logging

import click
from common.types import AgentSkill, AgentCapabilities, AgentCard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
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

  capabilities = AgentCapabilities(streaming=False)
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

if __name__ == "__main__":
  main()
```

### Test Run

Let's give this a run:

```bash
uv run my-project
```

The output should look something like this:

```bash
INFO:root:id='my-project-echo-skill' name='Echo Tool' description='Echos the input given' tags=['echo', 'repeater'] examples=['I will see this echoed back to me'] inputModes=['text'] outputModes=['text']
INFO:root:name='Echo Agent' description='This agent echos the input given' url='http://localhost:10002/' provider=None version='0.1.0' documentationUrl=None capabilities=AgentCapabilities(streaming=False, pushNotifications=False, stateTransitionHistory=False) authentication=None defaultInputModes=['text'] defaultOutputModes=['text'] skills=[AgentSkill(id='my-project-echo-skill', name='Echo Tool', description='Echos the input given', tags=['echo', 'repeater'], examples=['I will see this echoed back to me'], inputModes=['text'], outputModes=['text'])]
```

## A2A Server

We're almost ready to start our server! We'll be using the `A2AServer` class from our `common` module which under the hood starts a [uvicorn](https://www.uvicorn.org/) server.

### Task Manager

Before we create our server, we need a task manager to handle incoming requests.

We'll be implementing the `TaskManager` interface which requires us to implement `execute_task`. For this tutorial, we'll use the `InMemoryTaskManager` which provides a basic implementation.

Open up `src/my_project/task_manager.py` and add the following code. We will simply return a direct echo response and immediately mark the task complete without any sessions or subscriptions:

```python
from typing import AsyncIterable

from common.task_manager import InMemoryTaskManager
from common.types import (
  Artifact,
  JSONRPCResponse,
  Message,
  SendTaskRequest,
  SendTaskResponse,
  SendTaskStreamingRequest,
  SendTaskStreamingResponse,
  Task,
  TaskState,
  TaskStatus,
  TaskStatusUpdateEvent,
)

class MyAgentTaskManager(InMemoryTaskManager):
  def __init__(self):
    super().__init__()

  async def execute_task(self, body: dict):
      # Our custom logic that simply marks the task as complete
      # and returns the echo text
      return {"status": "completed", "output": body}
```

### A2A Server

With a task manager complete, we can now create our server.

Open up `src/my_project/__init__.py` and add the following code:

```python
# ...
from common.server import A2AServer
from my_project.task_manager import MyAgentTaskManager
# ...
def main(host, port):
  # ...

  task_manager = MyAgentTaskManager()
  server = A2AServer(
    agent_card=agent_card,
    task_manager=task_manager,
    host=host,
    port=port,
  )
  server.start()
```

### Test Run

Let's give this a run:

```bash
uv run my-project
```

The output should look something like this:

```bash
INFO:root:id='my-project-echo-skill' name='Echo Tool' description='Echos the input given' tags=['echo', 'repeater'] examples=['I will see this echoed back to me'] inputModes=['text'] outputModes=['text']
INFO:root:name='Echo Agent' description='This agent echos the input given' url='http://localhost:10002/' provider=None version='0.1.0' documentationUrl=None capabilities=AgentCapabilities(streaming=False, pushNotifications=False, stateTransitionHistory=False) authentication=None defaultInputModes=['text'] defaultOutputModes=['text'] skills=[AgentSkill(id='my-project-echo-skill', name='Echo Tool', description='Echos the input given', tags=['echo', 'repeater'], examples=['I will see this echoed back to me'], inputModes=['text'], outputModes=['text'])]
INFO:     Started server process [582]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:10002 (Press CTRL+C to quit)
```

Congratulations! Your A2A server is now running!

## Interacting With Your A2A Server

You can interact with your A2A server using a tool like `curl` or any HTTP client. Here's an example using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"execute","params":{"input":"hello"},"id":1}' http://localhost:10002/execute
```

You should see a response similar to this:

```json
{"status":"completed","output":{"jsonrpc":"2.0","method":"execute","params":{"input":"hello"},"id":1}}
```

## Adding Agent Capabilities

Now that we have a basic A2A server running, let's add some more functionality. We'll explore how A2A can work asynchronously and stream responses.

### Streaming

This allows clients to subscribe to the server and receive multiple updates instead of a single response. This can be useful for long running agent tasks, or where multiple Artifacts may be streamed back to the client.

First we'll declare our agent as ready for streaming. Open up `src/my_project/__init__.py` and update AgentCapabilities:

```python
# ...
def main(host, port):
  # ...
  capabilities = AgentCapabilities(
    streaming=True
  )
  # ...
```

Now in `src/my_project/task_manager.py` we'll have to implement `on_send_task_subscribe`:

```python
import asyncio
from typing import AsyncIterable
from common.task_manager import InMemoryTaskManager
from common.types import (
  Message,
  SendTaskStreamingRequest,
  SendTaskStreamingResponse,
  TaskState,
  TaskStatus,
  TaskStatusUpdateEvent,
)

class MyAgentTaskManager(InMemoryTaskManager):
  # ...
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

```

Restart your A2A server to pickup the new changes. You can test the streaming functionality with a client that supports Server-Sent Events (SSE).

## Using a Local Ollama Model

Now we get to the exciting part. We're going to add AI to our A2A server.

In this tutorial, we'll be setting up a local Ollama model and integrating it with our A2A server.

### Requirements

We'll be installing `ollama`, `langchain` as well as downloading an ollama model.

1. Download [ollama](https://ollama.com/download)
2. Run an ollama server:

```bash
ollama serve
```

3. Download a model from [this list](https://ollama.com/search). We'll be using `qwen:0.5b` as it's small and easy to run.

```bash
ollama pull qwen:0.5b
```

4. Install `langchain`:

```bash
uv add langchain langchain-ollama langgraph
```

### Integrating Ollama into our A2A server

First open up `src/my_project/__init__.py`:

```python
# ...

@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
@click.option("--ollama-host", default="http://127.0.0.1:11434")
@click.option("--ollama-model", default=None)
def main(host, port, ollama_host, ollama_model):
  # ...
  task_manager = MyAgentTaskManager(
    ollama_host=ollama_host,
    ollama_model=ollama_model,
  )
  # ..
```

Now let's add AI functionality in `src/my_project/agent.py`:

```python
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph

def create_ollama_agent(ollama_base_url: str, ollama_model: str):
  ollama_chat_llm = ChatOllama(
    base_url=ollama_base_url,
    model=ollama_model,
    temperature=0.2
  )
  agent = create_react_agent(ollama_chat_llm, tools=[])
  return agent

async def run_ollama(ollama_agent: CompiledGraph, prompt: str):
  agent_response = await ollama_agent.ainvoke(
    {"messages": [("user", prompt)]}
  )
  message = agent_response["messages"][-1].content
  return str(message)
```

Finally let's call our ollama agent from `src/my_project/task_manager.py`:

```python
# ...
from my_project.agent import create_ollama_agent, run_ollama

class MyAgentTaskManager(InMemoryTaskManager):
  def __init__(
    self,
    ollama_host: str,
    ollama_model: typing.Union[None, str]
  ):
    super().__init__()
    if ollama_model is not None:
      self.ollama_agent = create_ollama_agent(
        ollama_base_url=ollama_host,
        ollama_model=ollama_model
      )
    else:
      self.ollama_agent = None

  async def execute_task(self, body: dict):
    # ...
    input_text = body.get("input")
    if self.ollama_agent is not None and input_text:
      response_text = await run_ollama(ollama_agent=self.ollama_agent, prompt=input_text)
      return {"status": "completed", "output": response_text}

    return {"status": "completed", "output": body}

  # ...
```

Let's test it out!

First rerun our A2A server with the ollama model:

```bash
uv run my-project --ollama-model qwen:0.5b
```

And then send a request using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"execute","params":{"input":"hello"},"id":1}' http://localhost:10002/execute
```

You should see a response from the AI model!

Congratulations! You now have an A2A server generating responses using an AI model!
