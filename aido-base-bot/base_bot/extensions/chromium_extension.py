import os
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from base_bot.types import BrowserSessionConfig

class ChromiumExtension:
    """
    Extension to customize Chromium launch arguments and preferences.
    """
    @staticmethod
    def extend_browser(
        session_config: BrowserSessionConfig = None,
        configuration=None,
        browser_args=None,
        **kwargs
    ) -> Browser:
        
        headless = kwargs.pop('headless', False)
        
        args = [
            "--disable-features=ChromeWhatsNewUI",
        ]
        
        downloads_path = configuration.get('custom_downloads_path')
        
        if browser_args:
            args.extend(browser_args)
        
        # Create a browser context config with our custom attributes
        context_config = BrowserContextConfig(
            save_downloads_path=downloads_path
        )
        
        # Add our custom attribute to the context config
        # BrowserContextConfig is a dataclass, so we can set attributes directly
        if session_config:
            for key, value in session_config.items():
                setattr(context_config, key, value)
            
        config = BrowserConfig(
            extra_chromium_args=args,
            headless=headless,
            new_context_config=context_config
        )
        
        browser = Browser(
            config=config,
        )
        
        return [browser, context_config]
        
    
    @staticmethod
    def extend_browser_wip(
        browser_args=None,
        pdf_save_directory=None,
        **kwargs
    ) -> Browser:
        """
        Create a Browser instance with custom Chromium arguments and preferences.
        
        Args:
            browser_args: Custom arguments to pass to Chromium
            pdf_save_directory: Directory where PDFs should be saved
            **kwargs: Additional arguments to pass to Browser constructor
            
        Returns:
            A Browser instance with custom configuration
        """
        
        # Create downloads folder in current directory.
        downloads_path = os.path.join(os.getcwd(), 'downloads')  

        # Ensure the downloads directory exists.
        if not os.path.exists(downloads_path):  
            os.makedirs(downloads_path, exist_ok=True)

        # Default arguments to disable certain UI features
        # IMPORTANT: We're NOT disabling print preview anymore since we need access
        # to the printer selection dropdown to select Microsoft Print to PDF
        args = [
            "--disable-features=ChromeWhatsNewUI",
        ]
        
        # Add download directory argument
        download_dir = kwargs.pop('download_dir', downloads_path)
        args.append(f"--download-default-directory={download_dir}")
        
        # Store PDF save directory
        pdf_dir = pdf_save_directory or download_dir
        os.environ['PDF_SAVE_DIRECTORY'] = pdf_dir
        
        # Add custom browser arguments if provided
        if browser_args:
            args.extend(browser_args)
            
        # Get the headless parameter if it exists in kwargs, otherwise default to False
        headless = kwargs.pop('headless', False)
        
        # Create and return browser with custom config
        config = BrowserConfig(
            extra_chromium_args=args,
            headless=headless,
            **kwargs
        )
        
        return Browser(config=config)