import math
import sys
import os
import shutil
from typing import Dict, List, TextIO

from network.host import Host
from network.message import Message

class simulator:

    counter: int = 0
    nodes: List[Host] = []
    timeout: int = sys.maxsize

    # This is an interesting one, this dictionary keeps track for all nodes if their sending channel is clear.
    # How it does this is done because every node that decides to transmit will add their transmission time window
    # to the dictionary of themselves and their neighbours. This way the nodes can check channel availability.
    channels: Dict[Host, List[Message]] = {}
    channel_files: Dict[Host, TextIO] = {}
    channel_cleaning_evaluation: Dict[Host, int] = {}

    node_channel_counter: Dict[Host, int] = {}
    node_info_dict: Dict[Host, Dict] = {}

    def __init__(self, nodes, timeout):
        self.nodes = nodes
        self.timeout = timeout

    def begin_loop(self):

        output_path = "output/"
        print("Cleaning run environment...")
        if os.path.exists(output_path) and os.path.isdir(output_path):
            shutil.rmtree(output_path)
        os.mkdir("output/")


        print("Starting simulator...")
        if len(self.nodes) <= 0:
            print('No nodes registered so simulating nothing')
            return

        # Register channel dictionaries and metric dictionaries
        for node in self.nodes:
            self.channels[node] = [] 
            # Pass the channel dictionary to all nodes
            node.set_channels(self.channels)

            self.channel_files[node] = open(f"{output_path}node_{node.mac}", 'w')
            self.channel_cleaning_evaluation[node] = 0

        while self.counter < self.timeout:
            # Progress bar
            simulator.print_progress_bar(self.counter, self.timeout)


            # Main loop to let nodes do their thing
            node: Host
            for node in self.nodes:
                node.evaluate_round(self.counter)

            # check if we can actually deliver messages
            for node in self.nodes:
                node_channel = self.channels[node]
                # only deliver the message once self.counter + 1 = end_time of the message for the node.
                message_to_deliver = [x for x in node_channel if x.end_time == self.counter + 1 and (x.destination == node.mac or x.destination == -1)]

                # We have multiple messages delivered at the same time, will be a collision
                if len(message_to_deliver) > 1:
                    node.metrics["failed to deliver"] = node.metrics["failed to deliver"] + len(message_to_deliver)
                    continue

                # No need evaulating if there are no messages to deliver
                if len(message_to_deliver) == 1:
                    blocking_messages = simulator.find_conflicting_messages(message_to_deliver[0], node_channel)
                    if len(blocking_messages) > 0: 
                        node.metrics["failed to deliver"] = node.metrics["failed to deliver"] + 1
                        continue
                    else: 
                        node.message_queue.append(message_to_deliver[0])
                        node.metrics["successfully delivered"] = node.metrics["successfully delivered"] + 1

                # We are done evaluating, time to look at cleaning the channel.
                self.clean_channels(node)

            self.counter = self.counter + 1

        print('Done simulating, ran for %d iterations' % self.counter)
        return

    def print_results(self):
        """Method that prints results of the simulator

        Goes and fetches the metric dictionaries from all nodes and prints them out.
        """
        if len(self.nodes) > 0:
            node : Host
            for node in self.nodes:
                print(f"Node {node.mac} has the following metrics: {str(node.metrics)}")
    
    @staticmethod
    def find_conflicting_messages(message: Message, message_channel: List[Message]) -> List[Message]:
        """Find all messages conflicting with this message
        
        Returns the list of messages that conflict with this message, as in the end time is later then the start time of this message
        as well as the start time being before the end time of this message.
        """
        return  [x for x in message_channel if (x.end_time >= message.start_time and x.start_time <= message.end_time and x != message)]
    
    @staticmethod
    def print_progress_bar(counter: int, timeout: int):
        if ((counter / timeout) * 100 - math.ceil((counter / timeout)) * 100) < 0.0001:
            print(f"Progress: {format((counter / timeout) * 100, '.2f')}%\r", end="")


    def clean_channels(self, node: Host):
        """Intricate method for doing bookkeeping on the node channels, keeping calculation of conflicts relatively cheap.

        This method works by evaluating the first message, which has the first start time, (getting the one with the earliest end time would be more
        optimal but requires more computation) and an endtime. To determine if we can safely write this message to our permanent storage and drop it
        from memory we have to determine if we already evaluated all the messages that this one can be conflicting with.

        If we determine that indeed this can be removed because we evaluated all conflicting later messages we drop this one and write it to a file.
        Then we make a recursive call and try again with the next message in line.

        Now what if we can't delete this yet, then we are smart and write the time that message end to our dictionary, so we'll only start to evaluate if 
        we can clean this channel when that time has passed. This reduces the amount of unneeded computation greatly.
        """
        node_channel = self.channels[node]

        if self.channel_cleaning_evaluation[node] >= self.counter or len(node_channel) == 0:
            return

        first_message = node_channel[0]

        # If we are not done yet ourself don't remove
        if first_message.end_time >= self.counter:
            self.channel_cleaning_evaluation[node] = first_message.end_time
            return

        conflicting_messages = simulator.find_conflicting_messages(first_message, node_channel)

        # Checking if all messages are already evaluated, as in are there endtimes after the current time
        safe_to_delete = True 
        message : Message
        for message in conflicting_messages:
            if (message.end_time >= self.counter):
                safe_to_delete = False
                # Small trick here to optimize when we run this expensive operation next, we will only come back when we can actually make a change.
                self.channel_cleaning_evaluation[node] = message.end_time
                break

        if safe_to_delete:
            self.channel_files[node].write(f"{str(first_message)} deleted at: {self.counter} \n")
            node_channel.pop(0)
            self.clean_channels(node)


