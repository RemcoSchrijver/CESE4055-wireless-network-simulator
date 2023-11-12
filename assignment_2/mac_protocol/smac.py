import random
from enum import Enum, auto

from network.host import Host
from network.message import Message

# Random WAIT constants (gaussian)
MEAN_WAIT = 30
STD_WAIT = 10

# SYNC init bounds (min/max uniform)
SYNC_MIN_INIT_WAIT = 100
SYNC_MAX_INIT_WAIT = 1000

# SYNC schedule bounds (min/max uniform)
SYNC_MIN_SLEEP_WAIT = 50
SYNC_MAX_SLEEP_WAIT = 250
SYNC_MIN_SLEEP_PERIOD = 1000
SYNC_MAX_SLEEP_PERIOD = 2000
SYNC_MIN_LISTEN_PERIOD = 200
SYNC_MAX_LISTEN_PERIOD = 400

NEW_MESSAGE_RATIO = 50

class State(Enum):
    INIT = auto()
    SYNC_INIT = auto()
    SYNC_SCHEDULE = auto()
    SLEEP = auto()
    LISTEN = auto()


class MessageType(Enum):
    SYNC = auto()
    RTS = auto()
    CTS = auto()
    DATA = auto()
    ACK = auto()

class NodeType(Enum):
    FOLLOWER = auto()
    SYNCHRONIZER = auto()

