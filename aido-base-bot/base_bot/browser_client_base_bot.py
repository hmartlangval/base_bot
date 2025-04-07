import json
import os
import asyncio
import time
import logging
import uuid
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller, AgentHistoryList
from base_bot.extensions.chromium_extension import ChromiumExtension
from base_bot.extensions.pdf_save_extension import PDFExtension
from base_bot.extensions.map_extension import WebpageScreenshotExtension
from browser_use.browser.context import BrowserContext
from browser_use.browser.views import URLNotAllowedError  # Add this import
from browser_use.agent.views import AgentOutput
from browser_use.browser.context import BrowserState
from base_bot.llm_bot_base import LLMBotBase
from base_bot.types import BrowserSessionConfig

logger = logging.getLogger(__name__)

# Monkey patching function
def apply_browser_use_patches():
    """Apply monkey patches to browser_use package to customize its behavior."""
    print("Applying browser_use monkey patches...")
    
    # Store original method
    original_click_element_node = BrowserContext._click_element_node
    
    # Create a wrapper for the method we want to patch
    async def patched_click_element_node(self, element_node):
        """
        Patched version of _click_element_node to enable custom filenames for downloads.
        """
        print("Using patched _click_element_node method")
        page = await self.get_current_page()

        try:
            element_handle = await self.get_locate_element(element_node)

            if element_handle is None:
                raise Exception(f'Element: {repr(element_node)} not found')

            async def perform_click(click_func):
                """Performs the actual click, handling both download
                and navigation scenarios."""
                if self.config.save_downloads_path:
                    try:
                        # Try short-timeout expect_download to detect file download
                        async with page.expect_download(timeout=5000) as download_info:
                            await click_func()
                        download = await download_info.value
                        
                        # AIDO Nelvin customization here: Determine filename - check for custom filename attribute
                        if hasattr(self.config, 'annual_pdf_filename') and self.config.annual_pdf_filename:
                            # Use custom filename
                            filename = self.config.annual_pdf_filename
                            download_path = os.path.join(self.config.save_downloads_path, filename)
                            print(f"Using custom filename: {filename}")
                        else:
                            # Use suggested filename from download
                            suggested_filename = download.suggested_filename
                            unique_filename = await self._get_unique_filename(self.config.save_downloads_path, suggested_filename)
                            download_path = os.path.join(self.config.save_downloads_path, unique_filename)
                            
                        # Save the download
                        await download.save_as(download_path)
                        print(f"Download saved to: {download_path}")
                        return download_path
                    except TimeoutError:
                        # If no download is triggered, treat as normal click
                        await page.wait_for_load_state()
                        await self._check_and_handle_navigation(page)
                else:
                    # Standard click logic if no download is expected
                    await click_func()
                    await page.wait_for_load_state()
                    await self._check_and_handle_navigation(page)

            try:
                return await perform_click(lambda: element_handle.click(timeout=1500))
            except URLNotAllowedError as e:
                raise e
            except Exception:
                try:
                    return await perform_click(lambda: page.evaluate('(el) => el.click()', element_handle))
                except URLNotAllowedError as e:
                    raise e
                except Exception as e:
                    raise Exception(f'Failed to click element: {str(e)}')

        except Exception as e:
            raise Exception(f'Failed to click element: {repr(element_node)}. Error: {str(e)}')
    
    # Apply the patch
    BrowserContext._click_element_node = patched_click_element_node
    print("Monkey patch applied successfully")

# Add a try-except to handle the URLNotAllowedError which might not be imported yet
try:
    from browser_use.browser.views import URLNotAllowedError
except ImportError:
    # Define a placeholder class if the import fails
    class URLNotAllowedError(Exception):
        pass
        
        
