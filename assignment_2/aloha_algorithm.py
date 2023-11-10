import random

from host import Host
from message import Message


class Aloha:
    def __init__(self, message_length: int, send_freq_interval: (int, int)):
        self.counter = 0
        self.message_send = False
        self.states = ["IDLE", "SENDING"]
        self.message_length = message_length
        self.random_interval = send_freq_interval
        self.start_random = 0

        self.start_time = 0
        self.end_time = 0

    def process_algorithm(self, node: Host, round_counter, incoming_message):
        message = None

        if round_counter > self.start_time+1:
            self.message_send = False

        if incoming_message is None and self.message_send is False:
            message = self.send_message(node, round_counter)
            self.message_send = True

        return message

    def send_message(self, node, round_counter):
        message = None
        neigbors = node.get_neighbors()

        self.start_time = random.randint(self.start_random + self.random_interval[0], self.start_random + self.random_interval[1])
        self.end_time = self.start_time + self.message_length

        if len(neigbors) > 0:
            random_neigbour = random.randint(0, len(neigbors) - 1)
            destination = neigbors[random_neigbour].mac
            message = Message(node.mac, destination, self.start_time, self.end_time, "hello")

        self.start_random = self.start_time
        self.counter += 1

        return message
