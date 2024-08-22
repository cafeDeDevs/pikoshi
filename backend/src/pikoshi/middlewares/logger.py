import json
import os
import time
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute


class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before

            log_entry = {
                "route": str(request.url),
                "method": request.method,
                "duration": duration,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat(),
                "headers": dict(response.headers),
            }

            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"logs_{datetime.now().date()}.json")
            log_entries = []

            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    content = f.read().strip()
                    if content:
                        log_entries = json.loads(content)

            log_entries.append(log_entry)

            with open(log_file, "w") as f:
                json.dump(log_entries, f, indent=4)

            return response

        return custom_route_handler
