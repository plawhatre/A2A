import asyncio
import base64
import httpx
import json
from uuid import uuid4

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    MessageSendConfiguration,
    Message,
    Task,
    Part,
    TaskState,
    TextPart,
    DataPart
)

from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from remote_agent_connection import RemoteAgentConenction, TaskUpdateCallback

class HostAgent:
    """The Host Agent
    This is the agent responsible for choosing the remote agent
    to send task to and coordinate their work.
    """
    def __init__(
            self,
            remote_agent_addresses: list[str],
            httpx_client: httpx.AsyncClient,
            task_callback: TaskUpdateCallback | None
    ):
        self.httpx_client = httpx_client
        self.task_callback  = task_callback
        
        self.remote_agent_connections: dict[str, RemoteAgentConenction] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''

        loop = asyncio.get_running_loop()
        loop.create_task(self.init_remote_agent_addresses(remote_agent_addresses))

    async def init_remote_agent_addresses(self, remote_agent_addresses: list[str]):
        async with asyncio.TaskGroup() as task_group:
            for address in remote_agent_addresses:
                task_group.create_task(self.retrieve_card(address))

    async def retrieve_card(self, address: str):
        card_resolver = A2ACardResolver(self.httpx_client, address)
        card = await card_resolver.get_agent_card()
        self.register_agent_card(card)

    def register_agent_card(self, card: AgentCard):
        remote_connection = RemoteAgentConenction(self.httpx_client, card)
        
        self.remote_agent_connections[card.name] = remote_connection
        self.cards[card.name] = card

        agent_info = []
        for remote_agent in self.list_remote_agents():
            agent_info.append(json.dumps(remote_agent))
        self.agents = "\n".join(agent_info)

    def create_agent(self) -> Agent:
        agent = Agent(
            model='gemini-2.0-flash-001',
            name='host_agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                'This agent orchestrates the decomposition of the user request '
                'onto tasks that can be performed by the child agents.'
            ),
            tools=[self.list_remote_agents, self.send_message]
        )
        
    def root_instruction(self, context: ReadonlyContext):
        current_agent = self.check_state(context)
        instruction = (
            "You are an expert deligator who can deligate the user request to the "
            "appropriate remote agents."
            "\n\n"

            "Discovery:\n"
            "-You can use `list_remote_agents` to list the available remote agents you "
            "can use to deligate the task."
            "\n\n"

            "Execution:\n\n"
            "-For actionable request, you can `send_message` to interact with "
            "remote agents to take action."
            "\n\n"

            "Be sure to include the remote agent name when you repsond to the user."
            "\n\n"

            "Please rely on the tools to address the request, and don't make up the response. "
            "If you are not sure, please ask the user for more details. "
            "Focus on the most recent parts of the conversation primarily."
            "\n\n"

            "Agents:\n"
            f"{self.agents}"
            "\n\n"

            f"Current agent: {current_agent['active_agent']}"
        )
        return instruction
    
    def check_state(self, context: ReadonlyContext):
        state = context.state
        if (
            'context_id' in state
            and 'session_active' in state
            and state['session_active']
            and 'agent' in state
        ):
            return {"active_agent": f"{state['agent']}"}
        else:
            return {"active_agent": None}

    def before_model_callback(
            self,
            callback_context: CallbackContext,
            llm_request
    ):
        state = callback_context.state
        if (
            'session_active' not in state
            or not state['session_active']
        ):
            state['session_active'] = True

    def list_remote_agents(self):
        """
        List the available remote agents that 
        you can use to deligate the task.
        """
        if not self.remote_agent_connections:
            return []
        
        remote_agent_info = []
        for card in self.card.values():
            remote_agent_info.append({
                'name': card.name,
                'description': card.description
            })
        return remote_agent_info

    async def send_message(
            self,
            agent_name: str,
            message: str,
            tool_context: ToolContext
    ):
        """
        Sends a task either streaming (if supported) or non-streaming.

        This will send a message to the remote agent named agent_name.

        Ars:
            agent_name: Name of the agent to send task to.
            message: The message to send to agent for task.
            tool_context: The tool context this message runs in.

        Yields:
            A dictionary of JSON data
        """
        # Check Agent name
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f'Agent {agent_name} not found')
        
        # State
        state = tool_context.state
        state['agent'] = agent_name

        # Check RemoteAgentConnection instance
        client = self.remote_agent_connections[agent_name]
        if not client:
            raise ValueError(f'Client not available for {agent_name}')
        
        # taskId, ContextId and messageId
        taskId = state.get('task_id', None)
        contextId = state.get('context_id', None)
        messageId = state.get('message_id', None)
        if not messageId:
            messageId = str(uuid4())

        # Request
        request : MessageSendParams = MessageSendParams(
            id=str(uuid4()),
            message=Message(
                role='user',
                parts=[TextPart(text=message)],
                taskId=taskId,
                contextId=contextId,
                messageId=messageId
            ),
            configuration=MessageSendConfiguration(
                acceptedOutputModes=['text', 'text/plain', 'image/png']
            )
        )

        # Initial Response
        response = await client.send_message(request, self.task_callback)

        if isinstance(response, Message):
            return await convert_parts(response.parts, tool_context)
        
        # Task and State's session
        task: Task = response
        state['session_active'] = task.status.state not in [
            TaskState.completed,
            TaskState.canceled,
            TaskState.failed,
            TaskState.unknown
        ]

        # state's task_id and context_id
        if task.contextId:
            state['context_id'] = task.contextId
        state['task_id'] = task.id

        # Task status state if else ladder
        if task.status.state == TaskState.input_required:
            tool_context.actions.skip_summarization = True
            tool_context.actions.escalate = True
        elif task.status.state == TaskState.canceled:
            raise ValueError(f'Agent {agent_name} task {task.id} is cancelled')
        elif task.status.state == TaskState.failed:
            raise ValueError(f'Agent {agent_name} task {task.id} has failed') 
        
        # Response 
        response = []
        if task.status.message:
            response.extend(
                await convert_parts(task.status.message.parts, tool_context)
            )
        if task.artifacts:
            for artifact in task.artifacts:
                response.extend(
                    await convert_parts(artifact.parts, tool_context)
                )
        return response


async def convert_parts(parts: list[Part], tool_context: ToolContext): 
    response_parts = []
    for part in parts:
        response_parts.append(await convert_part(part, tool_context))
    return response_parts

async def convert_part(part: Part, tool_context: ToolContext):
    if part.root.kind == 'text':
        return part.root.text
    elif part.root.kind == 'data':
        return part.root.data
    elif part.root.kind == 'file':
        file_id = part.root.file.name
        file_bytes = base64.b64encode(part.root.file.bytes)
        file_part = types.Part(
            inline_data=types.Blob(
                mime_type=part.root.file.mimeType, 
                data=file_bytes
            )
        )
        await tool_context.save_artifact(file_id, file_part)
        tool_context.actions.skip_summarization = True
        tool_context.actions.escalate = True
        return DataPart(data={'artifact-file-id': file_id})
    return f'Unkown type: {part.kind}'