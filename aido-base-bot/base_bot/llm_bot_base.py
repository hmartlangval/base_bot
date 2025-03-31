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
    

