"""
Example showing how to set up and use the dependency injection system
"""

import importlib
import os
import logging
import sys
from pluggable import PluggableBot
from services import LoggerService, DatabaseService, ConfigService
from services.base_bot_shaken import BaseBotShaken
from services.queue_manager import QueueManager
from __init__ import get_application_path

# Extended bot class with dependency injection
class EnhancedBot(PluggableBot):
    def __init__(self, options=None, *args, **kwargs):
        
        base_path = get_application_path()
        default_options = {
            "plugins_path": os.path.join(base_path, "plugins"),
            "services_path": os.path.join(base_path, "services"),
            "config_path": os.path.join(base_path, "config")
        }
        
        # Merge with provided options
        if options:
            for key, value in default_options.items():
                if key not in options:
                    options[key] = value
        else:
            options = default_options
            
        super().__init__(options, *args, **kwargs)
        
        # Set up and register services
        self.setup_services()
        
        
        # Discover additional services
        self.discover_services(options["services_path"])
    
    
    def discover_services(self, services_dir=None):
        """Discover and load service definitions from a directory"""
        if services_dir is None:
            services_dir = os.path.join(get_application_path(), "services")
        
        if not os.path.exists(services_dir):
            self.print_message(f"Services directory not found: {services_dir}")
            return
            
        self.print_message(f"Discovering services in: {services_dir}")
        service_count = 0
        
        for filename in os.listdir(services_dir):
            if filename.endswith("_service.py"):
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
                        self.register_service(service_name, service_class)
                        service_count += 1
                        self.print_message(f"Loaded service: {service_name}")
                    else:
                        self.print_message(f"No service class found in {filename}")
                    
                    # Remove from path
                    sys.path.pop(0)
                    
                except Exception as e:
                    self.print_message(f"Error loading service {service_name}: {str(e)}")
        
        self.print_message(f"Discovered {service_count} services")
        return service_count

    def setup_services(self):
        """Set up and register services for dependency injection"""
        # Register services with socket access
        logger_service = self.register_service("logger", LoggerService)
        db_service = self.register_service("database", DatabaseService)
        config_service = self.register_service("config", ConfigService)
        browser_service = self.register_service("browser", BaseBotShaken)
        queue_manager_service = self.register_service("queue_manager", QueueManager)
        
        # Use the config service for bot configuration
        self.config["bot_name"] = config_service.get("bot_name", self.config["bot_name"])

    def register_service(self, service_name, service_instance_or_class, *args, **kwargs):
        """Register a service or dependency that plugins can access
        
        This can accept either:
        - An already instantiated service
        - A service class that will be instantiated with socket access
        """
        if isinstance(service_instance_or_class, type):
            # It's a class, instantiate it with socket access and args
            service = service_instance_or_class(self.sio, *args, **kwargs)
            self.services[service_name] = service
            self.print_message(f"Registered service: {service_name} (with socket access)")
        else:
            # It's already an instance, just register it
            service = service_instance_or_class
            # If service has socket_io attribute, update it
            if hasattr(service, 'set_socket_io'):
                service.set_socket_io(self.sio)
                self.print_message(f"Registered service: {service_name} (with socket access)")
            else:
                self.print_message(f"Registered service: {service_name}")
            self.services[service_name] = service
            
        return service

    def handle_custom_command(self, command, args):
        """Handle custom commands"""
        if command == 'discover':
            services_dir = args[0] if args else None
            self.discover_services(services_dir)
            return True
        
        # Pass to parent class if not handled
        return super().handle_custom_command(command, args)

# Example usage
if __name__ == "__main__":
    # Create bot with services
    bot = EnhancedBot()
    
    # Start the bot
    bot.start() 