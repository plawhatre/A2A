import httpx
from collections.abc import AsyncIterable
from pydantic import BaseModel
from typing import Literal

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

API_ADDRESS = 'https://api.frankfurter.app/'
SYSTEM_INSTRUCTIONS = (
    "You are a specialised agent for currency conversion. "
    "Your sole purpose is to use the 'get_exchange_rate' tool to answer the questions. "
    "If the user asks anything that is not about currency conversion or exchange rate "
    "then, politely state that you can not help with the topic and can only assist in currency related queries. "
    "Set the response status to input required if the user need to provide more information. "
    "Set the response status to error if there is an error while processing the request. "
    "Set the response status to complete if the request is complete."
)
MEMORY = MemorySaver()

@tool
def get_exchange_rate(
    currency_from: str = 'USD',
    currency_to: str = 'EUR',
    currency_date: str = 'latest'
):
    """This tool helps to get current currency exchange rate

    Args:
        currency_from: The currency to convert from (e.g., USD)
        currency_to: The currency to convert to (e.g., EUR)
        currency_date: The date on which this exchange is sought. 
                       Default is "latest"

    Returns:
        A dictionary containing the exchange rate. However, it will contain
        error message in case of an error.
    """
    try:
        address = API_ADDRESS + f"{currency_date}"
        params = {
            "from": currency_from,
            "to": currency_to
        }

        response = httpx.get(address, params=params)
        response.raise_for_status()

        data = response.json()

        if 'rates' not in data:
            return {'error': 'Invalid API response format'}
        return data

    except httpx.HTTPError as e:
        return {'error': f'API request failed: {e}'}
    except ValueError:
        return {'error': 'Invalid JSON response from API'}


class ResponseFormat(BaseModel):
    """Respond to the user in this format
    """
    status: Literal['input_required', 'complete', 'error'] = 'input_required'
    message: str

class CurrencyAgent:
    """Its a specialised agent for currency conversion
    """
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
        self.tools = [get_exchange_rate]
        self.graph = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=SYSTEM_INSTRUCTIONS,
            checkpointer=MEMORY,
            response_format=ResponseFormat
        )

    def invoke(self, query, context_id) -> str:
        inputs = {'messages': [HumanMessage(query)]}
        config = {'configurable': {'thread_id': context_id}}
        self.graph.invoke(inputs, config=config)
        return self.get_agent_response(config)

    async def stream(self, query, context_id) -> AsyncIterable:
        inputs = {'messages': [HumanMessage(query)]}
        config = {'configurable': {'thread_id': context_id}}
        for item in self.graph.stream(inputs, config=config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ): 
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Looking up the exchange rates...'
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing the exchange rates...'
                }
            yield self.get_agent_response(config)


    def get_agent_response(self, config):
        current_state = self.graph.get_current_state(config)
        structured_response = current_state.values.get('structured_response')
        if (
            structured_response
            and isinstance(structured_response, ResponseFormat)
        ):
            if (
                structured_response.status == 'input_required'
                or structured_response.status == 'error'
            ):
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message
                }
            if structured_response.status == 'complete':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message
                }
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': (
                "We are unable to process your request. "
                "Please try after some time."
            )
        }
