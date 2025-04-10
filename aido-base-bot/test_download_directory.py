import json
import time
import os

from base_bot import BaseBot
# Set root path to aido-base-bot
# root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# os.chdir(root_path)

# json_data = {
#     "order_number": "WTS-25-000016 Order",
#     "s_data": {
#         "x_county": "Pasco",
#         "x_property_address": "13127 Keel Court, Hudson, FL 34667",
#         "x_account_number": "",
#         "x_house_number": "13127",
#         "x_street_name": "Keel Court",
#         "x_city": "Hudson",
#         "x_zip_code": "34667"
#     }
# }

# json_data = {
#   "order_number": "WTS-25-000016 Order",
#   "s_data": {
#     "x_county": "pasco",
#     "x_property_address": "13127 Keel Court, Hudson, FL 34667",
#     "x_account_number": "",
#     "x_house_number": "13127",
#     "x_street_name": "Keel Court",
#     "x_city": "Hudson",
#     "x_zip_code": "34667"
#   },
#   "context": {
#     "pdf_path": "http://localhost:3000/api/data/1743612794545-WTS-25-000016 Order.pdf",
#     "original_filename": "WTS-25-000016 Order.pdf",
#     "file_type": "application/pdf",
#     "id": "67ed6b7d1bc731e14544f672"
#   }
# }
# singified_json = json.dumps(json_data).replace('"', '\\"')
# print('string', singified_json)

class BB(BaseBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def generate_response(self, message):
        print("testing custom downloads directory")
        
        config = self.config["downloads_path"]
        config2 = self.config["custom_downloads_path"]
        
        # json_data = self.extract_json_data(message)
        
        # if json_data:
        #     order_number = json_data.get("order_number")
        #     if order_number:
        #         new_dl_path = self.create_custom_downloads_directory(order_number)
        #         print(new_dl_path)
        
        
        return super().generate_response(message)

bot = BB(options={
    "bot_id": "tdd",
    "bot_name": "test download directory creation",
    # "downloads_path": "E:/nothing_downloads",
    "autojoin_channel": "general"
})


bot.start()
bot.join()
bot.cleanup()


        
        
        



