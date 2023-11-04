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
                "messages failed": 0,
                "forward-messages received": 0,
                "forward-messages sent": 0,
                "forward-messages failed": 0,
                "average ttl": 0,
                "highest ttl": 0,
                "lowest ttl": 0,
                "messages stranded": 0,
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

        self.messages_out_for_delivery = []

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
    def evaluate_round(self, round_counter):
        
        # Evaluate our incoming messages
        messages_to_forward = []
        while len(self.message_queue) > 0:
            message = self.message_queue.pop()

            if message.end_destination == self:
                self.metrics["messages received"] =+ 1
                self.incorporate_ttl(message) 
            else:
                if message.ttl == 0:
                    self.metrics["messages stranded"] += 1
                else:
                    self.metrics["forward-messages received"] =+ 1
                    messages_to_forward.append(message)

        # Roll a dice to send a message
        return_message = None 
        if self.timestamp_until_sending < round_counter:
            return_message = self.decide_to_send_message(round_counter)

        return_message = self.decide_to_send_message(round_counter)
        # If we have a message to send thats not already out for delivery do that now.
        if return_message is not None and return_message.destination is not None:
            # Routing algorithm basically only has to set the current destination(s), for broadcast just use all the current
            # neighbors.
            return_message = self.routing_algorithm(self.get_neighbors(), return_message)
            # Decrease TTL
            return_message.ttl = return_message.ttl - 1

            self.messages_out_for_delivery.append(return_message)

        # We also have messages to forward so let's try to deliver those as well.
        while len(messages_to_forward) > 0:
            # Routing for forwarding is also necessary.
            message_to_forward = messages_to_forward.pop()
            message_to_forward = self.routing_algorithm(self.get_neighbors(), message_to_forward)
            # Decrease TTL
            message_to_forward = message_to_forward - 1

            self.messages_out_for_delivery.append(message_to_forward)

        # Try do deliver our messages that are out for delivery, we basically check if our destinations are still in reach.
        self.try_to_deliver_messages(round_counter)

        # Done with our round except for moving, we do that later to make sure everyone is working with the same positions.
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


    # We keep track of our neighbors and try to deliver our message, if the destination nodes are out of our
    # range this is no longer a target, if we lose all targets sending the message failed.
    def try_to_deliver_messages(self, round_counter):
        if len(self.messages_out_for_delivery) > 0:
            neighbors_in_reach = self.get_neighbors()
            message : Message

            for message in self.messages_out_for_delivery:
                # There are messages to try to deliver
                if len(message.destination) > 0:
                    dest : Host
                    for dest in message.destination:

                        # Our dest is no longer in reach, remove it from our message destination cause it failed.
                        if neighbors_in_reach.__contains__(dest) == False:
                            message.destination.remove(dest)
                            if len(message.destination) < 1:

                                # We failed delivery completely, time to do book keeping.
                                metrics_string = "forward-messages failed"
                                if message.source == self:
                                    metrics_string = "messages failed"
                                self.metrics[metrics_string] =+ 1
                            continue

                        else: 
                            if round_counter > message.end_time:
                                dest.message_queue.append(message)
                                message.destination.remove(dest)

                                # We succeeded in delivering/forwarding our message, do book keeping.
                                metrics_string = "forward-messages sent"
                                if message.source == self:
                                    metrics_string = "messages sent"
                                self.metrics[metrics_string] =+ 1
                            continue
                            
                else:
                    self.messages_out_for_delivery.remove(message)
                


    # Incorporate TTL for a message successfully received we are going to store the metrics.
    def incorporate_ttl(self, message: Message):

        ttl = Message.default_ttl - message.ttl

        average = self.metrics["average ttl"]
        received_messages_count = self.metrics["messages received"]
        highest = self.metrics["highest ttl"]
        lowest = self.metrics["lowest ttl"]

        self.metrics["average ttl"] = ((average * (received_messages_count - 1)) + ttl) / received_messages_count
        if highest < ttl:
            self.metrics["highest ttl"] = ttl
        if lowest > ttl:
            self.metrics["lowest ttl"] = ttl

        return

    
    # Decide randomly if you will send a message
    def decide_to_send_message(self, round_counter):
        if self.message_chance > random.random():
            end_destination = random.choice(list(self._instances))
            if end_destination != self:
                return Message(self, None, end_destination, round_counter, round_counter + random.randint(10, 150), "random message")
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
