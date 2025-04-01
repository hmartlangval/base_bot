import json
import time
import os

# Set root path to aido-base-bot
# root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# os.chdir(root_path)


from base_bot.browser_client_base_bot import BrowserClientBaseBot


class TestBrowserClient(BrowserClientBaseBot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        
    async def generate_response(self, message):
        print("generate_response: ", message)
        
        instructions = await self.quick_load_prompts('prompts/simple.txt')
        
        result = await self.call_agent(instructions)
        print(result)
        
        
        return 'done'

    
bot = TestBrowserClient(options={
    "bot_id": "mapbot",
    "bot_name": "Map Bot",
    'model': 'gpt-4o-mini',
    'downloads_path': 'downloads',
    'autojoin_channel': 'general',
})

bot.start()

import requests
def call_rest_api():
    data = {
        "channelId": "general",
        "content": "@mapbot take a screenshot"
    }
    try:
        response = requests.post('http://localhost:3000/api/channels/general/sendMessage', json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()  # Return the response as JSON
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
call_rest_api()
    
bot.join()
    
bot.cleanup()
    
# bot.input_thread.join()




