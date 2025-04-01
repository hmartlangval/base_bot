import os
import logging

# Base class for socket-aware services
class SocketAwareService:
    def __init__(self, socket_io=None):
        self.socket_io = socket_io
    
    def set_socket_io(self, socket_io):
        """Set the socket.io client instance"""
        self.socket_io = socket_io
    
    def send_message(self, channel_id, content):
        """Send a message to a channel"""
        if self.socket_io:
            self.socket_io.emit("message", {
                "channelId": channel_id,
                "content": content
            })
            return True
        return False

# Example Logger service with socket awareness
class LoggerService(SocketAwareService):
    def __init__(self, socket_io=None):
        super().__init__(socket_io)
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PluggableBot')
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
        # Optionally broadcast important logs
        # self.send_message(channel_id, f"[LOG] {message}")
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)

# Example Database service with socket awareness
class DatabaseService(SocketAwareService):
    def __init__(self, socket_io=None):
        super().__init__(socket_io)
        self.responses = []
        self.info("Database service initialized")
    
    def info(self, message):
        print(f"[Database] {message}")
    
    def store_response(self, timestamp, message, response):
        """Store a response in the database"""
        self.responses.append({
            "timestamp": timestamp,
            "message": message,
            "response": response
        })
        self.info(f"Stored response, total records: {len(self.responses)}")
        
        # Optionally notify about database updates
        # if self.socket_io and len(self.responses) % 10 == 0:
        #     self.send_message(channel_id, f"Database milestone: {len(self.responses)} records")
    
    def get_responses(self):
        """Get all stored responses"""
        return self.responses

# Example Config service with socket awareness
class ConfigService(SocketAwareService):
    def __init__(self, socket_io=None):
        super().__init__(socket_io)
        # Default configuration
        self.config = {
            "echo_wait_time": 2,
            "bot_name": "Enhanced Pluggable Bot",
            "log_level": "INFO"
        }
        
        # Load any environment variables that override defaults
        if os.environ.get('ECHO_WAIT_TIME'):
            self.config['echo_wait_time'] = float(os.environ.get('ECHO_WAIT_TIME'))
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def __getitem__(self, key):
        """Allow dict-like access to config"""
        return self.config.get(key)
