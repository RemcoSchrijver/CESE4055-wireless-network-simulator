import sys
from typing import Dict, List

from assignment_2.host import Host
from assignment_2.message import Message

class simulator:

    counter: int = 0
    nodes: List[Host] = []
    timeout: int = sys.maxsize

    # This is an interesting one, this dictionary keeps track for all nodes if their sending channel is clear.
    # How it does this is done because every node that decides to transmit will add their transmission time window
    # to the dictionary of themselves and their neighbours. This way the nodes can check channel availability.
    channels: Dict[Host, List[Message]] = {}

    node_channel_counter: Dict[Host, int] = {}

    def __init__(self, nodes, timeout):
        self.nodes = nodes
        self.timeout = timeout

    def begin_loop(self):
        if len(self.nodes) > 0:
            print('No nodes registered so simulating nothing')
            return
        # Register channel dictionaries
        for node in self.nodes:
            self.channels[node] = []
        
        # Pass the channel dictionary to all nodes
        for node in self.nodes:
            node.set_channels(self.channels)

        # Main loop to let nodes do their thing
        while self.counter < self.timeout:
            node: Host
            for node in self.nodes:
                node.evaluate_round(self.counter)
            
            # Check if we can actually deliver messages
            for node in self.nodes:
                node_channel = self.channels[node]
                sorted(node_channel, key=lambda x: x.start_time)
                # trick here is I think we should keep track of what start time we evaluated, 
                # because we know for certain we cannot get new start time entries.

            self.counter = self.counter + 1
        print('Done simulating, ran for %d iterations' % self.counter)
