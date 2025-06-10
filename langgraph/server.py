import os
import sys
import httpx
import click
import uvicorn
from rich import print

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities
)
from agent import SUPPORTED_CONTENT_TYPES
from agent_executor import CurrencyAgentExecutor

@click.command()
@click.option('--host', 'host', default='0.0.0.0')
@click.option('--port', 'port', default=9999)
def main(host, port):
    """Start the Currency Agent server"""
    try:
        # Step 1: Capabilities
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
        
        # Step 2: Agent Skills
        skill = AgentSkill(
            id='convert currency',
            name='Currency exchange rate tool',
            description='Helps with exchange values between various currencies',
            tags=['currency conversion', 'currency exchange'],
            examples=['What is the exchange rate between USD and GBP?']
        )
        
        # Step 3: Agent Card
        agent_card = AgentCard(
            name='Currency agent',
            description='Helps with exchange rate for currencies',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        
        # Step 4: Client
        httpx_client = httpx.AsyncClient()
        
        # Step 5: Request handler
        request_handler = DefaultRequestHandler(
            agent_executor=CurrencyAgentExecutor(),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client)
        )
        
        # Step 6:Server
        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )

        # Step 7: Run the server
        uvicorn.run(server.build(), host=host, port=port)

    except Exception as e:
        print("Error occured:")
        print(e)
if __name__ == "__main__":
    main()