class SMAC:

    def __init__(self):
        self.state = State.INIT
        self.node_type = NodeType.FOLLOWER
        self.next_available_round = 1

        # Counters for alternating sleep/listen cycle
        self.next_listen_period = None
        self.next_sleep_period = None

        # SYNC schedules of neighbouring nodes
        self.schedule_table = dict()

        # SYNC schedule
        self.sync_init_wait = None

        self.message_durations = {
            MessageType.SYNC: 15,
            MessageType.RTS: 1,
            MessageType.CTS: 1,
            MessageType.DATA: 30,
            MessageType.ACK: 1
        }


    def process_algorithm(self, node: Host, round_counter, incoming_message):
        message = None
        received_message = None

        if incoming_message:
            received_message = incoming_message.message.split()

        if self.check_for_sync_schedules(received_message, node, round_counter, incoming_message):
            return message

        if self.state == State.INIT:
            node.plot_schedule.append(0)
            # Wait for other SYNC messages
            self.sync_init_wait = round_counter + random.randint(SYNC_MIN_INIT_WAIT, SYNC_MAX_INIT_WAIT)
            self.state = State.SYNC_INIT
            return message

        elif self.state == State.SYNC_INIT:
            node.plot_schedule.append(1)
            # No SYNC from other nodes, create a schedule
            if round_counter >= self.sync_init_wait:
                self.sync_init_wait = None

                # Create schedule
                sleep_period = random.randint(SYNC_MIN_SLEEP_PERIOD, SYNC_MAX_SLEEP_PERIOD)
                listen_period = random.randint(SYNC_MIN_LISTEN_PERIOD, SYNC_MAX_LISTEN_PERIOD)
                sleep_wait = round_counter + random.randint(SYNC_MIN_SLEEP_WAIT, SYNC_MAX_SLEEP_WAIT)

                # Create and broadcast schedule
                schedule = f"{sleep_period} {listen_period} {sleep_wait}"
                message = self.send_message(node, round_counter, MessageType.SYNC, schedule)

                # Update own state
                self.state = State.SYNC_SCHEDULE
                self.node_type = NodeType.SYNCHRONIZER

                schedule = {'sleep_period': sleep_period, 'listen_period': listen_period,
                                'sync_sleep_wait': sleep_wait, 'next_listen_period': sleep_wait+sleep_period, 'next_sleep_period': sleep_wait+sleep_period+listen_period}

                self.schedule_table[node.mac] = schedule

                print(message)
                return message


        elif self.state == State.SYNC_SCHEDULE:
            node.plot_schedule.append(2)
            merged_start_time = -1

            for key, schedule in self.schedule_table.items():
                if merged_start_time == -1:
                    merged_start_time = schedule['sync_sleep_wait']

                elif schedule['sync_sleep_wait'] < merged_start_time:
                    merged_start_time = schedule['sync_sleep_wait']

            if round_counter >= merged_start_time:
                self.state = State.SLEEP

            return message

        elif self.state == State.SLEEP:
            node.plot_schedule.append(3)
            for key, schedule in self.schedule_table.items():
                if round_counter >= schedule['next_listen_period']:
                    self.schedule_table[key]['next_sleep_period'] = round_counter + schedule['listen_period']
                    self.state = State.LISTEN

            return message

        elif self.state == State.LISTEN:
            node.plot_schedule.append(4)
            active_node = False

            for key, schedule in self.schedule_table.items():
                if round_counter > schedule['next_sleep_period']:
                    if schedule['next_listen_period'] >= schedule['next_sleep_period']:
                        continue
                    self.schedule_table[key]['next_listen_period'] = round_counter + schedule['sleep_period']
                else:
                    active_node = True

            if not active_node:
                self.state = State.SLEEP

            # Generate new message by sending a RTS packet if we have nothing to do
            if not incoming_message:
                random_message_event = random.randint(0, NEW_MESSAGE_RATIO)
                if random_message_event == 0:
                    message = self.send_message(node, round_counter, MessageType.RTS, "", destination_mac=None)
                    return message

            # Check for RTS packet
            if incoming_message:
                if received_message[0] == "RTS":
                    message = self.send_message(node, round_counter, MessageType.CTS, "", destination_mac=incoming_message.source)
                    return message

            # Check for CTS packet
            if incoming_message:
                if received_message[0] == "CTS":
                    message = self.send_message(node, round_counter, MessageType.DATA, "RANDOM BINARY DATA", destination_mac=incoming_message.source)
                    return message

            # Check for DATA packet
            if incoming_message:
                if received_message[0] == "DATA":
                    message = self.send_message(node, round_counter, MessageType.ACK, "", destination_mac=incoming_message.source)
                    return message

            return message
        else:
            print("Unknown state")

        return message

    def send_message(self, node: Host, round_counter: int,  message_type: MessageType, payload: str, destination_mac=None):
        message = None
        neighbors = node.get_neighbors()

        if self.next_available_round < round_counter:
            self.next_available_round = round_counter

        # Simulate random processing time
        random_wait = self.get_random_wait()
        start_time = random.randint(self.next_available_round, self.next_available_round + random_wait)

        # Add transmission time of the message
        end_time = start_time + self.message_durations[message_type]

        if message_type == MessageType.SYNC:
            # Broadcast SYNC to all neighbours
            if len(neighbors) > 0:
                message = Message(node.mac, -1, start_time, end_time, f"{message_type.name} {payload}")
        elif message_type == MessageType.RTS:
            if round_counter >= self.next_available_round:
                if len(neighbors) > 0:
                    random_neighbour = random.randint(0, len(neighbors) - 1)
                    destination = neighbors[random_neighbour].mac
                    message = Message(node.mac, destination, start_time, end_time, f"{message_type.name} {payload}")
        elif message_type == MessageType.CTS:
            if round_counter >= self.next_available_round:
                message = Message(node.mac, destination_mac, start_time, end_time, f"{message_type.name} {payload}")
        elif message_type == MessageType.DATA:
            if round_counter >= self.next_available_round:
                message = Message(node.mac, destination_mac, start_time, end_time, f"{message_type.name} {payload}")
        elif message_type == MessageType.ACK:
            if round_counter >= self.next_available_round:
                message = Message(node.mac, destination_mac, start_time, end_time, f"{message_type.name} {payload}")

        # Set next available round to the endtime of the current transmission
        self.next_available_round = end_time

        return message

    @staticmethod
    def get_random_wait():
        return round(random.gauss(MEAN_WAIT, STD_WAIT))

    def check_for_sync_schedules(self, received_message, node, round_counter, incoming_message):
        if incoming_message:
            if received_message[0] == "SYNC":
                sleep_period = int(received_message[1])
                listen_period = int(received_message[2])
                sync_sleep_wait = int(received_message[3])

                if round_counter <= sync_sleep_wait:

                        if self.state == State.SYNC_INIT:
                            self.state = State.SYNC_SCHEDULE

                        self.node_type = NodeType.FOLLOWER

                        schedule = {'sleep_period': sleep_period, 'listen_period': listen_period,
                                    'sync_sleep_wait': sync_sleep_wait, 'next_listen_period': sync_sleep_wait + sleep_period,
                                    'next_sleep_period': sync_sleep_wait + sleep_period + listen_period}

                        self.schedule_table[incoming_message.source] = schedule

                        if len(self.schedule_table) > 1:
                            print(f"Schedules merged for node {node.mac}")

                        return True
        return False

