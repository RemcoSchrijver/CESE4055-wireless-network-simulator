from collections.abc import Sequence
import weakref
import math
import random
from typing import Any, Callable, Dict, List
from message import Message


class Host:
    _instances = set()  # atribute protect to save all instances of host

    # message queue that the simulator can use to deposit messages into.
    message_queue: List[Message] 


    # Metrics kept per host, can be customized if need be.
    metrics: Dict

    # def __init__(self, mac: int, x: float, y: float, reach: float, algorithm: Callable[[Message, List[Any], int], Message]):	#default constructor
    def __init__(self, mac: int, x: float, y: float, reach: float, routing_algorithm, movement_frequency : float, message_chance : float):  # default constructor
        self.reach = reach
        self.mac = mac
        self.positionx = x
        self.positiony = y
        self._instances.add(weakref.ref(self))
        self.routing_algorithm = routing_algorithm
        self.metrics = {
                "messages received": 0,
                "messages sent": 0,
                "forward-messages received": 0,
                "messages forwarded": 0,
                "average ttl": 0,
                "highest ttl": 0,
                "lowest ttl": 0,
            }
        self.message_queue = []
        self.movement_frequency = movement_frequency
        self.message_chance = message_chance

        self.timestamp_until_sending = 0

        # Movement related variables
        self.move_turns_remaining = 0
        self.dx = 0
        self.dy = 0

        self.max_y = 500
        self.max_x = 500
        self.min_y = 0
        self.min_x = 0
        self.max_move = 50


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
        
        messages_to_forward = []
        while len(self.message_queue) > 0:
            message = self.message_queue.pop()
            if message.end_destination == self:
                self.metrics["messages received"] = self.metrics["messages received"] + 1
            else:
                messages_to_forward.append(message)


        return_message = self.decide_to_send_message(round_counter)

        # If we have a message to send lets do that now.
        if return_message is not None:
            self.send_message(return_message)

        # Done with our round
        return


    # Here we either continue moving or calculate a new move.
    def evaluate_moving(self):
        if self.move_turns_remaining < 1:
            if self.movement_frequency > random.random():
                self.pick_next_move()
        else:
            self.positiony += self.dy
            self.positionx += self.dx
            self.move_turns_remaining -= 1



    def pick_next_move(self):
        
        y_upper = math.ceil(min(self.positiony + self.max_move/2, self.max_y))
        y_lower = math.floor(max(self.positiony - self.max_move/2, self.min_y))

        x_upper = math.ceil(min(self.positionx + self.max_move/2, self.max_x))
        x_lower = math.floor(max(self.positionx - self.max_move/2, self.min_x))

        new_y = random.randint(y_lower, y_upper)
        new_x = random.randint(x_lower, x_upper)
        speed_in_turns = random.randint(500, 2000)
        
        self.move_turns_remaining = speed_in_turns
        
        self.dy = (new_y - self.positiony)/speed_in_turns
        self.dx = (new_x - self.positionx)/speed_in_turns

        return


    def send_message(self, message: Message):
        neighbors = self.get_neighbors()

        self.channels[self].append(message)
        # Dumps the messages in the channel of the neighbors.
        for each in neighbors:
            self.channels[each].append(message)
    
    def decide_to_send_message(self, round_counter):
        if self.message_chance > random.random():
            end_destination = random.choice(list(self._instances))
            if end_destination != self:
                return Message(self, None, end_destination, round_counter, round_counter + random.randint(10, 150), "random message", 64)
        return None


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
