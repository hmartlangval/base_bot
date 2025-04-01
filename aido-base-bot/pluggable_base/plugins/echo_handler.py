import time
import datetime
import asyncio
from dotenv import load_dotenv

# from base_bot_shaken import BaseBotShaken

load_dotenv()

# Specify which dependencies this plugin requires
def get_dependencies():
    return ["config", "logger", "database", "browser"]

async def handle_message(message, deps=None):
    """
    Echo handler plugin - demonstrates dynamic reloading and dependency injection
    
    Last updated: 2023-10-15 12:00
    """
    # Access injected dependencies if available
    if deps:
        # Log using injected logger if available
        if "logger" in deps:
            deps["logger"].info(f"Echo handler processing: {message.get('content', None)}")
        
        # Use injected config if available
        config = deps.get("config", {})
        wait_time = config.get("echo_wait_time", 1)
    else:
        wait_time = 1
    
    content = message.get("content", None)
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"Echo handler processing at {timestamp}: {content}")
    
    # Use asyncio.sleep instead of time.sleep in async functions
    await asyncio.sleep(wait_time)  # simulate processing asynchronously with configurable wait time
    
    if deps and "browser" in deps:
        bot = deps["browser"]
        agent_response = await bot.call_agent("navigate to http://localhost:5500/simplepage.html page. Do nothing else. Wait for 5 seconds. Exit.")
        print(f'Agent response: {agent_response}')
    
    # Store in database if available
    if deps and "database" in deps and agent_response is not None:
        deps["database"].store_response(timestamp, content, agent_response)
        deps["database"].send_message("general", f"Echo response at {timestamp}: {content} (Agent: {agent_response})")
    
    # Return the response
    # return f"Echo response at {timestamp}: {message_data} (Agent: {agent_response})"
    return "I AM DONE -----------------"