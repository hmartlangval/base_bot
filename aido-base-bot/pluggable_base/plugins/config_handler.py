import time
import datetime
import asyncio
from dotenv import load_dotenv

from services.base_bot_shaken import BaseBotShaken

load_dotenv()

def get_dependencies():
    return ["config", "logger", "queue_manager"]

async def handle_message(message, deps=None):
    
    if deps and "config" in deps:
        config_service = deps["config"]
    
    
    return "Config handler called"