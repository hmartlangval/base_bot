import importlib
import re
import threading
import queue
import json
import socketio
import sys
import signal
import datetime
import os
import time
import asyncio
import concurrent.futures
import gc
from __init__ import get_application_path

class PluggableBot:
    def __init__(self, options=None):
        # Initialize options with defaults and overrides
        options = options or {}
        
        base_path = get_application_path()
        
        # Check for dev mode in environment variables
        self.dev_mode = os.environ.get('BOT_DEV_MODE', 'false').lower() == 'true'
        
        # Default paths based on base_path
        default_plugins_path = options.get("plugins_path", os.path.join(base_path, "plugins"))
        
        # Bot configuration
        self.config = {
            "bot_id": options.get("bot_id", "pluggable-bot"),
            "bot_name": options.get("bot_name", "Pluggable Bot"),
            "bot_type": options.get("bot_type", "pluggable"),
            "server_url": options.get("server_url", "http://localhost:3000"),
            "default_channel": options.get("default_channel", "general"),
            "max_reconnect_attempts": int(options.get("max_reconnect_attempts", 5)),
            "socketio_path": options.get("socketio_path", "/api/socket"),
            "plugins_path": default_plugins_path
        }
        
        # Add base_path to sys.path to help imports
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        # Print path information for debugging
        self.base_path = base_path
        print(f"Application base path: {base_path}")
        print(f"Plugins path: {self.config['plugins_path']}")
        
        # Bot state
        self.state = {
            "current_channel_id": None,
            "is_connected": False,
            "connection_attempts": 0,
            "channel_states": {},  # Track active state of channels
            "active_plugins": {}   # Track currently running plugins
        }
        
        # Service/dependency registry
        self.services = {}
        
        # Global queue for results from plugin threads
        self.result_queue = queue.Queue()
        
        # Create a Socket.IO client
        self.sio = socketio.Client(
            reconnection=True,
            reconnection_attempts=self.config["max_reconnect_attempts"],
            reconnection_delay=1,
            reconnection_delay_max=5,
            request_timeout=20
        )
        
        # Create thread pool executor for async execution
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        
        # Store original signal handler
        self._original_sigint_handler = signal.getsignal(signal.SIGINT)
        
        # Store module timestamps for dev mode
        self.module_timestamps = {}
        
        # Create main asyncio event loop and task scheduler
        self.main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.main_loop)
        
        # Initialize the bot
        self.init()
        
        # Log dev mode status
        if self.dev_mode:
            self.print_message("🔧 Running in DEVELOPMENT mode - plugins will be dynamically reloaded")
        else:
            self.print_message("🚀 Running in PRODUCTION mode - plugin changes require restart")
    
    def init(self):
        """Initialize the bot"""
        self.setup_socket_handlers()
        
    def setup_socket_handlers(self):
        """Set up Socket.IO event handlers"""
        
        @self.sio.event
        def connect():
            self.state["is_connected"] = True
            self.state["connection_attempts"] = 0
            self.print_message("Connected to server")
            
            # Register the bot
            self.sio.emit("register", {
                "botId": self.config["bot_id"],
                "name": self.config["bot_name"],
                "type": self.config["bot_type"]
            })
            
            self.print_message(f'Registered as {self.config["bot_name"]} ({self.config["bot_id"]})')
            self.display_prompt()
            
            # Override in child class if needed
            self.on_connect()

        @self.sio.event
        def disconnect():
            self.state["is_connected"] = False
            self.print_message("Disconnected from server")
            self.display_prompt()
            
            # Override in child class if needed
            self.on_disconnect()

        @self.sio.event
        def connect_error(error):
            self.state["connection_attempts"] += 1
            self.print_message(f'Connection error: {str(error)}')
            
            if self.state["connection_attempts"] < self.config["max_reconnect_attempts"]:
                self.print_message(f'Reconnection attempt {self.state["connection_attempts"]}/{self.config["max_reconnect_attempts"]}...')
            else:
                self.print_message(f'Failed to connect after {self.config["max_reconnect_attempts"]} attempts.')
                self.print_message("Use /reconnect to try again or check server status.")
            
            self.display_prompt()
            
            # Override in child class if needed
            self.on_connect_error(error)

        @self.sio.on("new_message")
        def on_new_message(message):
            # Don't show our own messages again
            if message.get("senderId") != self.config["bot_id"]:
                self.print_message(f"{message.get('senderName')}: {message.get('content')}")
                
                if self.should_handle_message(message):
                    try:
                        # Process with plugins or custom handler
                        self.handle_message(message)
                    except Exception as e:
                        self.print_message(f"Error processing message: {e}")
            
            self.display_prompt()

        @self.sio.on("channel_status")
        def on_channel_status(data):
            self.print_message(f"Channel status: {data.get('channelId')} ({'active' if data.get('active') else 'inactive'})")
            self.print_message(f'Participants: {len(data.get("participants", []))}')
            
            # Update channel state
            self.state["channel_states"][data.get("channelId")] = data.get("active")
            
            self.display_prompt()
            
            # Override in child class if needed
            self.on_channel_status(data)

        @self.sio.on("bot_registered")
        def on_bot_registered(data):
            self.print_message(f"Bot registered: {data.get('name')} ({data.get('botId')})")
            self.display_prompt()
            
            # Auto join default channel
            self.process_command("/join general")
            
            # Override in child class if needed
            self.on_bot_registered(data)
    
    # Core functionality methods
    def should_handle_message(self, message):
        """Determine if the message should be handled by this bot"""
        return True
        # Default implementation
        # Override in child class for custom logic
         # Check if the channel is active before responding
        # if self.state["channel_states"].get(message.get("channelId")) is False:
        #     return False
        
        # # Base implementation: respond to messages that tag this bot
        # tags = message.get("tags", [])
        
        # print(f"Tags: {tags}")
        # print(f"Bot ID: {self.config['bot_id']}")
        # print(f"Result: {tags and self.config['bot_id'] in tags}")
        # return tags and self.config["bot_id"] in tags
    
    def handle_message(self, message):
        """Handle a new message"""
        # Default implementation using plugin system
        message_tags = message.get("tags", [])
        message_content = message.get("content")
        
        # Extract JSON data for plugins that need it
        message["jsonArray"] = self.extract_json_data_as_array(message)
        message["jsonBlock"] = self.extract_json_block(message_content)
        
        if message_tags:
            for tag in message_tags:
                # Determine full plugin file path
                plugin_filename = f"{tag}_handler.py"
                plugin_path = os.path.join(self.config['plugins_path'], plugin_filename)
                
                # First check if the file exists directly
                if os.path.exists(plugin_path):
                    try:
                        # Try to load the module from file path
                        import importlib.util
                        spec = importlib.util.spec_from_file_location(
                            f"{tag}_handler", 
                            plugin_path
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Create a unique execution ID
                        execution_id = f"{tag}_handler_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                        
                        # Execute in a thread
                        thread = threading.Thread(
                            target=self._execute_plugin_thread_from_module,
                            args=(module, message, execution_id)
                        )
                        thread.daemon = True
                        thread.start()
                        
                        # Track the active plugin
                        self.state["active_plugins"][execution_id] = {
                            "plugin_name": f"{tag}_handler",
                            "start_time": datetime.datetime.now(),
                            "status": "running"
                        }
                        
                        # Schedule check for results
                        self._schedule_task(self.check_results())
                        
                    except Exception as e:
                        self.print_message(f"Error loading plugin from file '{plugin_path}': {e}")
                else:
                    # Try module import approach (for bundled installation)
                    try:
                        # Several possible module paths to try
                        module_paths = [
                            f"{self.config['plugins_path']}.{tag}_handler",  # pluggable_base.plugins.echo_handler
                            f"plugins.{tag}_handler",                        # plugins.echo_handler (relative)
                            f"{tag}_handler"                                 # echo_handler (direct)
                        ]
                        
                        for module_path in module_paths:
                            try:
                                self.print_message(f"Trying to load plugin from module: {module_path}")
                                self.execute_plugin(module_path, message)
                                break  # If successful, stop trying other paths
                            except ImportError:
                                continue  # Try the next module path
                        else:
                            # None of the module paths worked
                            self.print_message(f"Plugin '{tag}_handler' could not be found or imported.")
                            
                    except Exception as e:
                        self.print_message(f"Error executing plugin '{tag}_handler': {e}")
        else:
            # Let the child class handle it
            self.on_message(message)
    
    def execute_plugin(self, plugin_name, message_data):
        """Load and execute a plugin"""
        # Create a unique ID for this plugin execution
        execution_id = f"{plugin_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # Start plugin in a separate thread that won't block the main bot
        thread = threading.Thread(
            target=self._execute_plugin_thread,
            args=(plugin_name, message_data, execution_id)
        )
        thread.daemon = True
        thread.start()
        
        # Track the active plugin
        self.state["active_plugins"][execution_id] = {
            "plugin_name": plugin_name,
            "start_time": datetime.datetime.now(),
            "status": "running"
        }
        
        # Start a background task to check for results
        self._schedule_task(self.check_results())
        
        return execution_id
    
    def _should_reload_module(self, module_name):
        """Check if a module should be reloaded"""
        if not self.dev_mode:
            return False
            
        # Convert module name to file path
        try:
            module = sys.modules.get(module_name)
            if not module:
                return False  # Module not loaded yet
                
            file_path = module.__file__
            if not file_path:
                return False
                
            # Check file modification time
            current_mtime = os.path.getmtime(file_path)
            last_mtime = self.module_timestamps.get(module_name, 0)
            
            if current_mtime > last_mtime:
                self.module_timestamps[module_name] = current_mtime
                return True
                
            return False
        except (AttributeError, OSError):
            return False
    
    def _execute_plugin_thread(self, plugin_name, message_data, execution_id):
        """Thread function to execute plugin, supporting both sync and async handlers"""
        try:
            # Check if module exists in sys.modules and needs reloading
            if plugin_name in sys.modules and self._should_reload_module(plugin_name):
                self.print_message(f"🔄 Hot reloading plugin: {plugin_name}")
                module = importlib.reload(sys.modules[plugin_name])
            else:
                # Import the module for the first time
                module = importlib.import_module(plugin_name)
                
                # Store initial timestamp if in dev mode
                if self.dev_mode and plugin_name not in self.module_timestamps:
                    file_path = module.__file__
                    if file_path:
                        self.module_timestamps[plugin_name] = os.path.getmtime(file_path)
            
            handler_function = getattr(module, "handle_message")
            plugin_result = None
            bot_instance = None
            
            # Check if the handler wants dependency injection
            # Look for a 'get_dependencies' function that returns a list of required dependencies
            dependencies = {}
            if hasattr(module, 'get_dependencies') and callable(module.get_dependencies):
                required_deps = module.get_dependencies()
                if isinstance(required_deps, list):
                    for dep_name in required_deps:
                        if self.has_service(dep_name):
                            dependencies[dep_name] = self.get_service(dep_name)
                        else:
                            self.print_message(f"Warning: Plugin {plugin_name} requested dependency '{dep_name}' which is not available")
            
            # Check if the handler is asynchronous
            if asyncio.iscoroutinefunction(handler_function):
                # Create a completely new event loop for this plugin execution
                loop = asyncio.new_event_loop()
                
                # Important: Set this new loop as the thread-local event loop
                # This ensures that any asyncio calls in this thread use this loop
                asyncio.set_event_loop(loop)
                
                try:
                    # Run the async function in the isolated loop
                    # Pass dependencies if the function accepts them
                    import inspect
                    sig = inspect.signature(handler_function)
                    
                    if len(sig.parameters) > 1 and 'deps' in sig.parameters:
                        # Function accepts deps parameter
                        plugin_result = loop.run_until_complete(handler_function(message_data, deps=dependencies))
                    else:
                        # Standard function with just message_data
                        plugin_result = loop.run_until_complete(handler_function(message_data))
                    
                    # Look for BaseBotShaken instances in the module globals
                    for var_name in dir(module):
                        var = getattr(module, var_name)
                        if hasattr(var, '__class__') and var.__class__.__name__ == 'BaseBotShaken':
                            bot_instance = var
                            break
                        
                    # Also inspect local variables in current frame for BaseBotShaken instances
                    if 'bot' in module.__dict__:
                        bot_instance = module.__dict__['bot']
                    
                    # If we found a BaseBotShaken instance, clean it up
                    if bot_instance and hasattr(bot_instance, 'cleanup'):
                        if asyncio.iscoroutinefunction(bot_instance.cleanup):
                            loop.run_until_complete(bot_instance.cleanup())
                        elif callable(bot_instance.cleanup):
                            bot_instance.cleanup()
                        self.print_message(f"Automatically cleaned up BaseBotShaken instance in {plugin_name}")
                    
                    # Run a final iteration to ensure all cleanups are processed
                    loop.run_until_complete(asyncio.sleep(0.1))
                except Exception as e:
                    self.print_message(f"Error in async plugin {plugin_name}: {str(e)}")
                    raise
                finally:
                    # Set the bot instance to None to help with garbage collection
                    if bot_instance:
                        bot_instance = None
                    
                    # Cancel all remaining tasks in this loop
                    pending = asyncio.all_tasks(loop)
                    if pending:
                        for task in pending:
                            task.cancel()
                        
                        # Allow tasks to respond to cancellation
                        try:
                            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                        except (asyncio.CancelledError, RuntimeError):
                            # Ignore cancellation errors
                            pass
                    
                    # Close the event loop but catch any errors
                    try:
                        loop.run_until_complete(loop.shutdown_asyncgens())
                    except (RuntimeError, GeneratorExit):
                        pass
                    
                    try:
                        loop.close()
                    except RuntimeError:
                        pass
                    
                    # Set thread loop to None to ensure garbage collection
                    asyncio.set_event_loop(None)
                    
                    # Force garbage collection
                    gc.collect()
            else:
                # Call the synchronous handler directly
                # Check if it wants dependencies
                import inspect
                sig = inspect.signature(handler_function)
                
                if len(sig.parameters) > 1 and 'deps' in sig.parameters:
                    # Function accepts deps parameter
                    plugin_result = handler_function(message_data, deps=dependencies)
                else:
                    # Standard function with just message_data
                    plugin_result = handler_function(message_data)
                
            # Store the result
            self.result_queue.put((plugin_name, plugin_result, execution_id))
            
            # Update plugin status
            self.state["active_plugins"][execution_id]["status"] = "completed"
            self.state["active_plugins"][execution_id]["end_time"] = datetime.datetime.now()
            
        except (ImportError, AttributeError) as e:
            self.result_queue.put((plugin_name, f"Error: {e}", execution_id))
            
            # Update plugin status
            self.state["active_plugins"][execution_id]["status"] = "error"
            self.state["active_plugins"][execution_id]["error"] = str(e)
            self.state["active_plugins"][execution_id]["end_time"] = datetime.datetime.now()
    
    async def check_results(self):
        """Check for results from plugin execution - async coroutine"""
        # Wait a bit for plugin execution
        await asyncio.sleep(0.1)
        while not self.result_queue.empty():
            plugin_name, result, execution_id = self.result_queue.get()
            
            # Get plugin execution details
            plugin_info = self.state["active_plugins"].get(execution_id, {})
            start_time = plugin_info.get("start_time")
            end_time = plugin_info.get("end_time", datetime.datetime.now())
            
            # Calculate execution time
            if start_time:
                execution_time = (end_time - start_time).total_seconds()
                self.print_message(f"Plugin '{plugin_name}' completed in {execution_time:.2f}s: {result}")
            else:
                self.print_message(f"Plugin '{plugin_name}' result: {result}")
            
            # If we're in a channel, send the result back
            if self.state["current_channel_id"]:
                self.send_message(result)
    
    def get_active_plugins(self):
        """Get information about currently active plugins"""
        active_count = 0
        completed_count = 0
        error_count = 0
        
        for execution_id, info in self.state["active_plugins"].items():
            status = info.get("status")
            if status == "running":
                active_count += 1
            elif status == "completed":
                completed_count += 1
            elif status == "error":
                error_count += 1
        
        return {
            "active": active_count,
            "completed": completed_count,
            "error": error_count,
            "total": len(self.state["active_plugins"])
        }
    
    # Event handler methods for child classes to override
    def on_connect(self):
        """Called when connected to server"""
        pass
    
    def on_disconnect(self):
        """Called when disconnected from server"""
        pass
    
    def on_connect_error(self, error):
        """Called on connection error"""
        pass
    
    def on_message(self, message):
        """Called when a message is received that wasn't handled by a plugin"""
        # Override in child class
        pass
    
    def on_channel_status(self, data):
        """Called when channel status changes"""
        pass
    
    def on_bot_registered(self, data):
        """Called when bot is registered with server"""
        pass
    
    # Utility methods
    def extract_json_block(self, content):
        """Extract JSON block from a message content"""
        if not content:
            return None
        import re
        json_matches = re.findall(r'```json(.*?)```', content, re.DOTALL)
        if json_matches:
            try:
                import json
                return json.loads(json_matches[0].strip())
            except:
                return None
        return None
        
    def extract_json_data(self, message):
        """Extract JSON data from a message which is in message's jsonData field"""
        jsonData = message.get("jsonData", None)
        if jsonData:
            json_key = list(jsonData.keys())[0]
            return jsonData[json_key]
        return None  
    
    def extract_json_data_as_array(self, message):
        """Extract JSON data as array from a message which is within [json][/json] tags"""
        jsonData = message.get("jsonData", None)
        if jsonData:
            json_keys = list(jsonData.keys())
            json_array = []
            for key in json_keys:
                json_array.append(jsonData[key])
            return json_array
        return []
    
    def print_message(self, message):
        """Print a message with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f'[{timestamp}] {message}')

    def display_prompt(self):
        """Display prompt to the user"""
        channel_status = f'({self.config["bot_id"]})[{self.state["current_channel_id"]}]' if self.state["current_channel_id"] else "[no channel]"
        
        channel_active = ""
        if self.state["current_channel_id"]:
            is_active = self.state["channel_states"].get(self.state["current_channel_id"], True)
            channel_active = "active" if is_active else "inactive"
        
        connection_status = "connected" if self.state["is_connected"] else "disconnected"
        
        # Get active plugin count
        active_plugins = self.get_active_plugins()
        plugin_indicator = f"[🔌{active_plugins['active']}]" if active_plugins['active'] > 0 else ""
        
        mode_indicator = "🔧" if self.dev_mode else "🚀"
        
        prompt = f'{mode_indicator} {channel_status} {plugin_indicator}'
        if channel_active:
            prompt += f" ({channel_active})"
        prompt += f" ({connection_status}) > "
        
        # Print the prompt without newline and flush
        print(prompt, end="", flush=True)

    def process_command(self, input_text):
        """Process user commands"""
        trimmed_input = input_text.strip()
        
        # Check if it's a command (starts with /)
        if trimmed_input.startswith('/'):
            command_parts = trimmed_input[1:].split(' ')
            command = command_parts[0].lower()
            args = command_parts[1:] if len(command_parts) > 1 else []
            
            if command == 'join':
                join_channel_id = args[0] if args else self.config["default_channel"]
                if not self.state["is_connected"]:
                    self.print_message("Not connected to server. Cannot join channel.")
                    return
                self.sio.emit("join_channel", join_channel_id)
                self.state["current_channel_id"] = join_channel_id
                self.print_message(f"Joining channel: {join_channel_id}")
                
            elif command == 'leave':
                if not self.state["current_channel_id"]:
                    self.print_message("Error: Not in a channel")
                    return
                if not self.state["is_connected"]:
                    self.print_message("Not connected to server. Cannot leave channel.")
                    return
                self.sio.emit("leave_channel", self.state["current_channel_id"])
                self.print_message(f'Leaving channel: {self.state["current_channel_id"]}')
                self.state["current_channel_id"] = None
                
            elif command == 'reconnect':
                if self.state["is_connected"]:
                    self.print_message("Already connected to server.")
                    return
                self.print_message("Attempting to reconnect to server...")
                try:
                    self.connect()
                except Exception as e:
                    self.print_message(f"Reconnection error: {str(e)}")
            
            elif command == 'mode':
                # Toggle development mode
                self.dev_mode = not self.dev_mode
                mode_name = "DEVELOPMENT" if self.dev_mode else "PRODUCTION"
                self.print_message(f"Switched to {mode_name} mode")
                
            elif command == 'reload':
                # Force reload all plugins
                if self.dev_mode:
                    plugin_count = 0
                    for module_name in list(sys.modules.keys()):
                        if module_name.startswith(f"{self.config['plugins_path']}."):
                            try:
                                importlib.reload(sys.modules[module_name])
                                plugin_count += 1
                                self.print_message(f"Reloaded plugin: {module_name}")
                            except Exception as e:
                                self.print_message(f"Error reloading {module_name}: {str(e)}")
                    
                    self.print_message(f"Reloaded {plugin_count} plugins")
                else:
                    self.print_message("Plugin reloading is only available in development mode")
                    self.print_message("Use /mode to switch to development mode")
            
            elif command == 'plugins':
                # Show plugin status
                plugins = self.get_active_plugins()
                self.print_message(f"Plugin Status:")
                self.print_message(f"- Active: {plugins['active']}")
                self.print_message(f"- Completed: {plugins['completed']}")
                self.print_message(f"- Errors: {plugins['error']}")
                self.print_message(f"- Total: {plugins['total']}")
                
                # List currently running plugins
                if plugins['active'] > 0:
                    self.print_message("Currently running plugins:")
                    for execution_id, info in self.state["active_plugins"].items():
                        if info.get("status") == "running":
                            start_time = info.get("start_time")
                            running_time = (datetime.datetime.now() - start_time).total_seconds()
                            self.print_message(f"- {info.get('plugin_name')} (running for {running_time:.2f}s)")
                    
            elif command == 'discover':
                services_dir = args[0] if args else None
                count = self.discover_services(services_dir)
                self.print_message(f"Discovered {count} services")
                return True
            
            elif command == 'help':
                self.show_help()
                    
            elif command == 'exit':
                self.cleanup_and_exit()
                
            else:
                # Give child classes a chance to handle custom commands
                if not self.handle_custom_command(command, args):
                    self.print_message(f"Unknown command: {command}")
        
        elif trimmed_input and self.state["current_channel_id"]:
            # Send a message to the current channel
            if not self.state["is_connected"]:
                self.print_message("Not connected to server. Cannot send message.")
                return
            
            # Check if the channel is active before sending a message
            if self.state["channel_states"].get(self.state["current_channel_id"]) is False:
                self.print_message(f'Cannot send message: Channel {self.state["current_channel_id"]} is inactive.')
                self.display_prompt()
                return
            
            self.send_message(trimmed_input)
            
        elif trimmed_input:
            self.print_message("Error: Not in a channel. Join a channel first with /join [channel]")
        
        self.display_prompt()
    
    def handle_custom_command(self, command, args):
        """Handle custom commands - override in child class"""
        # Child classes should override this
        return False
    
    def discover_services(self, services_dir=None):
        """Discover and load service definitions from a directory"""
        import importlib.util
        
        if services_dir is None:
            base_path = get_application_path()
            services_dir = os.path.join(base_path, "services")
        
        if not os.path.exists(services_dir):
            self.print_message(f"Services directory not found: {services_dir}")
            return 0
            
        self.print_message(f"Discovering services in: {services_dir}")
        service_count = 0
        
        for filename in os.listdir(services_dir):
            # Look for service modules, which could be Python files or directories with __init__.py
            if filename.endswith('_service.py'):
                service_name = filename[:-11]  # Remove _service.py suffix
                try:
                    # Add the services directory to path temporarily
                    sys.path.insert(0, os.path.dirname(services_dir))
                    
                    # Import the module dynamically
                    spec = importlib.util.spec_from_file_location(
                        service_name, 
                        os.path.join(services_dir, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for a service class
                    service_class_name = f"{service_name.capitalize()}Service"
                    if hasattr(module, service_class_name):
                        service_class = getattr(module, service_class_name)
                        
                        # Check if we already have this service registered
                        if service_name in self.services:
                            self.print_message(f"Service '{service_name}' is already registered, skipping")
                        else:
                            # Register the service with socket access
                            service_instance = service_class(self.sio)
                            self.register_service(service_name, service_instance)
                            service_count += 1
                            self.print_message(f"Loaded service: {service_name}")
                    else:
                        self.print_message(f"No service class found in {filename}")
                    
                    # Remove from path
                    sys.path.pop(0)
                    
                except Exception as e:
                    self.print_message(f"Error loading service {service_name}: {str(e)}")
            
            # Also check for directories that might be service packages
            elif os.path.isdir(os.path.join(services_dir, filename)) and not filename.startswith('__'):
                init_path = os.path.join(services_dir, filename, '__init__.py')
                if os.path.exists(init_path):
                    try:
                        # Try to import as a package
                        module_name = f"services.{filename}"
                        if module_name in sys.modules:
                            module = importlib.reload(sys.modules[module_name])
                        else:
                            module = importlib.import_module(module_name)
                        
                        # Look for a service class
                        service_class_name = f"{filename.capitalize()}Service"
                        if hasattr(module, service_class_name):
                            service_class = getattr(module, service_class_name)
                            
                            # Check if we already have this service registered
                            if filename in self.services:
                                self.print_message(f"Service '{filename}' is already registered, skipping")
                            else:
                                # Register the service with socket access
                                service_instance = service_class(self.sio)
                                self.register_service(filename, service_instance)
                                service_count += 1
                                self.print_message(f"Loaded service package: {filename}")
                    except Exception as e:
                        self.print_message(f"Error loading service package {filename}: {str(e)}")
        
        return service_count
    
    def send_message(self, content):
        """Send a message to the current channel"""
        self.sio.emit("message", {
            "channelId": self.state["current_channel_id"],
            "content": content
        })
        self.print_message(f"You sent: {content}")
    
    def show_help(self):
        """Show help message for available commands"""
        self.print_message("Available commands:")
        self.print_message("/join [channel] - Join a channel (default: general)")
        self.print_message("/leave - Leave the current channel")
        self.print_message("/reconnect - Attempt to reconnect to the server")
        self.print_message("/mode - Toggle between development and production mode")
        self.print_message("/reload - Force reload all plugins (dev mode only)")
        self.print_message("/plugins - Show status of running plugins")
        self.print_message("/discover [directory] - Discover and load services")
        self.print_message("/help - Show this help message")
        self.print_message("/exit - Exit the bot")

    # Main operations
    def connect(self):
        """Connect to the server"""
        self.sio.connect(
            url=self.config["server_url"],
            socketio_path=self.config["socketio_path"]
        )
    
    def signal_handler(self, sig, frame):
        """Handle signals for graceful exit"""
        print("\nCtrl+C detected! Shutting down gracefully...")
        self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """Clean up resources and exit"""
        if self.state["current_channel_id"] and self.state["is_connected"]:
            self.sio.emit("leave_channel", self.state["current_channel_id"])
        if self.state["is_connected"]:
            self.sio.disconnect()
        
        # Shutdown thread pool executor
        self.executor.shutdown(wait=False)
        
        # Stop the asyncio event loop
        self.main_loop.call_soon_threadsafe(self.main_loop.stop)
        
        self.print_message("Exiting bot")
        
        # Restore original signal handler
        signal.signal(signal.SIGINT, self._original_sigint_handler)
        sys.exit(0)
    
    def console_input_loop(self):
        """Console input loop to process user commands"""
        try:
            while True:
                user_input = input()
                self.process_command(user_input)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
    
    def start(self):
        """Start the bot"""
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.print_message(f"Starting {self.config['bot_name']}")
        self.print_message(f"Connecting to {self.config['server_url']}")
        
        try:
            # Start asyncio loop in a separate thread
            loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
            loop_thread.start()
            
            # Connect to the server
            self.connect()
            
            # Display initial prompt
            self.display_prompt()
            
            # Start console input loop
            self.console_input_loop()
            
        except Exception as e:
            self.print_message(f"Error starting bot: {e}")
            sys.exit(1)
            
    def _run_event_loop(self):
        """Run the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self.main_loop)
        self.main_loop.run_forever()
    
    def register_service(self, service_name, service_instance):
        """Register a service or dependency that plugins can access"""
        self.services[service_name] = service_instance
        self.print_message(f"Registered service: {service_name}")
        return service_instance
        
    def get_service(self, service_name):
        """Get a registered service by name"""
        if service_name not in self.services:
            raise KeyError(f"Service not found: {service_name}")
        return self.services[service_name]
        
    def has_service(self, service_name):
        """Check if a service is registered"""
        return service_name in self.services

    def _schedule_task(self, coroutine):
        """Schedule a coroutine to run in the background"""
        # Run in executor to avoid blocking and ensure it works in the main thread
        future = asyncio.run_coroutine_threadsafe(coroutine, self.main_loop)
        return future

    def _execute_plugin_thread_from_module(self, module, message, execution_id):
        """Execute a plugin from a directly loaded module"""
        try:
            if not hasattr(module, "handle_message"):
                raise AttributeError(f"Module does not have handle_message function")
                
            handler_function = module.handle_message
            plugin_result = None
            bot_instance = None
            plugin_name = execution_id.split('_')[0] + "_handler"
            
            # Check if the handler wants dependency injection
            dependencies = {}
            if hasattr(module, 'get_dependencies') and callable(module.get_dependencies):
                required_deps = module.get_dependencies()
                if isinstance(required_deps, list):
                    for dep_name in required_deps:
                        if self.has_service(dep_name):
                            dependencies[dep_name] = self.get_service(dep_name)
                        else:
                            self.print_message(f"Warning: Plugin {plugin_name} requested dependency '{dep_name}' which is not available")
            
            # Rest of the function identical to _execute_plugin_thread
            if asyncio.iscoroutinefunction(handler_function):
                # Create a completely new event loop for this plugin execution
                loop = asyncio.new_event_loop()
                
                # Important: Set this new loop as the thread-local event loop
                asyncio.set_event_loop(loop)
                
                try:
                    # Run the async function in the isolated loop
                    # Pass dependencies if the function accepts them
                    import inspect
                    sig = inspect.signature(handler_function)
                    
                    if len(sig.parameters) > 1 and 'deps' in sig.parameters:
                        # Function accepts deps parameter
                        plugin_result = loop.run_until_complete(handler_function(message, deps=dependencies))
                    else:
                        # Standard function with just message_data
                        plugin_result = loop.run_until_complete(handler_function(message))
                    
                    # Look for BaseBotShaken instances in the module globals
                    for var_name in dir(module):
                        var = getattr(module, var_name)
                        if hasattr(var, '__class__') and var.__class__.__name__ == 'BaseBotShaken':
                            bot_instance = var
                            break
                        
                    # Also inspect local variables in current frame for BaseBotShaken instances
                    if 'bot' in module.__dict__:
                        bot_instance = module.__dict__['bot']
                    
                    # If we found a BaseBotShaken instance, clean it up
                    if bot_instance and hasattr(bot_instance, 'cleanup'):
                        if asyncio.iscoroutinefunction(bot_instance.cleanup):
                            loop.run_until_complete(bot_instance.cleanup())
                        elif callable(bot_instance.cleanup):
                            bot_instance.cleanup()
                        self.print_message(f"Automatically cleaned up BaseBotShaken instance in {plugin_name}")
                    
                    # Run a final iteration to ensure all cleanups are processed
                    loop.run_until_complete(asyncio.sleep(0.1))
                except Exception as e:
                    self.print_message(f"Error in async plugin {plugin_name}: {str(e)}")
                    raise
                finally:
                    # Set the bot instance to None to help with garbage collection
                    if bot_instance:
                        bot_instance = None
                    
                    # Cancel all remaining tasks in this loop
                    pending = asyncio.all_tasks(loop)
                    if pending:
                        for task in pending:
                            task.cancel()
                        
                        # Allow tasks to respond to cancellation
                        try:
                            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                        except (asyncio.CancelledError, RuntimeError):
                            # Ignore cancellation errors
                            pass
                    
                    # Close the event loop but catch any errors
                    try:
                        loop.run_until_complete(loop.shutdown_asyncgens())
                    except (RuntimeError, GeneratorExit):
                        pass
                    
                    try:
                        loop.close()
                    except RuntimeError:
                        pass
                    
                    # Set thread loop to None to ensure garbage collection
                    asyncio.set_event_loop(None)
                    
                    # Force garbage collection
                    gc.collect()
            else:
                # Call the synchronous handler directly
                # Check if it wants dependencies
                import inspect
                sig = inspect.signature(handler_function)
                
                if len(sig.parameters) > 1 and 'deps' in sig.parameters:
                    # Function accepts deps parameter
                    plugin_result = handler_function(message, deps=dependencies)
                else:
                    # Standard function with just message_data
                    plugin_result = handler_function(message)
            
            # Store the result
            self.result_queue.put((plugin_name, plugin_result, execution_id))
            
            # Update plugin status
            self.state["active_plugins"][execution_id]["status"] = "completed"
            self.state["active_plugins"][execution_id]["end_time"] = datetime.datetime.now()
            
        except Exception as e:
            self.result_queue.put((plugin_name, f"Error: {e}", execution_id))
            
            # Update plugin status
            self.state["active_plugins"][execution_id]["status"] = "error"
            self.state["active_plugins"][execution_id]["error"] = str(e)
            self.state["active_plugins"][execution_id]["end_time"] = datetime.datetime.now()