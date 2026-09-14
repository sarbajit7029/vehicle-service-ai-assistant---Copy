from fastapi import WebSocket


class ConnectionManager:
    """
    Manage active WebSocket connections.

    Each connection is associated with a chat session ID.
    """

    def __init__(self) -> None:
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(
        self,
        websocket: WebSocket,
        session_id: int,
    ) -> None:
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: int) -> None:
        self.active_connections.pop(session_id, None)

    async def send_json(
        self,
        session_id: int,
        data: dict,
    ) -> None:
        websocket = self.active_connections.get(session_id)

        if websocket is not None:
            await websocket.send_json(data)


manager = ConnectionManager()