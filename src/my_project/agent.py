from vertexai.preview.generative_models import GenerativeModel

def create_google_adk_agent(project_id: str, location: str, model_id: str) -> GenerativeModel:
    """Initializes and returns a Google ADK agent."""
    import vertexai
    vertexai.init(project=project_id, location=location)
    
    agent = GenerativeModel(model_id)
    return agent

async def run_google_adk_agent(agent: GenerativeModel, prompt: str) -> str:
    """Runs the Google ADK agent with the given prompt."""
    response = await agent.generate_content_async(prompt)
    return response.text
