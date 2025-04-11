import json
from base_bot import BaseBot
from dotenv import load_dotenv

load_dotenv()

class TestPrivateMessageSender(BaseBot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setup_event_listeners()

    # def on_private_message(self, message):
        # self.print_message(f"Private message received: { message }")
        # msg_type = message.get("msg_type", None)
        # if msg_type == "enquire_if_available-response":
        # if msg_type == "task_state-response":
        #     self.print_message(f"Task state response received: { message }")

    async def generate_response(self, message):
        self.socket.emit("message", {
            "channelId": "general",
            "content": "Checking if pmtestrecipient can receive new task"
        })
    
        
        print("CHECKING IF CAN RECEIVE NEW TASK")
        can_receive_new_task = await self.can_bot_receive_new_task("pmtestrecipient")
        self.socket.emit("message", {
            "channelId": "general",
            "content": f"Can receive new task?: { can_receive_new_task }"
        })
        print("Can receive new task:", can_receive_new_task)
    
        
        return "none"
        
    # def setup_event_listeners(self):
    #     """Set up event listeners for events from parent class"""
    #     if hasattr(self, 'on') and callable(self.on):
    #         self.on('private_message', self.on_private_message)
        
    # def on_private_message(self, message):
    #     self.print_message(f"Private message at leaf node: {message}")
    #     # self.emit("private_message", message)
        
bot = TestPrivateMessageSender(options={
    "bot_id": "pmtestsender",
    "bot_name": "Private Message Test Sender",
    "autojoin_channel": "general"    
})

bot.start()
bot.join()
bot.cleanup()
