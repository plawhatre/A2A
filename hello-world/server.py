import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities
)

from agent_executor import HelloWorldAgentExecutor

if __name__ == "__main__":
    # Step 1: Agent Skills
    skill = AgentSkill(
        id='hello_world',
        name='returns hello world',
        description='just returns hello world',
        tags=['hello world'],
        examples=['hi', 'hello world']
    )
    extended_skills = AgentSkill(
        id='super_hello_world',
        name='returns a super hello world',
        description='a more enthusiastic greeting for authenticated users',
        tags=['hello world', 'super', 'extended'],
        examples=['super hi', 'give me a super hello']
    )

    # Step 2: Agent Card
    public_agent_card = AgentCard(
        name='hello world agent',
        description='just a hello world agent',
        url='http://localhost:9999/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        supportsAuthenticatedExtendedCard=True
    )
    extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'super hello world agent',
            'description': 'hello world agent for authenticatd users',
            'version': '1.0.1',
            'skills': [
                skill,
                extended_skills
            ]
        }
    )

    # Step 3: Request handler
    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore()
    )

    # Step 4: Server
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=public_agent_card,
        extended_agent_card=extended_agent_card
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)