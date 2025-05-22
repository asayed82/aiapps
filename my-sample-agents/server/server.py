
import asyncio
from core.websocket_handler import handle_client
from core.logger import logger


async def main() -> None:
    """Starts the WebSocket server."""
    port = 8081

    logger.info("Starting websocket server from server.py main()...")
    
    import websockets
    
    async with websockets.serve(
        handle_client,
        "0.0.0.0",
        port,
        ping_interval=30,
        ping_timeout=10,
    ):
        logger.info(f"Running websocket server on 0.0.0.0:{port}...")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())