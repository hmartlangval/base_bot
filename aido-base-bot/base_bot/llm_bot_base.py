import json
import os
from typing import Optional
from langchain_openai import ChatOpenAI

from base_bot import BaseBot

class LLMBotBase(BaseBot):
    def __init__(self, options=None):
        
        super().__init__(options)
        
        model = options.get('model', 'gpt-4o') if options else 'gpt-4o'
        self.llm = ChatOpenAI(model=model)
        self.prompt_json = {}
        self.is_prompt_loaded = False
     
        print('LLMBotBase initialized')
    
    async def analyze_image(self, instructions, encoded_image_base64=None, image_url=None):
        if image_url or encoded_image_base64:
            image_source = image_url if image_url else f"data:image/jpeg;base64,{encoded_image_base64}"
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instructions},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_source},
                        },
                    ],
                }
            ]
            # return "will parse later"
            response = await self.llm.ainvoke(messages)
            return response.content
        else:
            return "PDF to image conversion failed."
    
    async def call(self, messages):
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def quick_load_prompts(self, prompt_path):
        try:
            with open(prompt_path, 'r') as f:
                prompt_text = f.read()
            return prompt_text
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return None

     # to move to base
    async def load_v2_prompts_for_action(self, v2_config: dict, action_name: Optional[str] = 'default'):
        if not v2_config:
            raise Exception(f"v2_config is not set... Failed to load prompts for action: {action_name}")
        
        return v2_config.get('actions', {}).get(action_name, {})
    
    async def load_v2_config(self, action_name: Optional[str] = 'default'):
        botId = self.options.get('bot_id', None)
        if not botId:
            raise Exception("bot_id is not set. V2 requires a bot_id to be explicitly set before calling the LLM.")
            return ["", None, None] # dynamically identify the V2 prompt directory
        botId = self.options.get('bot_id', None)
        if not botId:
            raise Exception("bot_id is not set. V2 requires a bot_id to be explicitly set before calling the LLM.")
            return ["", None, None]
        
        v2_prompt_dir = self.options.get('prompts_directory', None)
        if not v2_prompt_dir:
            raise Exception("prompts_directory is not set. V2 requires a new prompt directory from Chat server configuration")
            return ["", None, None]
        
        v2_prompt_dir = os.path.join(v2_prompt_dir, botId)
        v2_prompt_dir = os.path.abspath(v2_prompt_dir) if os.path.isabs(v2_prompt_dir) else os.path.join(os.getcwd(), v2_prompt_dir)
        
        # then load the v2 configuration file
        v2_config_file = os.path.join(v2_prompt_dir, "config.json")   
        if not os.path.exists(v2_config_file):
            raise Exception(f"prompt file {v2_config_file} does not exist")
        
        with open(v2_config_file, 'r') as file:
            v2_config = json.load(file)
        
        # set default in case config file did not exists
        if not v2_config:
            v2_config = {}
        
        return v2_config
    

    async def load_prompts(self, prompts_path=None, reload=False):
        
        if not reload and self.is_prompt_loaded:
            return
        
        try:
            opt_prompts_path = prompts_path if prompts_path else self.options.get('prompts_path', "prompts.txt") if self.options else "prompts.txt"
            
            prompt_text = None
            if opt_prompts_path.startswith("http://") or opt_prompts_path.startswith("https://"):
                import requests
                response = requests.get(opt_prompts_path)
                if response.status_code == 200:
                    prompt_text = response.text
                else:
                    raise Exception(f"Failed to fetch prompts from URL: {opt_prompts_path}")
            else:
                import os
                self.prompts_path = opt_prompts_path if os.path.isabs(opt_prompts_path) else os.path.join(os.getcwd(), opt_prompts_path)
                with open(self.prompts_path, 'r') as f:
                    prompt_text = f.read()
                    
            self.prompt_text = prompt_text
            self.is_prompt_loaded = True
            
        except Exception as e:
            print(f"Error loading prompts: {e}")
            self.prompt_json = {}
            
            
     #V2 additional methods
    async def actions_in_config(self):
        """ Returns an iterable of actions in the config file """
        cfg = await self.load_v2_config();
        self.v2_config = cfg
        return [{"name": key, **value} for key, value in cfg.get('actions', {}).items()]
    
    async def v2_prompt(self, v2_config: dict):
        """ Returns the prompt for a given action """
        
        instruction_file_path = os.path.join(self.options.get('prompts_directory', ''), v2_config.get('activeInstructionPrompt', ''))
        system_file_path = os.path.join(self.options.get('prompts_directory', ''), v2_config.get('activeSystemPrompt', ''))
        
        instruction_file_path = os.path.abspath(instruction_file_path) if os.path.isabs(instruction_file_path) else os.path.join(os.getcwd(), instruction_file_path)
        system_file_path = os.path.abspath(system_file_path) if os.path.isabs(system_file_path) else os.path.join(os.getcwd(), system_file_path)
        
        if not os.path.isfile(instruction_file_path):
            raise Exception(f"prompt file {instruction_file_path} does not exist")
        
        with open(instruction_file_path, 'r') as file:
            instructions = file.read()
            self.prompt_text = instructions
        
        if os.path.isfile(system_file_path):
            with open(system_file_path, 'r') as file:
                extend_system_prompt = file.read()
        else:
            extend_system_prompt = ""
            
        return [instructions, extend_system_prompt]
    
    async def load_v2_config(self, action_name: Optional[str] = None):
        """ Returns the v2 config, if given an action name, it returns the action config """
        botId = self.options.get('bot_id', None)
        if not botId:
            raise Exception("bot_id is not set. V2 requires a bot_id to be explicitly set before calling the LLM.")
            return ["", None, None] # dynamically identify the V2 prompt directory
        botId = self.options.get('bot_id', None)
        if not botId:
            raise Exception("bot_id is not set. V2 requires a bot_id to be explicitly set before calling the LLM.")
            return ["", None, None]
        
        v2_prompt_dir = self.options.get('prompts_directory', None)
        if not v2_prompt_dir:
            raise Exception("prompts_directory is not set. V2 requires a new prompt directory from Chat server configuration")
            return ["", None, None]
        
        v2_prompt_dir = os.path.join(v2_prompt_dir, botId)
        v2_prompt_dir = os.path.abspath(v2_prompt_dir) if os.path.isabs(v2_prompt_dir) else os.path.join(os.getcwd(), v2_prompt_dir)
        
        # then load the v2 configuration file
        v2_config_file = os.path.join(v2_prompt_dir, "config.json")   
        if not os.path.exists(v2_config_file):
            raise Exception(f"prompt file {v2_config_file} does not exist")
        
        with open(v2_config_file, 'r') as file:
            v2_config = json.load(file)
        
        # set default in case config file did not exists
        if not v2_config:
            v2_config = {}
        
        if action_name:
            return v2_config.get(action_name, {})
        
        return v2_config
    
    

