import asyncio
import os
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller


class WebpageScreenshotParams(BaseModel):
    """Parameters for the WebpageScreenshot action"""
    url: str
    filename: str
    sensitive_data: Optional[dict] = None
    custom_control1: Optional[str] = None
    custom_control2: Optional[str] = None


# class PDFExportOptionsParams(BaseModel):
#     """Parameters for the advanced PDF export action"""
#     path: Optional[str] = None
#     format: str = "A4"
#     landscape: bool = False
#     print_background: bool = True
#     scale: float = 1.0
#     full_page: bool = True


class WebpageScreenshotExtension:
    """
    Extension class that adds WebpageScreenshot capabilities to browser-use without modifying original code.
    """
    
    def __init__(self, configuration: Optional[dict] = None):
        """
        Initialize the WebpageScreenshot extension.
        
        Args:
            default_output_dir: Default directory for saving PDFs if not specified
        """
        
        self.default_output_dir = configuration.get('downloads_path', "downloads")
        os.makedirs(self.default_output_dir, exist_ok=True)
    
        
    def extend(self, controller: Controller) -> Controller:
        """
        Extend a controller with Map capabilities.
        
        Args:
            controller: The controller to extend
            
        Returns:
            The extended controller
        """
        # Register the PDF export action with explicit param_model
        @controller.registry.action(
            'Export the current page as Map',
            param_model=WebpageScreenshotParams
        )
        async def webpage_screenshot(params: WebpageScreenshotParams, browser: BrowserContext):
            """Export the current page as a Map file."""
            page = await browser.get_current_page()
            
            # if params.custom_control1:
            #     print('custom controls are given, i am doing my custom zoomout (decreaze size) now')
            #     await page.wait_for_selector(params.custom_control1)
            #     await page.locator(params.custom_control1).click()
            #     await asyncio.sleep(5)
            # else:
            #     print("NO CUStom cOntrOls>>>> No ZOOMINg")
            
            downloads_path = self.default_output_dir
            
            filename = params.filename
            if not filename:
                filename = f"map_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            
            path = os.path.join(downloads_path, filename)
            try:
                await page.screenshot(path=path)
                msg = f"✅ Page screenshot as Map to: {downloads_path}"
                print(msg)  # Optional console output
                return ActionResult(extracted_content=msg, include_in_memory=True)
            except Exception as e:
                error_msg = f"❌ Failed to screenshot Map: {str(e)}"
                print(error_msg)  # Optional console output
                return ActionResult(error=error_msg)
                
      
        return controller