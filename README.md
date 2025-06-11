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
```python
-----------REQUEST-----------
{
    'id': 'f9b11070-c441-462a-813d-cd9a9cad7055',
    'jsonrpc': '2.0',
    'method': 'message/send',
    'params': {
        'message': {
            'kind': 'message',
            'messageId': '449885dcbbfa49bd83ec5ea19811c736',
            'parts': [{'kind': 'text', 'text': 'How much is 10 USD in INR?'}],
            'role': 'user'
        }
    }
}
-----------RESPONSE-----------
{
    'id': 'f9b11070-c441-462a-813d-cd9a9cad7055',
    'jsonrpc': '2.0',
    'result': {
        'artifacts': [
            {
                'artifactId': 'c72e9782-a937-4aad-a8da-88d52c24b941',
                'name': 'conversion_result',
                'parts': [{'kind': 'text', 'text': '10 USD is 855.8 INR.'}]
            }
        ],
        'contextId': '4c1c2307-583a-4b8d-ac61-068a3729dc3a',
        'history': [
            {
                'contextId': '4c1c2307-583a-4b8d-ac61-068a3729dc3a',
                'kind': 'message',
                'messageId': '449885dcbbfa49bd83ec5ea19811c736',
                'parts': [{'kind': 'text', 'text': 'How much is 10 USD in INR?'}],
                'role': 'user',
                'taskId': '640252ac-f5a7-43e0-b1cc-2f6275c12f8c'
            },
            {
                'contextId': '4c1c2307-583a-4b8d-ac61-068a3729dc3a',
                'kind': 'message',
                'messageId': '72f8bec3-4986-4701-8aa5-0d6fa01491bc',
                'parts': [{'kind': 'text', 'text': 'Looking up the exchange rates...'}],
                'role': 'agent',
                'taskId': '640252ac-f5a7-43e0-b1cc-2f6275c12f8c'
            },
            {
                'contextId': '4c1c2307-583a-4b8d-ac61-068a3729dc3a',
                'kind': 'message',
                'messageId': 'c95dd90a-5139-4add-88ea-7c52f99cce2a',
                'parts': [{'kind': 'text', 'text': 'Processing the exchange rates...'}],
                'role': 'agent',
                'taskId': '640252ac-f5a7-43e0-b1cc-2f6275c12f8c'
            }
        ],
        'id': '640252ac-f5a7-43e0-b1cc-2f6275c12f8c',
        'kind': 'task',
        'status': {'state': 'completed'}
    }
}
```