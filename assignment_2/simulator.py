import sys
from typing import List

from assignment_2.host import Host

class simulator:

    counter: int = 0
    nodes: List[Host] = []
    timeout: int = sys.maxsize

    # This is an interesting one, this dictionary keeps track for all nodes if their sending channel is clear.
    # How it does this is done because every node that decides to transmit will add their transmission time window
    # to the dictionary of themselves and their neighbours. This way the nodes can check channel availability.
    channels = {}

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
               # still requires implementation. 
               node_channel = self.channels[node]
            
            self.counter = self.counter + 1
        print('Done simulating, ran for %d iterations' % self.counter)
