import os
from dotenv import load_dotenv

load_dotenv()

class ConfigurableApp():
    def __init__(self, options=None):
        
        self.options = options or {}
        
        # new approach where we are using ENV downloads path if not specified
        downloads_path = self.options.get("downloads_path", None)
        if not downloads_path:
            downloads_path = os.getenv("DOWNLOADS_PATH", None)
            if downloads_path:
                self.options.setdefault("downloads_path", downloads_path)
        
        # keeping this for backwards compatibility
        opt_downloads_path = self.options.get('downloads_path', "downloads") if self.options else "downloads"
        downloads_path = opt_downloads_path if os.path.isabs(opt_downloads_path) else os.path.join(os.getcwd(), opt_downloads_path)
        
        # downloads_path = os.path.join(os.getcwd(), 'downloads')
        if not os.path.exists(downloads_path):  
            os.makedirs(downloads_path, exist_ok=True)
            
        print('configuration config for parent')
        self.config = {
            "downloads_path": downloads_path,
            "custom_downloads_path": downloads_path,
            "browser_headless": self.options.get('browser_headless', False) if self.options else False
        }
        
    def create_custom_downloads_directory(self, relative_folder_path):
        cfg_downloads_path = self.config["downloads_path"]
            
        if not relative_folder_path:
            return cfg_downloads_path
        
        downloads_path = cfg_downloads_path if os.path.isabs(cfg_downloads_path) else os.path.join(os.getcwd(), cfg_downloads_path)
        
        new_downloads_path = os.path.join(downloads_path, relative_folder_path)
        if not os.path.exists(new_downloads_path):
            os.makedirs(new_downloads_path, exist_ok=True)
            return new_downloads_path
        else:
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_downloads_path_with_timestamp = f"{new_downloads_path}_{timestamp}"
            
            os.makedirs(new_downloads_path_with_timestamp, exist_ok=True)
            print(f"Folder {new_downloads_path_with_timestamp} created")
            return new_downloads_path_with_timestamp
        
        # downloads_path = cfg_downloads_path if os.path.isabs(cfg_downloads_path) else os.path.join(os.getcwd(), cfg_downloads_path)
        
        # new_downloads_path = os.path.join(downloads_path, relative_folder_path)
        # if not os.path.exists(new_downloads_path):  
        #     os.makedirs(new_downloads_path, exist_ok=True)
            
        # self.config["custom_downloads_path"] = new_downloads_path
        # return new_downloads_path

