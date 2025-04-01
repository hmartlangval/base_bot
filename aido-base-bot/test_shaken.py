import json
import time
import os
from dotenv import load_dotenv

# Load .env file from the base_bot_shaken directory
dotenv_path = os.path.join(os.path.dirname(__file__), 'base_bot_shaken', '.env')
load_dotenv(dotenv_path)

# Set root path to aido-base-bot
# root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# os.chdir(root_path)


from base_bot_shaken import BaseBotShaken


class TestBrowserClient(BaseBotShaken):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        
    async def generate_response(self, message):
        print("generate_response: ", message)
        
        instructions = await self.quick_load_prompts('prompts/simple.txt')
        
        result = await self.call_agent(instructions)
        print(result)
        
        
        return 'done'

    
bot = TestBrowserClient(options={
    'model': 'gpt-4o-mini',
    'downloads_path': 'downloads'
})





