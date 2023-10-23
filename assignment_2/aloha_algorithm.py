import random

from host import Host
from message import Message


class Aloha:
    counter = 0
    begin_random = 0
    end_random = 20
    states = ["IDLE", "SENDING"]

    def __init__(self):
        pass

    def process_algorithm(self, node: Host, round_counter, incoming_message):
        message = None
        if incoming_message == None:
            message = self.send_message(node, round_counter)
        # message = Message(origin, neighbours[0], 20, 25, "hello")
        return message

    def send_message(self, node, round_counter):
        message = None
        neigbors = node.get_neighbors()

        start_time = random.randint(self.begin_random, self.end_random)
        end_time = start_time + 5

        if len(neigbors) > 0:
            random_neigbour = random.randint(0, len(neigbors) - 1)
            destination = neigbors[random_neigbour].mac
            message = Message(node.mac, destination, start_time, end_time, "hello")

        self.begin_random = end_time
        self.end_random = self.begin_random + 10
        self.counter += 1

        return message
