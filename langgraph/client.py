import asyncio
import httpx
import uuid
from typing import Any
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest
)
from rich import print

PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
EXTENDED_AGENT_CARD_PATH = 'agent/authenticatedExtendedCard'
BASE_URL = 'http://0.0.0.0:9999'

async def main():
    async with httpx.AsyncClient() as httpx_client:
        # Step 1: Agent resolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=BASE_URL
        )
        final_agent_card_to_use : AgentCard | None = None

        try:
            # Step 2: Public agent
            _public_agent = await resolver.get_agent_card()
            final_agent_card_to_use = _public_agent

            if _public_agent.supportsAuthenticatedExtendedCard:
                try:
                    # Step 3: Extended agent
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs = {'headers': {'Authorization': 'dummy-token-for-extended-card'}}
                    )
                    final_agent_card_to_use = _extended_card
                except Exception as e:
                    print(
                        "Failed to fetch the Extended card."
                        "Continuing with the Public card:\n"
                        f"{e}"
                    )
            elif (_public_agent):
                print("Extended agent card not supported")
        except Exception as e:
            print(
                "Failed to fetch the Public card."
                f"{e}"
            )
        
        # Step 4: Client
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=final_agent_card_to_use
        )

        # Step 5: payload
        payload = {
            "message": {
                "role": "user",
                "parts": [
                    {"kind": "text", "text": "How much is 10 USD in INR?"}
                ],
                "messageId": uuid.uuid4().hex
            }
        }

        # Step 5a: Request-Response
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(**payload)           
        )
        response = await client.send_message(request)
        print(f"-----------REQUEST-----------") 
        print( request.model_dump(mode='json', exclude_none=True))
        print(f"-----------RESPONSE-----------") 
        print(response.model_dump(mode='json', exclude_none=True))

        # # Step 5b: Multiturn Request-Response
        first_payload = {
            "message": {
                "role": "user",
                "parts": [
                    {"kind": "text", "text": "How much is 10 USD?"}
                ],
                "messageId": uuid.uuid4().hex
            }
        }
        first_request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(**first_payload)           
        )
        first_response = await client.send_message(first_request)
        print(f"-----------1st RESPONSE-----------") 
        print(first_response.model_dump(mode='json', exclude_none=True))

        taskId = first_response.root.result.id
        contextId = first_response.root.result.contextId

        second_payload = {
            "message": {
                "role": "user",
                "parts": [
                    {"kind": "text", "text": "CAD"}
                ],
                "messageId": uuid.uuid4().hex,
                "taskId":taskId,
                "contextId": contextId
            }
        }
        second_request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(**second_payload)           
        )
        second_response = await client.send_message(second_request)
        print(f"-----------2nd RESPONSE-----------") 
        print(second_response.model_dump(mode='json', exclude_none=True))
        

if __name__ == "__main__":
    asyncio.run(main())