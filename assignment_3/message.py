
class Message:

    source = None
    destination = []
    end_destination = None
    start_time : int = 0
    end_time : int = 0
    message : str = ""
    default_ttl : int = 64

    # Note destination can be a list for a broadcast
    def __init__(self, source, destination, end_destination, start_time, end_time, message):
        self.source = source
        self.destination = destination
        self.start_time = start_time
        self.end_time = end_time
        self.message = message
        self.end_destination = end_destination
        self.ttl = self.default_ttl


    def before_message(self, message):
        if (self.start_time < message.start_time):
            return True
        return False

    def __str__(self):
        return f"start: {self.start_time}, end: {self.end_time}, source: {self.source}, dest: {self.destination}, message: {self.message}"

