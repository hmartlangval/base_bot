import time
import datetime
import asyncio
from dotenv import load_dotenv

from base_bot_shaken import BaseBotShaken

load_dotenv()

async def handle_message(message_data):
    
    """
    Echo handler plugin - demonstrates dynamic reloading and async capability
    
    Last updated: 2023-10-15 12:00
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"Echo handler processing at {timestamp}: {message_data}")
    
    # Use asyncio.sleep instead of time.sleep in async functions
    await asyncio.sleep(1)  # simulate processing asynchronously
    
    # Create a bot instance
    bot = BaseBotShaken()
    
    # Call the agent asynchronously
    agent_response = await bot.call_agent("navigate to http://localhost:5500/simplepage.html page. Do nothing else. Wait for 5 seconds. Exit.")
    
    print('Bot initialized without errors')
    print(f'Agent response: {agent_response}')
    
    # Return the response
    return f"Echo response at {timestamp}: {message_data} (Agent: {agent_response})" 