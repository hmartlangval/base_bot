from base_bot import BaseBot
from dotenv import load_dotenv

load_dotenv()

class TestTaskCreation(BaseBot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
bot = TestTaskCreation(options={
    "bot_id": "ttc",
    "bot_name": "Test Task Creation",
    "autojoin_channel": "general"
})

bot.start()
bot.join()
bot.cleanup()
