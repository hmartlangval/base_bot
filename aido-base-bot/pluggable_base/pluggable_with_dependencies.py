"""
Example showing how to set up and use the dependency injection system
"""

import os
import logging
from pluggable import PluggableBot
from services import LoggerService, DatabaseService, ConfigService
from services.base_bot_shaken import BaseBotShaken
from services.queue_manager import QueueManager

# Extended bot class with dependency injection
class EnhancedBot(PluggableBot):
    def __init__(self, options=None, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        
        # Set up and register services
        self.setup_services()
        
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

# Example usage
if __name__ == "__main__":
    # Create bot with services
    bot = EnhancedBot()
    
    # Start the bot
    bot.start() 