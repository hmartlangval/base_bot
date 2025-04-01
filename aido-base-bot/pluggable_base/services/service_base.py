# Base class for socket-aware services
class SocketAwareService():
    def __init__(self, socket_io=None, options=None, *args, **kwargs):
        self.socket_io = socket_io
        self.options = options
    
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
