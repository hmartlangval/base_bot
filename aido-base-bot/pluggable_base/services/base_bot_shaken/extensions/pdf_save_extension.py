import os
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller


class PDFExportParams(BaseModel):
    """Parameters for the PDF export action"""
    path: Optional[str] = None,
    sensitive_data: Optional[dict] = None,


class PDFExportOptionsParams(BaseModel):
    """Parameters for the advanced PDF export action"""
    path: Optional[str] = None
    format: str = "A4"
    landscape: bool = False
    print_background: bool = True
    scale: float = 1.0
    full_page: bool = True


class PDFExtension:
    """
    Extension class that adds PDF capabilities to browser-use without modifying original code.
    """
    
    def __init__(self, configuration: Optional[dict] = None):
        """
        Initialize the PDF extension.
        
        Args:
            default_output_dir: Default directory for saving PDFs if not specified
        """
        
        self.default_output_dir = configuration.get('downloads_path', "downloads")
        os.makedirs(self.default_output_dir, exist_ok=True)
        
    def extend(self, controller: Controller) -> Controller:
        """
        Extend a controller with PDF capabilities.
        
        Args:
            controller: The controller to extend
            
        Returns:
            The extended controller
        """
        # Register the PDF export action with explicit param_model
        @controller.registry.action(
            'Export the current page as PDF',
            param_model=PDFExportParams
        )
        async def export_to_pdf(params: PDFExportParams, browser: BrowserContext):
            """Export the current page as a PDF file."""
            page = await browser.get_current_page()
            
            print("saving params:", params)
            # Generate path if not provided
            print("params.path: ", params.path)
            print("self.default_output_dir: ", self.default_output_dir)
            path = os.path.join(self.default_output_dir, params.path)
            
            # if not path:
            #     page_title = await page.title()
            #     sanitized_title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in page_title)
            #     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            #     filename = f"{sanitized_title}_{timestamp}.pdf"
            #     path = os.path.join(self.default_output_dir, filename)
            
            # # Handle if path is a directory
            # if os.path.isdir(path):
            #     page_title = await page.title()
            #     sanitized_title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in page_title)
            #     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            #     filename = f"{sanitized_title}_{timestamp}.pdf"
            #     path = os.path.join(self.default_output_dir, filename)
            
            if not path:
                msg = "NO PATHS to save to, not saving PDF."
                print(msg)
                return ActionResult(extracted_content=msg, include_in_memory=True)
            
            # Make sure path ends with .pdf
            if not path.lower().endswith('.pdf'):
                path += '.pdf'
            
            print("final path to save filed to:", path)
            # Ensure the directory exists
            # os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            # Configure PDF options
            pdf_options = {
                # 'printBackground': True,
                'format': 'A4',
                'margin': {
                    'top': '0.4in',
                    'right': '0.4in',
                    'bottom': '0.4in',
                    'left': '0.4in',
                }
            }
            
            try:
                # Export the page to PDF
                await page.pdf(path=path, **pdf_options)
                msg = f"✅ Page exported as PDF Standard to: {path}"
                print(msg)  # Optional console output
                return ActionResult(extracted_content=msg, include_in_memory=True)
            except Exception as e:
                error_msg = f"❌ Failed to export PDF: {str(e)}"
                print(error_msg)  # Optional console output
                return ActionResult(error=error_msg)
                
        # # Register an advanced PDF export action with more options
        # @controller.registry.action(
        #     'Export the current page as PDF with options',
        #     param_model=PDFExportOptionsParams
        # )
        # async def export_to_pdf_with_options(params: PDFExportOptionsParams, browser: BrowserContext):
        #     """Export the current page as a PDF file with customizable options."""
        #     page = await browser.get_current_page()
            
        #     # Generate path if not provided (same as basic function)
        #     path = params.path
        #     if not path:
        #         page_title = await page.title()
        #         sanitized_title = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in page_title)
        #         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        #         filename = f"{sanitized_title}_{timestamp}.pdf"
        #         path = os.path.join(self.default_output_dir, filename)
            
        #     # Ensure it's a .pdf file
        #     if not path.lower().endswith('.pdf'):
        #         path += '.pdf'
                
        #     # Ensure the directory exists
        #     os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
        #     # Configure PDF options
        #     pdf_options = {
        #         'printBackground': params.print_background,
        #         'format': params.format,
        #         'landscape': params.landscape,
        #         'scale': params.scale,
        #         'margin': {
        #             'top': '0.4in',
        #             'right': '0.4in',
        #             'bottom': '0.4in',
        #             'left': '0.4in',
        #         },
        #         'fullPage': params.full_page
        #     }
            
        #     try:
        #         # Export the page to PDF
        #         await page.pdf(path=path, **pdf_options)
        #         msg = f"✅ Page exported as PDF to: {path} (Format: {params.format}, Landscape: {params.landscape})"
        #         return ActionResult(extracted_content=msg, include_in_memory=True)
        #     except Exception as e:
        #         error_msg = f"❌ Failed to export PDF: {str(e)}"
        #         return ActionResult(error=error_msg)
        
        # # Return the extended controller
        return controller