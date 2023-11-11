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

        self.message_out_for_delivery: Message = None 
        self.message_out_queue = []
        self.message_lines = None

        # DSR
        self.passed_ids = []
        self.known_routes = []

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
    def evaluate_round(self, round_counter, canvas, message_id):
        
        # Evaluate our incoming messages
        messages_to_forward = []
        while len(self.message_queue) > 0:
            message: Message
            message = self.message_queue.pop()

            # So if the message is not a re-request and it reaches its destinations it will send a ReRequest message
            # back to its source
            if message.type != "ReRequest" and message.end_destination() == self and message_id not in self.passed_ids:
                self.metrics["messages received"] += 1
                self.incorporate_ttl(message)

                self.passed_ids.append(message_id)

                request_route = message.route
                next_hop = message.route.pop()
                start_time = round_counter
                end_time = start_time + 2
                new_message = Message(self, next_hop, message.source, start_time, end_time, "rerequest",
                                      message_id, message.route, request_route,  "ReRequest")
                self.message_out_queue.append(new_message)

            elif message.type == "ReRequest" and len(message.route) > 0:
                if message.end_destination == self:
                    if not any(message.source == sublist[0] for sublist in self.known_routes):
                        self.known_routes.append([message.source, message.request_route])
                else:
                    next_hop = message.route.pop()
                    start_time = round_counter
                    end_time = start_time + 2
                    new_message = Message(self, next_hop, message.source, start_time, end_time, "rerequest"
                                          , message_id, message.route, message.request_route, "ReRequest")
                    self.message_out_queue.append(new_message)

            if len(message.route) == 0:
                # Link broken???
                continue

            # if message.end_destination() == self: # this is a weakref, make it a strongref by using a method call.
            #     self.metrics["messages received"] += 1
            #     self.incorporate_ttl(message)

            else:
                if message.ttl == 0:
                    self.metrics["messages stranded"] += 1
                else:
                    self.metrics["forward-messages received"] += 1
                    messages_to_forward.append(message)

        # Roll a dice to send a message
        return_message = None 
        if self.timestamp_until_sending < round_counter:
            return_message, message_id = self.decide_to_send_message(round_counter, message_id)

        # If we have a message to send thats not already out for delivery do that now.
        if return_message is not None and return_message.end_destination is not None:
            # Routing algorithm basically only has to set the current destination(s), for broadcast just use all the current
            # neighbors.

            self.message_out_queue.append(return_message)

        # We also have messages to forward so let's try to deliver those as well.
        while len(messages_to_forward) > 0:
            # Routing for forwarding is also necessary.
            message_to_forward: Message
            message_to_forward = messages_to_forward.pop()

            # Edit the message timings
            message_to_forward.end_time = round_counter + (message_to_forward.end_time - message_to_forward.start_time)
            message_to_forward.start_time = round_counter
            # Decrease TTL
            message_to_forward.ttl -= 1
            message_to_forward.route.append(self)

            self.message_out_queue.append(message_to_forward)

        # Try do deliver our messages that are out for delivery, we basically check if our destinations are still in reach.
        self.try_to_deliver_messages(round_counter, canvas)

        # Done with our round except for moving, we do that later to make sure everyone is working with the same positions.
        return message_id


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
    def try_to_deliver_messages(self, round_counter, canvas):
        if len(self.message_out_queue) > 0 and self.message_out_for_delivery is None:
            neighbors_in_reach = self.get_neighbors()
            self.message_out_for_delivery = self.message_out_queue.pop() 
            self.message_out_for_delivery.end_time = round_counter + self.message_out_for_delivery.end_time - self.message_out_for_delivery.start_time
            self.message_out_for_delivery.start_time = round_counter
            self.message_out_for_delivery = self.routing_algorithm(neighbors_in_reach, self.message_out_for_delivery)

        if self.message_out_for_delivery is not None:
            neighbors_in_reach = self.get_neighbors()
            message : Message

            message = self.message_out_for_delivery
            # There are messages to try to deliver
            if len(message.destination) > 0:
                dest : Host
                for dest in message.destination:

                    # Our dest is no longer in reach, remove it from our message destination cause it failed.
                    if dest in neighbors_in_reach == False:
                        message.destination.remove(dest)
                        self.delete_line(canvas, message, dest)
                        if len(message.destination) < 1:

                            # We failed delivery completely, time to do book keeping.
                            metrics_string = "forward-messages failed"
                            if message.source == self:
                                metrics_string = "messages failed"
                            self.metrics[metrics_string] += 1
                        continue

                    else: 
                        # We succeeded in delivering/forwarding our message, do book keeping.
                        if round_counter > message.end_time:
                            dest.message_queue.append(message)
                            message.destination.remove(dest)

                            metrics_string = "forward-messages sent"
                            if message.source == self:
                                metrics_string = "messages sent"
                            self.metrics[metrics_string] += 1
                            self.delete_line(canvas)

                        # We are still in reach and can keep delivering.
                        else:
                            self.draw_line(canvas, message, dest)
                        continue
                            
                        
            else:
                if(message.end_time > round_counter):
                    # We failed delivery completely, time to do book keeping.
                    metrics_string = "forward-messages failed"
                    if message.source == self:
                        metrics_string = "messages failed"
                    self.metrics[metrics_string] += 1
                
                self.delete_line(canvas)
                self.message_out_for_delivery = None 


                
    def draw_line(self, canvas, message: Message, destination):
            self.delete_line(canvas)
            self.message_lines = canvas.create_line(self.positionx, self.positiony, destination.positionx, destination.positiony, fill='green', width=3)
            

    def delete_line(self, canvas):
            canvas.delete(self.message_lines)


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
    def decide_to_send_message(self, round_counter, message_id):
        if self.message_chance > random.random():
            end_destination = random.choice(list(self._instances))
            if end_destination() != self:
                end_time = round_counter + random.randint(10, 15)
                self.timestamp_until_sending = end_time
                message_id += 1
                return Message(self, None, end_destination, round_counter, end_time,
                               "random message", message_id, [self], None, "Packet Discovery"), message_id

        return None, message_id


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
