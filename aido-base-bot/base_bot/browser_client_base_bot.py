import os
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller

from base_bot.extensions.chromium_extension import ChromiumExtension
from base_bot.extensions.pdf_save_extension import PDFExtension

from base_bot.llm_bot_base import LLMBotBase

class BrowserClientBaseBot(LLMBotBase):
        
    def __init__(self, options=None, *args, **kwargs):
        
        super().__init__(options, *args, **kwargs)

        self.controller = Controller()
        
        pdf_extension = PDFExtension(configuration=self.config)
        pdf_extension.extend(self.controller)
        
        print('BrowserClientBaseBot initialized')
        
    
    async def call_agent(self, task, extend_system_message=None, sensitive_data=None):
        
        if not task:
            return "No instructions provided"

        headless = self.config['browser_headless']
        
        browser = ChromiumExtension.extend_browser(headless=headless)
        
        agent = Agent(
            task=task,
            llm=self.llm,
            browser=browser,
            controller=self.controller,
            extend_system_message=extend_system_message,
            sensitive_data=sensitive_data,
        )
        
        result = await agent.run()
        
        await browser.close()
        
        return result


