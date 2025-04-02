import os
import asyncio
import time
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller

from base_bot.extensions.chromium_extension import ChromiumExtension
from base_bot.extensions.pdf_save_extension import PDFExtension
from base_bot.extensions.map_extension import WebpageScreenshotExtension

from base_bot.llm_bot_base import LLMBotBase

class BrowserClientBaseBot(LLMBotBase):
    
    def __init__(self, options=None, *args, **kwargs):
        
        super().__init__(options, *args, **kwargs)

        self.controller = Controller()
        
        pdf_extension = PDFExtension(configuration=self.config)
        pdf_extension.extend(self.controller)
        
        webpage_screenshot_extension = WebpageScreenshotExtension(configuration=self.config)
        webpage_screenshot_extension.extend(self.controller)
        
        # Track active browser instances
        self.active_browser = None
        # Track active agent instance
        self.active_agent = None
        
        print('BrowserClientBaseBot initialized')
        
        # Set up event listeners
        self.setup_event_listeners()
    
    def setup_event_listeners(self):
        """Set up event listeners for events from parent class"""
        # Listen for the restart event
        if hasattr(self, 'on') and callable(self.on):
            # self.on('restart', self.on_restart_received)
            self.on('control_command', self.on_control_command)
    
    def on_control_command(self, message):
        """Handle control command event"""
        print("Control command received:", message)
        if message.get('command') == 'cancel':
            self.on_cancel_received()
    
    def on_cancel_received(self, *args, **kwargs):
        """Handle restart event from parent class with graceful shutdown"""
        print("Cancel received - gracefully shutting down browser automation...")
        
        # Create a new event loop for this thread if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Step 1: If agent is active, pause it first
        if self.active_agent:
            try:
                print("Pausing agent execution...")
                if hasattr(self.active_agent, 'pause') and callable(self.active_agent.pause):
                    self.active_agent.pause()
                    
                    # Small delay to allow current operations to complete
                    time.sleep(0.5)
                    
                    # Step 2: Stop the agent after pause
                    print("Stopping agent execution...")
                    if hasattr(self.active_agent, 'stop') and callable(self.active_agent.stop):
                        self.active_agent.stop()
                        
                        # Another small delay to ensure stop signal is processed
                        time.sleep(0.5)
            except Exception as e:
                print(f"Error while pausing/stopping agent: {e}")
        
        # Step 3: Close the browser
        if self.active_browser:
            try:
                print("Closing browser...")
                # Run the close method in the event loop
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(self.active_browser.close(), loop)
                    future.result(timeout=5)  # Wait for up to 5 seconds
                else:
                    loop.run_until_complete(self.active_browser.close())
                
                print("Browser successfully closed on cancel")
            except Exception as e:
                print(f"Error closing browser on cancel: {e}")
            finally:
                # Clear the references regardless of success
                self.active_browser = None
                self.active_agent = None
    
    async def call_agent(self, task, extend_system_message=None, sensitive_data=None):
        
        if not task:
            return "No instructions provided"

        headless = self.config['browser_headless']
        
        browser = ChromiumExtension.extend_browser(headless=headless)
        
        # Store a reference to the browser so it can be closed on restart
        self.active_browser = browser
        
        try:
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=browser,
                controller=self.controller,
                extend_system_message=extend_system_message,
                sensitive_data=sensitive_data,
            )
            
            # Store reference to the agent so it can be gracefully stopped
            self.active_agent = agent
            
            result = await agent.run()
            return result
        finally:
            # Reset the agent reference since run has completed
            self.active_agent = None
            # Always close the browser when done
            await browser.close()
            # Clear the browser reference
            self.active_browser = None


