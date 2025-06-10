# Google's A2A Protocol

##### 1. Output: Hello World
```python
-----------REQUEST-----------
{
    'id': '0b04aa0f-c07f-49bd-bcee-aa875b05871b',
    'jsonrpc': '2.0',
    'method': 'message/send',
    'params': {
        'message': {
            'kind': 'message',
            'messageId': '8e730af8a55c470b858aa4701c0b7546',
            'parts': [{'kind': 'text', 'text': 'How much is 10 USD in INR?'}],
            'role': 'user'
        }
    }
}
-----------RESPONSE-----------
{
    'id': '0b04aa0f-c07f-49bd-bcee-aa875b05871b',
    'jsonrpc': '2.0',
    'result': {
        'kind': 'message',
        'messageId': 'a12e4675-f04a-4f56-9771-34c5a7c67238',
        'parts': [{'kind': 'text', 'text': 'Hello World'}],
        'role': 'agent'
    }
}
```

##### 2. Output: Langgraph