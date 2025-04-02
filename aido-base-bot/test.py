import ctypes
import json
import time
from base_bot.browser_client_base_bot import BrowserClientBaseBot

class TestBrowserClient(BrowserClientBaseBot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

    async def prepare_prompt_json(self):
        print('initializing on the test browser client')
        
        prompt_data = {}
        current_county = None

        in_instructions = False
        
        for line in self.prompt_text.split('\n'):
            line = line.strip()

            if line.startswith("#"):
                continue                
            if line.startswith(">>County:") and not in_instructions:
                current_county = line.replace('>>County:', '').strip()
                prompt_data[current_county] = {}
                in_instructions = False
            elif line.startswith(">>URL:"):
                url = line.replace('>>URL:', '').strip()
                prompt_data[current_county]['url'] = url
            elif line.startswith(">>INSTRUCTIONS:"):
                instructions = []
                in_instructions = True
            elif in_instructions:
                if line.startswith(">>County:"):
                    if current_county and instructions:
                        prompt_data[current_county]['instructions'] = "\n".join(instructions)
                    current_county = line.replace('>>County:', '').strip()
                    prompt_data[current_county] = {}
                    in_instructions = False
                else:
                    instructions.append(line.strip())
            elif line == "":
                continue
            else:
                instructions.append(line.strip())

        if current_county and instructions:
            prompt_data[current_county]['instructions'] = "\n".join(instructions)

        self.prompt_json = prompt_data
        print('prompt json file is loaded and is ready to use')

    def get_instructions(self, sensitive_data):
        county = sensitive_data.get('x_county')
        if county:
            prompt_data = self.prompt_json.get(county, {})
            navigate_url = prompt_data.get('url', '')
            instructions = prompt_data.get('instructions', '')
        else:
            instructions = ''
            
        if not instructions or not navigate_url:
            return None
            
        instructions = f"""
        search_by_account_number: {'true' if sensitive_data.get('x_account_number') else 'false'}
        
        Navigate to the following URL: {navigate_url}
        
        {instructions}
        """
        
        return instructions
    
    def should_respond_to(self, message):
        # print("MESSAGE: ", message)
        print("JSON CoNTENT: ", message.get("jsonData", None))
        return False
        # super().should_respond_to(message)
     
    async def generate_response(self, message):
        # print("MESSAGE: ", message)
        requestJson = message.json;
        print("REQUEST JSON: ", requestJson)
        
        if not self.is_prompt_loaded:
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": 'Message is received, processing... >>>'
            })

            await self.load_prompts()
            await self.prepare_prompt_json()
        
        sensitive_data = {  
            'x_account_number': '1234567890',
            'x_county': 'brevard',
        }
          
        instructions = self.get_instructions(sensitive_data)
        
        instructions = instructions.replace('[order_number]', '73-832-8383')
        print("INstRUCTIONS: ", instructions)
        
        
        
        
        sys_instructions = """You are a web navigator. When you are to save a page as PDF, the following parameters are to be passed to the extension:"""
        
      
        
        result  = await self.call_agent(instructions, extend_system_message=sys_instructions, sensitive_data=sensitive_data)
        
        return "Browser automation done"
        
        #     return 'Prompts are successfully loaded ' + json.dumps(self.prompt_json, indent=4)
        # else:
        #     return 'Prompt is already loaded... >>>' + json.dumps(self.prompt_json, indent=4)
    
def get_window_handle():
    user32 = ctypes.windll.user32
    handle = user32.GetForegroundWindow()
    return handle
   
bot = TestBrowserClient(options={
    "window_hwnd": get_window_handle(),
    "commands": {
       "restart": "^c^cpython test.py"  
    },
    "bot_id": "final",
    "bot_name": "final bot",
    "bot_type": "bot",
    'model': 'gpt-4o-mini',
    'downloads_path': 'my_downloads',
    'autojoin_channel': 'general',
    # 'prompts_path': "prompts.txt" default is prompts.txt, can be a url or a local file (relative or absolute path)
    # 'prompts_path': 'base_bot/prompts.txt'
})

bot.start()

import requests
def call_rest_api():
    json_data = {
        "order_number": "73-832-8383",
        "s_data": {
            "x_account_number": "1234567890",
            "x_county": "brevard"
        }
    }
    data = {
        "content": f" start processing for [json]{json.dumps(json_data)}[/json]",
        "sender": "Admin"
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