class BrowserClientBaseBot(LLMBotBase):
    
    def __init__(self, options=None, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        # Apply monkey patch after initializing the base class
        apply_browser_use_patches()
        
        self.controller = Controller()
        
        pdf_extension = PDFExtension(configuration=self.config)
        pdf_extension.extend(self.controller)
        
        webpage_screenshot_extension = WebpageScreenshotExtension(configuration=self.config)
        webpage_screenshot_extension.extend(self.controller)
        
        # Track active browser instances and their contexts
        self._browser_instances = {}  # Dict to store browser instances and their contexts
        # Track active agent instance
        self.active_agent = None
        
        print('BrowserClientBaseBot initialized')
        
        # Set up event listeners
        self.setup_event_listeners()
    
    def check_success_or_failure(self, history):
        """Check if the result is a success or failure"""
        
        if not isinstance(history, AgentHistoryList):
            print("history is not an AgentHistoryList")
            return [False, None]
        
        if history.is_done():
            # Check if the agent was successful
            if history.is_successful():
                print("Agent completed the task successfully")
                
                # You can also get the final result if any
                final_result = history.final_result()
                if final_result:
                    print("Final result:", final_result)
                    return [True, final_result]
            else:
                print("Agent completed but was not successful")
                
            # Check for any errors that occurred
            if history.has_errors():
                errors = history.errors()
                print("Errors:", errors)
                return [False, errors]
        else:
            print("Agent did not complete the task")
            return [False, 'Agent did not complete the task']

        return [False, None]
            
        
    
    def setup_event_listeners(self):
        """Set up event listeners for events from parent class"""
        # Listen for the restart event
        if hasattr(self, 'on') and callable(self.on):

            self.on('control_command', self.on_control_command)
    
    def on_control_command(self, message):
        """Handle control command event"""
        print("Control command received:", message)
        if message.get('command') == 'cancel':
            self.on_cancel_received()
    
    async def gracefully_shutdown_agent(self):
        """Common method to gracefully shutdown the agent and browser"""
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
        
        # Step 3: Close all browser instances
        for browser_id, (browser, context_config) in self._browser_instances.items():
            original_json = None
            try:
                # Log browser context info if available
                if context_config:
                    original_json = getattr(context_config, 'original_json', None)
                    # custom_filename = getattr(context_config, 'annual_pdf_filename', None)
                    # print(f"Retrieved before closing browser filename: {custom_filename} {original_json}")
                
                print(f"Closing browser instance {browser_id}...")
                
                
                json_string = ""
                if original_json:
                    print("_____PREPARING JSON STRING")
                    json_string = f"[json]{json.dumps(original_json)}[/json] [Retry]"
                    print("JSON STRING", json_string)
                else:
                    print("----------NO ORIGINAL JSON")
                    
                self.socket.emit('message', {
                    "channelId": "general",
                    "content": f"Task cancelled for order \"{original_json['order_number']}\". {json_string}"
                })
                
                try:
                    await browser.close()
                except Exception as e:
                    print(f"Error closing browser instance {browser_id}: {e}")
                print(f"Browser instance {browser_id} successfully closed")
            except Exception as e:
                print(f"Error during cleanup of browser instance {browser_id}: {e}")
        
        # Clear all references
        self._browser_instances.clear()
        self.active_agent = None
    
    def on_cancel_received(self, *args, **kwargs):
        """Handle cancel event - gracefully shut down the agent and browser"""
        print("Cancel received - gracefully shutting down browser automation...")
        
        # Create a new event loop for this thread if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Use the common shutdown method
        loop.run_until_complete(self.gracefully_shutdown_agent())
        print("Browser automation successfully cancelled")
    
    
    async def log_completion_to_external_service(self, history: AgentHistoryList):
        # Here you can extract just the "next step" information from agent_output
        next_step = history.final_result()
        
        self.socket.emit('message', {
            "channelId": "general",
            "content": next_step
        })
    
    async def log_step_to_external_service(self, browser_state: BrowserState, agent_output: AgentOutput, step_number: int):
        # Get the next goal from the agent's brain
        next_step = agent_output.current_state.next_goal
        
        self.socket.emit('message', {
            "channelId": "general",
            "content": next_step
        })
       
    
    async def call_agent(self, task, extend_system_message=None, sensitive_data=None, session_config: BrowserSessionConfig = None):
        if not task:
            return "No instructions provided"

        # Store parameters for potential restart
        self.last_task_params = {
            'task': task,
            'extend_system_message': extend_system_message,
            'sensitive_data': sensitive_data
        }
        
        headless = self.config['browser_headless']
        
        browser_id = str(uuid.uuid4())
        [browser, context_config] = ChromiumExtension.extend_browser(session_config, self.config, headless=headless)
        self._browser_instances[browser_id] = (browser, context_config)
        
        try:
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=browser,
                controller=self.controller,
                extend_system_message=extend_system_message,
                sensitive_data=sensitive_data,
                register_new_step_callback=self.log_step_to_external_service,
                register_done_callback=self.log_completion_to_external_service
            )
            
            # Store reference to the agent so it can be gracefully stopped
            self.active_agent = agent
            
            result = await agent.run()
            return result
        finally:
            # Clean up this specific browser instance
            if browser_id in self._browser_instances:
                browser, context_config = self._browser_instances.pop(browser_id)
                try:
                    await browser.close()
                except Exception as e:
                    print(f"Error during cleanup of browser instance {browser_id}: {e}")
            
            # Reset the agent reference since run has completed
            self.active_agent = None