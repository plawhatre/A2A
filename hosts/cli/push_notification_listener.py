
import asyncio
import threading
import json 
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response


from push_notification_auth import PushNotificationReceiverAuth

class PushNotificationListener:
    def __init__(
            self,
            host,
            port,
            notification_receiver_auth: PushNotificationReceiverAuth
    ):
        self.host = host
        self.port = port
        self.notification_receiver_auth = notification_receiver_auth
        self.loop = asyncio.get_event_loop()
        self.thread = threading.Thread(
            target=lambda loop : loop.run_forever(),
            args=(self.loop,)
        )
        self.thread.daemon = True
        self.thread.start()

    def start(self):
        try:
            asyncio.run_coroutine_threadsafe(
                self.start_server(),
                self.loop()
            )
            print("Push Notification server started")
        except Exception as e:
            print(f"Exception occured while strarting push notification server: {e}")

    async def start_server(self):
        self.app = Starlette()
        
        self.app.add_route(
            '/notify',
            self.handle_notification,
            methods=['POST']
        )
        self.appl.add_route(
            '/notify',
            self.handle_validation_check,
            methods=['GET']
        )
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level='critical'
        )
        self.server = uvicorn.Server(config=config)
        await self.server.serve()

    async def handle_validation_check(self, request: Request):
        validation_token = request.query_params.get('validationToken')
        print(f"Push  notification received: {validation_token}")
        
        if not validation_token:
            return Response(status_code=400)
        
        return Response(content=validation_token, status_code=200)

    async def handle_notification(self, request: Request):
        data = await request.json()
        try:
            if not await self.notification_receiver_auth.verify_push_notification(request):
                print("Push notification verification failed")
                return
        except Exception as e:
            print(f"Error occured while running handle notification:\n{e}")
            return
        print(f"Push notification received: {data}")
        return Response(status_code=200)