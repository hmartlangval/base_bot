import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables from .env file in this directory
# env_path = os.path.join(os.path.dirname(__file__), '.env')
# load_dotenv(env_path)

from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller

from .extensions.chromium_extension import ChromiumExtension
from .extensions.pdf_save_extension import PDFExtension
from .extensions.map_extension import WebpageScreenshotExtension

from .llm_bot_base import LLMBotBase

from services import SocketAwareService

class BaseBotShaken(SocketAwareService, LLMBotBase):
        
    def __init__(self, socket_io=None, options=None, *args, **kwargs):
        # Initialize each parent class separately
        SocketAwareService.__init__(self, socket_io, options, *args, **kwargs)
        LLMBotBase.__init__(self, options)

        self.controller = Controller()
        
        pdf_extension = PDFExtension(configuration=self.config)
        pdf_extension.extend(self.controller)
        
        webpage_screenshot_extension = WebpageScreenshotExtension(configuration=self.config)
        webpage_screenshot_extension.extend(self.controller)
        
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


