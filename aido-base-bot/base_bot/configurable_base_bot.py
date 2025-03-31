import os

class ConfigurableApp():
    def __init__(self, options=None):
        
        self.options = options or {}
        
        opt_downloads_path = self.options.get('downloads_path', "downloads") if self.options else "downloads"
        downloads_path = opt_downloads_path if os.path.isabs(opt_downloads_path) else os.path.join(os.getcwd(), opt_downloads_path)
        
        # downloads_path = os.path.join(os.getcwd(), 'downloads')
        if not os.path.exists(downloads_path):  
            os.makedirs(downloads_path, exist_ok=True)
            
        print('configuration config for parent')
        self.config = {
            "downloads_path": downloads_path,
            "browser_headless": self.options.get('browser_headless', False) if self.options else False
        }

