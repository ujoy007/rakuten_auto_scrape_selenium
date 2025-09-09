# start_server.py
import asyncio
import sys
import uvicorn
from uvicorn import Config, Server

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    config = Config("main:app", host="127.0.0.1", port=8000, log_level="info")
    server = Server(config)
    await server.serve()

if __name__ == "__main__":
    # Create and set the event loop explicitly
    if sys.platform.startswith("win"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        if sys.platform.startswith("win"):
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.close()