class Message:

    source = None
    destination = None
    start_time = 0
    end_time = 0
    message = ""

    def __init__(self, source, destination, start_time, end_time, message):
        self.source = source
        self.destination = destination
        self.start_time = start_time
        self.end_time = end_time
        self.message = message

    def collides(self, message):
        if (self.start_time < message.end_time):
            return True
        if (self.end_time > message.start_time):
            return True
        return False

    def before_message(self, message):
        if (self.start_time < message.start_time):
            return True
        return False
