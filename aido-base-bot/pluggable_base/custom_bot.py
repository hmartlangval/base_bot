from pluggable import PluggableBot

class CustomBot(PluggableBot):
    """
    Custom bot implementation that extends the PluggableBot base class
    and focuses only on message handling.
    """
    
    def __init__(self, options=None):
        # You can provide custom options when initializing
        custom_options = options or {}
        custom_options["bot_name"] = custom_options.get("bot_name", "Custom Bot")
        custom_options["bot_id"] = custom_options.get("bot_id", "custombot")
        
        # Initialize the parent class
        super().__init__(custom_options)
    
    
    def on_message(self, message):
        """
        Custom message handler - this is the primary function that needs
        to be implemented in a child class
        """
        sender = message.get("senderName", "Someone")
        content = message.get("content", "")
        
        # Create a personalized response
        response = f"Hello {sender}! I received your message: {content}"
        
        # Send the response back to the channel
        if self.state["current_channel_id"]:
            self.send_message(response)
    
    def on_connect(self):
        """Custom connect handler"""
        self.print_message("CustomBot connected and ready to chat!")
    
    def handle_custom_command(self, command, args):
        """Handle custom commands specific to this bot"""
        if command == 'hello':
            self.print_message("Hello there! This is a custom command.")
            return True
        return False

# Run the custom bot if this file is executed directly
if __name__ == "__main__":
    bot = CustomBot()
    bot.start() 