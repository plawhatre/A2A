import httpx
import uuid
from typing import Callable

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    Task,
    Message,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    MessageSendParams,
    SendStreamingMessageRequest,
    SendMessageRequest,
    JSONRPCErrorResponse
)

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]


class RemoteAgentConenction:
    """
    A class to hold connections to remote agents
    """
    def __init__(self, client: httpx.AsyncClient, agent_card: AgentCard):
        self.agent_client = A2AClient(client, agent_card)
        self.card = agent_card
        self.pending_tasks = set() #Is this needed?

    def get_agent(self) -> AgentCard:
        return self.card
    
    async def send_message(
            self,
            request: MessageSendParams,
            task_callbacks: TaskUpdateCallback | None
    ):  
        # Path 1: For Streaming
        if self.card.capabilities.streaming:
            task = None
            async for response in self.agent_client.send_message_streaming(
                SendStreamingMessageRequest(
                    id=str(uuid.uuid4()),
                    params=request
                )
            ):
                # Path 1.1: If error occurs
                if not response.root.result:
                    return response.root.error
                
                # Path 1.2: If error doesn't occur

                # Path 1.2.a: Return Message
                event = response.root.result
                if isinstance(event, Message):
                    return event
                
                # Path 1.2.b: Task + Update cycle
                if task_callbacks and event:
                    task =task_callbacks(event, self.card)
                if hasattr(event, 'final') and event.final:
                    break
            return task

                
                
        # Path 2: For Non-Streaming
        else:
            response = await self.agent_client.send_message(
                SendMessageRequest(
                    id=str(uuid.uuid4()),
                    params=request
                )
            )
            # Path 2.1: If error occurs
            if isinstance(response.root.result, JSONRPCErrorResponse):
                return response.root.error
            
            # Path 2.2: If error doesn't occur

            # Path 2.2.a: Return Message
            if isinstance(response.root.result, Message):
                return response.root.result
            
            # path 2.2.b: Task callback
            if task_callbacks:
                task_callbacks(response.root.result, self.card)
            return response.root.result
                
