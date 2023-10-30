import math
import sys
import os
import shutil
from typing import Dict, List, TextIO

from host import Host
from message import Message

class simulator:

    counter: int = 0
    nodes: List[Host] = []
    timeout: int = sys.maxsize

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

        while self.counter < self.timeout:
            # Progress bar
            simulator.print_progress_bar(self.counter, self.timeout)


            # Main loop to let nodes do their thing
            node: Host
            for node in self.nodes:
                node.evaluate_round(self.counter)
            
            # All messages have been sent out now it's time to let the nodes move.
            for node in self.nodes:
                node.decide_to_move(self.counter)

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
    def print_progress_bar(counter: int, timeout: int):
        if ((counter / timeout) * 100 - math.ceil((counter / timeout)) * 100) < 0.0001:
            print(f"Progress: {format((counter / timeout) * 100, '.2f')}%\r", end="")


