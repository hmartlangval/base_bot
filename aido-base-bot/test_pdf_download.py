import json
import time
import os
import asyncio
import logging
from functools import wraps
import inspect
from dotenv import load_dotenv
load_dotenv()
from base_bot.browser_client_base_bot import BrowserClientBaseBot


class TestBrowserClient(BrowserClientBaseBot):
    
    def __init__(self, options=None, *args, **kwargs):
        # Apply monkey patches before initializing the bot
        # apply_browser_use_patches()
        options = options if options else kwargs.get('options', {})
        
        downloads_path = options.get("downloads_path", None)
        if not downloads_path:
            downloads_path = os.getenv("DOWNLOADS_PATH", None)
            if downloads_path:
                options.setdefault("downloads_path", downloads_path)
                kwargs['options'] = options
                
        super().__init__(options, *args, **kwargs) 
        
    async def generate_response(self, message):
        print("generate_response: ", message)
        
        order_number = None
        json_data = self.extract_json_data(message)
        if json_data:
            order_number = json_data.get("order_number")
            if order_number:
                new_dl_path = self.create_custom_downloads_directory(order_number)
                print(new_dl_path)
        
        filename =  f"{order_number}_TEST.pdf" if order_number else None
        
        result = await self.call_agent("You are navigating a webpage http://127.0.0.1:5500/aido-base-bot/examples/simplepage.html. click on the download link to download a file", None, None, 
                                       {
                                           "annual_pdf_filename": filename
                                        }
                                    )
        print(result)
        
        is_success = self.check_success_or_failure(result)
        print("is_success: ", is_success)
        
        return 'done'



bot = TestBrowserClient(options={
    "bot_type": "task_bot",
    "bot_id": "pdfdownloadbot",
    "bot_name": "PDF Download Bot",
    'model': 'gpt-4o-mini',
    'downloads_path': 'downloads',
    'autojoin_channel': 'general',
})

bot.start()

import requests
def call_rest_api():
    data = {
        "channelId": "general",
        "content": "@pdfdownloadbot download the pdf file"
    }
    try:
        response = requests.post('http://localhost:3000/api/channels/general/sendMessage', json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()  # Return the response as JSON
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
call_rest_api()
    
bot.join()
    
bot.cleanup()
    
# bot.input_thread.join()




