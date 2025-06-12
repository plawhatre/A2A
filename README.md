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
-----------MULTITURN RESPONSE-----------
{
    'id': '242f6940-4b5e-4b39-8868-80691bbf2450',
    'jsonrpc': '2.0',
    'result': {
        'contextId': '3e27da4b-bbf7-4ada-8bda-f83b5ba0c458',
        'history': [
            {
                'contextId': '3e27da4b-bbf7-4ada-8bda-f83b5ba0c458',
                'kind': 'message',
                'messageId': '60d0cb8b9f834536a020aeaa6691be1f',
                'parts': [{'kind': 'text', 'text': 'How much is 10 USD?'}],
                'role': 'user',
                'taskId': '9d394ba7-c6cf-454d-873b-b2e5bedf790c'
            },
            {
                'contextId': '3e27da4b-bbf7-4ada-8bda-f83b5ba0c458',
                'kind': 'message',
                'messageId': '62a4504b-0a0e-4857-af7d-f59cb4bdb210',
                'parts': [{'kind': 'text', 'text': 'Could you please specify which currency you would like to convert 10 USD to?'}],
                'role': 'agent',
                'taskId': '9d394ba7-c6cf-454d-873b-b2e5bedf790c'
            },
            {
                'contextId': '3e27da4b-bbf7-4ada-8bda-f83b5ba0c458',
                'kind': 'message',
                'messageId': '38ee02f1a20b46c7af68a26b3faa07d0',
                'parts': [{'kind': 'text', 'text': 'CAD'}],
                'role': 'user',
                'taskId': '9d394ba7-c6cf-454d-873b-b2e5bedf790c'
            },
            {
                'contextId': '3e27da4b-bbf7-4ada-8bda-f83b5ba0c458',
                'kind': 'message',
                'messageId': '1d120e3d-e018-454d-a873-1e40809e190b',
                'parts': [{'kind': 'text', 'text': 'Looking up the exchange rates...'}],
                'role': 'agent',
                'taskId': '9d394ba7-c6cf-454d-873b-b2e5bedf790c'
            },
            {
                'contextId': '3e27da4b-bbf7-4ada-8bda-f83b5ba0c458',
                'kind': 'message',
                'messageId': 'c8ccad10-224d-41ff-8f9b-24777ac854cc',
                'parts': [{'kind': 'text', 'text': 'Processing the exchange rates...'}],
                'role': 'agent',
                'taskId': '9d394ba7-c6cf-454d-873b-b2e5bedf790c'
            }
        ],
        'id': '9d394ba7-c6cf-454d-873b-b2e5bedf790c',
        'kind': 'task',
        'status': {
            'message': {
                'contextId': '3e27da4b-bbf7-4ada-8bda-f83b5ba0c458',
                'kind': 'message',
                'messageId': '6fd4ee19-f802-46f8-a837-647736de1635',
                'parts': [{'kind': 'text', 'text': '10 USD is 13.686 CAD'}],
                'role': 'agent',
                'taskId': '9d394ba7-c6cf-454d-873b-b2e5bedf790c'
            },
            'state': 'input-required'
        }
    }
}
```