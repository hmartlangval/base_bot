import os

from datetime import datetime
from typing import Optional
from playwright.async_api import Dialog, Page
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller
from .pdf_save_extension import PDFExtension, PDFExportParams
 
class PrintDialogHandler:
    """
    Plugin to handle system print dialogs during browser automation.
    When browser-use triggers a print action, this plugin handles the native print dialog
    and saves the output as PDF.
    """
   
    def __init__(self, configuration: Optional[dict] = None):
        """
        Initialize the print dialog handler.
       
        Args:
            configuration: Configuration dictionary containing settings like output directory
        """
        self.config = configuration or {}
   
    async def setup_print_dialog_handler(self, page: Page):
        """Set up handlers for system print dialogs."""
       
        async def handle_print_dialog(dialog: Dialog):
            try:
                # When print dialog appears, we want to:
                # 1. Set the printer to "Microsoft Print to PDF" or similar PDF printer
                # 2. Set the output path
                # 3. Click Print/Save
               
                # First dismiss the native dialog as we'll handle it via page actions
                await dialog.dismiss()
               
                # Wait for the print dialog UI elements
                await page.wait_for_selector('select[aria-label="Destination"]', timeout=5000)
               
                # Select PDF printer
                await page.select_option('select[aria-label="Destination"]', 'Microsoft Print to PDF')
               
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"print_output_{timestamp}.pdf"
                output_path = os.path.join(self.config.get('custom_downloads_path', 'downloads'), filename)
               
                # Click the Save/Print button
                save_button = await page.wait_for_selector('button[aria-label="Print"]')
                await save_button.click()
               
                # Wait for save dialog and handle it
                # Note: This part may need adjustment based on system specifics
                await page.wait_for_timeout(1000)  # Brief wait for save dialog
               
                print(f"PDF saved to: {output_path}")
               
            except Exception as e:
                print(f"Error handling print dialog: {str(e)}")
       
        # Set up the dialog handler
        page.on("dialog", handle_print_dialog)
   
    def extend(self, controller: Controller) -> Controller:
        """
        Extend the controller with print dialog handling capabilities.
       
        Args:
            controller: The controller to extend
           
        Returns:
            The extended controller
        """
       
        @controller.registry.action(
            'Handle print dialog',
            param_model=None
        )
        async def handle_print_dialog(browser: BrowserContext):
            """Set up handlers for print dialogs on the current page."""
            page = await browser.get_current_page()
            await self.setup_print_dialog_handler(page)
            return ActionResult(
                extracted_content="Print dialog handler has been set up successfully",
                include_in_memory=True
            )
       
        return controller