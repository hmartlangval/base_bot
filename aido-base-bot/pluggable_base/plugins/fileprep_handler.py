import time
import datetime
import asyncio
from dotenv import load_dotenv

# from base_bot_shaken import BaseBotShaken

load_dotenv()

# Specify which dependencies this plugin requires
def get_dependencies():
    return ["config", "logger", "queue_manager"]

async def handle_message(message, deps=None):
    """
    Echo handler plugin - demonstrates dynamic reloading and dependency injection
    
    Last updated: 2023-10-15 12:00
    """
    
    if deps and "queue_manager" in deps:
        qm = deps["queue_manager"]
    
    if not qm:
        return "Queue Manager servies not found"
    
    result = await qm.process_request(message)
    
    deps["logger"].info(f"File Prep result: {result}")
    
    if result:
        return result
    
    return "File Prep I AM DONE -----------------"