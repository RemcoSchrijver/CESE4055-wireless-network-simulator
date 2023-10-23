from collections.abc import Sequence
import weakref
import math
import logging
from typing import Any, Callable, Dict, List
from message import Message


class Host:
    _instances = set()  # atribute protect to save all instances of host

    # message queue that the simulator can use to deposit messages into.
    message_queue: List[Message] 

    # Channel placeholder, will get registered by the simulator.
    channels = None

    # Algorithm used by to determine what to do with incoming messages and what to send.
    # Takes an incoming message if available, a list of neighbors that can be contacted. 
    # algorithm: Callable[[Message, List[Any], int], Message]
    algorithm = None

    # Metrics kept per host, can be customized if need be.
    metrics : Dict 

    # def __init__(self, mac: int, x: float, y: float, reach: float, algorithm: Callable[[Message, List[Any], int], Message]):	#default constructor
    def __init__(self, mac: int, x: float, y: float, reach: float, algorithm):  # default constructor
        self.reach = reach
        self.mac = mac
        self.positionx = x
        self.positiony = y
        self._instances.add(weakref.ref(self))
        self.algorithm = algorithm
        self.metrics = {"failed to deliver": 0, "successfully delivered": 0, "messages sent": 0}
        self.channels = {}
        self.message_queue = []

    @classmethod  # to list all instances of host class
    def get_instances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    # Evaluates a single round, checks if there is a message to handle else just go to the algorithm.
    # Maybe it might be nice to give the algorithm a sense of the counter but that can be added later.
    def evaluate_round(self, round_counter):
        incoming_message: Message = None

        if len(self.message_queue) > 0:
            incoming_message = self.message_queue.pop(0)

        return_message = self.algorithm.process_algorithm(self, round_counter, incoming_message)

        # If we have a message to send lets do that now.
        if return_message is not None:
            self.metrics["messages sent"] = self.metrics["messages sent"] + 1
            self.send_message(return_message)

        # Done with our round
        return

    def send_message(self, message: Message):
        neighbors = self.get_neighbors()

        self.channels[self].append(message)
        # Dumps the messages in the channel of the neighbors.
        for each in neighbors:
            self.channels[each].append(message)

    def is_reacheable(self, neighbor):  # check if neighbor host is reacheable
        first_part = ((self.positionx - neighbor.positionx) ** 2)
        second_part = ((self.positiony - neighbor.positiony) ** 2)
        distance = math.sqrt(first_part + second_part)

        if distance == 0:  # to not add itself on the neighbors list
            return distance
        else:
            return distance <= self.reach  # returns true if is reacheable

    def get_neighbors(self):  # get all neighbors of a host
        neighbors = []
        for obj in Host.get_instances():
            if (self.is_reacheable(obj)):  # check if a node is reacheable
                neighbors.append(obj)  # add to the list of neighbors
        return neighbors  # returns the list

    def get_mac(self):  # returns the mac address
        return self.mac

    def get_positionx(self):  # returns the first coordinate location
        return self.positionx

    def get_positiony(self):  # returns the second coordinate location
        return self.positiony

    def get_reach(self):  # returns the reach
        return self.reach

    def set_channels(self, channels):
        self.channels = channels

    def add_message_to_queue(self, message):
        self.message_queue.append(message)
