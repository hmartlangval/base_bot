import json
from base_bot import BaseBot
from dotenv import load_dotenv

load_dotenv()

class TestBotStateManagement(BaseBot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def generate_response(self, message):
        
        content = message.get("content", None)
        print(f"Received message: {content}")
        
        return "printer"
        
        # self.get_aido_order("67f68f59b35a8dcab4fd7edd")
        
        # if "start" in content:
        #     botstates = self.get_bot_state()
        #     if any(task.id == "task1" and task.status == "in_progress" for task in botstates.tasks):
        #         return "Task currently in progress. Please wait for it to complete."
        #     self.new_task_started("task1", "test task")
        # elif "end" in content:
        #     self.task_ended("task1", "test result")
        # elif "status" in content:
        #     bot_state = self.get_bot_state()
        #     return f"Bot state: {json.dumps(bot_state.to_dict(), indent=4)}"
        # return "No default response"
        
bot = TestBotStateManagement(options={
    "bot_id": "tsm",
    "bot_name": "Test State Management",
    "autojoin_channel": "general"    
})

bot.start()
bot.join()
bot.cleanup()
