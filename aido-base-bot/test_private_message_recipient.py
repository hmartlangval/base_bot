import asyncio
import json
from base_bot import BaseBot
from dotenv import load_dotenv
import uuid

load_dotenv()

class TestPrivateMessageRecipient(BaseBot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setup_event_listeners()
        
    async def generate_response(self, message):
        self.socket.emit("message", {
            "channelId": "general",
            "content": "Starting new task"
        })
        
        #generate some random task id and start, wait for 10 seconds and complete the task
        uuid1 = str(uuid.uuid4())
        bot_state = self.get_bot_state()
        taskCount = len(bot_state.tasks or [])
        self.new_task_started(uuid1, "Robotic Task - " + str(taskCount))
        
        await asyncio.sleep(10)
        self.task_ended(uuid1)
        return f"Task completed, {taskCount} tasks remaining"
        
    # def setup_event_listeners(self):
    #     """Set up event listeners for events from parent class"""
    #     if hasattr(self, 'on') and callable(self.on):
    #         self.on('private_message', self.on_private_message)
        
    # def on_private_message(self, message):
    #     self.print_message(f"Private message at leaf node2e: {message}")
    #     self.print_message("replying to sender using private message")
        
    #     msg_type = message.get("msg_type", None)
    #     #you received a private message aobut task_state
    #     if msg_type == "task_state":
    #         self.print_message("task state message received, sending task state response")
    #         self.socket.emit("private-bot", {
    #             "targetBotIds": [message["senderId"]],
    #             "msg_type": "task_state-response",
    #             "data": {
    #                 "tasks": self.get_bot_state().get("tasks", [])
    #             }
    #         })
        
    #     # self.socket.emit("private-bot", {
    #     #     "targetBotIds": [message["senderId"]],
    #     #     "data": {
    #     #         "content": "This is in response to your private message."
    #     #     }
    #     # })  
        
    #     # self.emit("private_message", message)
        
bot = TestPrivateMessageRecipient(options={
    "bot_id": "pmtestrecipient",
    "bot_name": "Private Message Test Recipient",
    "autojoin_channel": "general"    
})

bot.start()
bot.join()
bot.cleanup()
