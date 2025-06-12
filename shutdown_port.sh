ps -ef | grep server.py | awk '{print $3}' | xargs kill -9 
# uv run langgraph/server.py
# uv run langgraph/client.py