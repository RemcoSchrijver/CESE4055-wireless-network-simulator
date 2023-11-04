import math
import sys
from time import sleep
from typing import Dict, List, TextIO

from host import Host
from message import Message

class simulator:

    counter: int = 0
    nodes: List[Host] = []
    timeout: int = sys.maxsize

    def __init__(self, nodes, timeout, tkinter_window, canvas, node_dict):
        self.nodes = nodes
        self.timeout = timeout
        self.tkinter_window = tkinter_window
        self.canvas = canvas
        self.node_dict = node_dict

    def begin_loop(self):
        

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

            # Main loop for letting the nodes move around
            for node in self.nodes:
                node.evaluate_moving()
                self.canvas.move(self.node_dict[node], node.dx, node.dy)

            
            self.tkinter_window.update_idletasks()
            self.tkinter_window.update()
            

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

