import math
import sys
import random
from typing import Dict, List

from host import Host
from message import Message

class simulator:

    counter: int = 0
    nodes: List[Host] = []
    timeout: int = sys.maxsize

    # This is an interesting one, this dictionary keeps track for all nodes if their sending channel is clear.
    # How it does this is done because every node that decides to transmit will add their transmission time window
    # to the dictionary of themselves and their neighbours. This way the nodes can check channel availability.
    channels: Dict[Host, List[Message]] = {}

    node_channel_counter: Dict[Host, int] = {}
    node_info_dict: Dict[Host, Dict] = {}

    def __init__(self, nodes, timeout):
        self.nodes = nodes
        self.timeout = timeout

    def begin_loop(self):

        print("Starting simulator...")
        if len(self.nodes) <= 0:
            print('No nodes registered so simulating nothing')
            return
        # Register channel dictionaries and metric dictionaries
        for node in self.nodes:
            self.channels[node] = [] 
            self.node_info_dict[node] = {"failed to deliver": 0, "successfully delivered": 0}
        # Pass the channel dictionary to all nodes
        for node in self.nodes:
            node.set_channels(self.channels)

        # Main loop to let nodes do their thing
        while self.counter < self.timeout:
            # Progress bar
            if ((self.counter / self.timeout) * 100 - math.ceil((self.counter / self.timeout)) * 100) < 0.0001:
                print(f"progress: {format((self.counter / self.timeout) * 100, '.2f')}\r", end="")


            node: Host
            for node in self.nodes:
                node.evaluate_round(self.counter)

            # check if we can actually deliver messages
            for node in self.nodes:
                node_channel = self.channels[node]
                sorted(node_channel, key=lambda x: x.end_time)
                # only deliver the message once self.counter + 1 = end_time of the message for the node.
                message_to_deliver = [x for x in node_channel if x.end_time == self.counter + 1 and x.destination == node.mac]

                # We have multiple messages delivered at the same time, will be a collision
                if len(message_to_deliver) > 1:
                    self.node_info_dict[node]["failed to deliver"] = self.node_info_dict[node]["failed to deliver"] + len(message_to_deliver)
                    continue

                if len(message_to_deliver) == 1:
                    message_start_time = message_to_deliver[0].start_time
                    message_end_time = message_to_deliver[0].end_time

                    earlier_messages = [x for x in node_channel if x.end_time <= message_start_time]
                    if len(earlier_messages) > 0:
                        self.node_info_dict[node]["failed to deliver"] = self.node_info_dict[node]["failed to deliver"] + 1
                        continue

                    later_messages = [x for x in node_channel if x.start_time <= message_end_time]
                    if len(later_messages) > 0:
                        self.node_info_dict[node]["failed to deliver"] = self.node_info_dict[node]["failed to deliver"] + 1
                        continue

                    # We don't have later messages that will go before or us, or messages that were trying to be delivered during us.
                    # So we can now actually deliver the message.
                    node.message_queue.append(message_to_deliver[0])
                    self.node_info_dict[node]["successfully delivered"] = self.node_info_dict[node]["successfully delivered"] + 1

            self.counter = self.counter + 1
        print('Done simulating, ran for %d iterations' % self.counter)

    def print_results(self):
        for node, values in self.node_info_dict.items():
            print(f"Node {node.mac} has the following metrics: {str(values)}")
