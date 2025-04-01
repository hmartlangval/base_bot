# PluggableBot Framework

A flexible and extensible bot framework with support for dynamic plugin loading.

## Features

- Socket.io client for real-time communication
- Pluggable architecture with hot-reloading plugins in development mode
- Console-based command interface
- Channel management and message handling
- Extendable with custom message handlers

## Getting Started

### Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the simple message bot:

```bash
python pluggable.py
```

Or create your own custom bot by extending the `PluggableBot` class.

### Development Mode

The bot supports two modes:

1. **Production Mode** (default): Plugins are loaded once and not reloaded
2. **Development Mode**: Plugins are automatically reloaded when their source files change

To enable development mode, set the `BOT_DEV_MODE` environment variable:

```bash
# On Windows
set BOT_DEV_MODE=true
python pluggable.py

# On Linux/Mac
BOT_DEV_MODE=true python pluggable.py
```

You can also toggle the mode at runtime using the `/mode` command.

## Creating Plugins

Plugins should be placed in the `plugins` directory and follow the naming convention `<tag>_handler.py`.

Each plugin must implement a `handle_message` function that takes a message content as an argument and returns a response:

```python
# plugins/echo_handler.py
import time

def handle_message(message_data):
    """
    Simple echo handler plugin
    """
    print(f"Processing: {message_data}")
    time.sleep(1)  # simulate processing
    return f"Echo response: {message_data}"
```

Plugins are automatically loaded when a message contains a tag that matches the plugin name.

## Available Commands

- `/join [channel]` - Join a channel (default: general)
- `/leave` - Leave the current channel
- `/reconnect` - Attempt to reconnect to the server
- `/mode` - Toggle between development and production mode
- `/reload` - Force reload all plugins (dev mode only)
- `/exit` - Exit the bot
- `/help` - Show help message

## Creating a Custom Bot

To create a custom bot, extend the `PluggableBot` class and override the methods you need:

```python
from pluggable import PluggableBot

class CustomBot(PluggableBot):
    def __init__(self, options=None):
        custom_options = options or {}
        custom_options["bot_name"] = "My Custom Bot"
        super().__init__(custom_options)
    
    def should_handle_message(self, message):
        """Custom logic to determine if we should handle a message"""
        # Only respond to messages containing the word "hello"
        return "hello" in message.get("content", "").lower()
    
    def on_message(self, message):
        """Custom message handler"""
        sender = message.get("senderName", "Someone")
        content = message.get("content", "")
        
        # Create a personalized response
        response = f"Hello {sender}! I received your message: {content}"
        
        # Send the response
        if self.state["current_channel_id"]:
            self.send_message(response)

if __name__ == "__main__":
    bot = CustomBot()
    bot.start()
```

## Extending the Framework

You can override any of these methods to customize the behavior:

- `on_connect()` - Called when connected to server
- `on_disconnect()` - Called when disconnected from server
- `on_message(message)` - Called for messages not handled by plugins
- `should_handle_message(message)` - Determines if a message should be handled
- `handle_custom_command(command, args)` - Handle custom commands 